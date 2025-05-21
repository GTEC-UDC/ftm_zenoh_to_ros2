from setuptools import find_packages, setup

package_name = 'ftm_zenoh_to_ros2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Valentin Barral',
    maintainer_email='valentin.barral@udc.es',
    description='Bridge between Zenoh and ROS2 for FTM',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ftm_zenoh_to_ros2 = ftm_zenoh_to_ros2.ftm_zenoh_to_ros2:main',
        ],
    },
)
