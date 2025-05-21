import rclpy
from rclpy.node import Node
from gtec_msgs.msg import ESP32S2FTMRangingExtra, ESP32S2FTMFrame
from zenoh import Config, open
from threading import Thread
import time
import base64
import json

class FtmZenohToROS2Bridge(Node):
    def __init__(self, zenoh_key="ftm", ros2_topic="ftm_ros2"):
        super().__init__('ftm_zenoh_to_ros2_bridge')
        self.declare_parameter("ros2_topic", ros2_topic)
        self.declare_parameter("zenoh_key", zenoh_key)
        self.ros2_topic = self.get_parameter("ros2_topic").get_parameter_value().string_value
        self.zenoh_key = self.get_parameter("zenoh_key").get_parameter_value().string_value

        self.publisher = self.create_publisher(ESP32S2FTMRangingExtra, self.ros2_topic, 10)
        self.get_logger().info(f"Zenoh to ROS2 bridge initialized: Zenoh key = {self.zenoh_key}, ROS2 topic = {self.ros2_topic}")

        # Iniciar Zenoh en un hilo aparte
        self.thread = Thread(target=self.zenoh_listen, daemon=True)
        self.thread.start()

    def zenoh_listen(self):
        session = open(Config())
        session.declare_subscriber(
            self.zenoh_key,
            self.zenoh_callback
        )
        try:
            while rclpy.ok():
                time.sleep(0.1)
        finally:
            session.close()

    def zenoh_callback(self, sample):
        ros_msg = ESP32S2FTMRangingExtra()  # Create an instance of the custom message
        decoded_json_data = None # Initialize to None

        try:
            # Obtener los bytes reales del payload
            if hasattr(sample.payload, 'to_bytes'):
                raw_bytes = sample.payload.to_bytes()
            elif isinstance(sample.payload, (bytes, bytearray)):
                raw_bytes = sample.payload
            else:
                raw_bytes = bytes(sample.payload)

            # 1. Intentar decodificar como base64+JSON
            try:
                decoded_bytes = base64.b64decode(raw_bytes)
                decoded_json_data = json.loads(decoded_bytes.decode('utf-8'))
                self.get_logger().info(f"Received from Zenoh (base64+JSON decoded)")
            except Exception:
                # 2. Si falla, intentar como JSON directo
                try:
                    raw_str = raw_bytes.decode('utf-8')
                    decoded_json_data = json.loads(raw_str)
                except Exception:
                    # 3. Si todo falla, mostrar como string plano
                    if hasattr(sample.payload, 'to_string'):
                        raw_data = sample.payload.to_string()
                    else:
                        raw_data = str(sample.payload)
                    self.get_logger().error(f"Error decoding Zenoh message: Not base64 nor JSON. Raw: {raw_data}")
                    # If it's not JSON, we cannot populate the custom message, so we return or handle error
                    return

            if decoded_json_data:
                ros_msg.anchor_id = decoded_json_data.get("anchor_id", "")
                ros_msg.rtt_est = decoded_json_data.get("rtt_est", 0)
                ros_msg.rtt_raw = decoded_json_data.get("rtt_raw", 0)
                ros_msg.dist_est = float(decoded_json_data.get("dist_est", 0.0))
                ros_msg.own_est = float(decoded_json_data.get("own_est", 0.0))
                ros_msg.num_frames = decoded_json_data.get("num_frames", 0)

                frames_data = decoded_json_data.get("frames", [])
                for frame_item_data in frames_data:
                    frame_msg = ESP32S2FTMFrame()
                    frame_msg.rssi = frame_item_data.get("rssi", 0)
                    frame_msg.rtt = frame_item_data.get("rtt", 0)
                    frame_msg.t1 = frame_item_data.get("t1", 0)
                    frame_msg.t2 = frame_item_data.get("t2", 0)
                    frame_msg.t3 = frame_item_data.get("t3", 0)
                    frame_msg.t4 = frame_item_data.get("t4", 0)
                    ros_msg.frames.append(frame_msg)
                
                self.get_logger().info(f"Publishing: anchor_id={ros_msg.anchor_id}, dist_est={ros_msg.dist_est}")
                self.publisher.publish(ros_msg)
            else:
                # This case should ideally be caught by the return above if decoding completely fails
                self.get_logger().warn("Decoded JSON data is None, skipping publish.")

        except Exception as e:
            self.get_logger().error(f"Unexpected error processing Zenoh message: {e}. Raw payload: {sample.payload}")

def main(args=None):
    rclpy.init(args=args)
    node = FtmZenohToROS2Bridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
