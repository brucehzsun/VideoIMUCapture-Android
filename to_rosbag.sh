#!/usr/bin/env zsh

export PYTHONPATH="$(pwd)/proto_python/protobuf:${PYTHONPATH}"
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
source /opt/ros/noetic/setup.zsh

python data2rosbag.py /home/bruce/slam/dataset/slam_data_cap_01 \
--calibration /home/bruce/slam/dataset/kalibr-camchain-imucam.yaml \
--raw-image