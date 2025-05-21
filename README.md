# FTM Zenoh to ROS 2 Node

This ROS 2 node subscribes to FTM (Fine Time Measurement) data published over Zenoh and republishes it as ROS 2 messages.
It is specifically designed to work with FTM data published by the [GTEC-UDC/esp32s2-ftm-tag](https://github.com/GTEC-UDC/esp32s2-ftm-tag) project.

## Dependencies

This node depends on custom ROS 2 message types for FTM data. These messages can be found in the following repository:
[@GTEC-UDC/rosmsgs](https://github.com/GTEC-UDC/rosmsgs)

Please ensure you have built and sourced this messages package in your ROS 2 workspace.

### Python Dependencies

This project uses `eclipse-zenoh` for communication. You can install it and other potential Python dependencies using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## How to Launch

To launch the node, execute the main Python script:

```bash
ros2 run ftm_zenoh_to_ros2 ftm_zenoh_to_ros2
```

### Parameters

The node accepts the following ROS 2 parameters, which can be set during launch:

*   `zenoh_key` (string, default: "ftm")
    *   The Zenoh key expression to subscribe to for incoming FTM data.
*   `ros2_topic` (string, default: "ftm_ros2")
    *   The name of the ROS 2 topic where the FTM data will be published.

Example of launching with custom parameters:

```bash
ros2 run ftm_zenoh_to_ros2 ftm_zenoh_to_ros2 --ros-args -p zenoh_key:="custom/ftm/topic" -p ros2_topic:="my_ftm_data"
```


