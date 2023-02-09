#!/usr/bin/env zsh

export PYTHONPATH="$(pwd)/proto_python/protobuf:${PYTHONPATH}"
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
source /opt/ros/noetic/setup.zsh

python3 calibration/data2lth_vision.py /home/bruce/slam/dataset/slam_data_cap_01