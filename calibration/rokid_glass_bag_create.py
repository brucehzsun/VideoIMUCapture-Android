# import rosbag
import rosbag
import rospy
from sensor_msgs.msg import Image
from sensor_msgs.msg import Imu
# from geometry_msgs.msg import PointStamped
# import ImageFile
# import PIL.ImageFile as ImageFile
import time, sys, os
import argparse
import cv2
import numpy as np
import csv


# structure
# dataset/cam0/data/TIMESTAMP.png
# dataset/camN/data/TIMESTAMP.png
# dataset/imu0/data.csv
# dataset/imuN/data.csv
# dataset/leica0/data.csv

def getImageFilesFromDir(data_path: str):
    '''Generates a list of files from the directory'''
    root_dir = os.path.join(data_path, "mav0", "cam0")
    image_dir = os.path.join(root_dir, "data")
    csv_file = os.path.join(root_dir, "data.csv")

    image_files = list()
    timestamps = list()
    if os.path.exists(image_dir):
        for file in os.listdir(image_dir):
            if os.path.splitext(file)[1] in ['.bmp', '.png', '.jpg']:
                image_files.append(os.path.join(image_dir,file))
                timestamps.append(os.path.splitext(file)[0])
            # for f in files:
            #     if os.path.splitext(f)[1] in ['.bmp', '.png', '.jpg']:
            #         image_files.append(os.path.join(path, f))
        print(f"file={image_files[0]}")
    else:
        print(f"image path not exist,path = {image_dir}")
        exit(-1)

    # sort by timestamp
    sort_list = sorted(zip(timestamps, image_files))
    image_files = [file[1] for file in sort_list]
    timestamps = [file[0] for file in sort_list]
    print(f"timestamps[0]={timestamps[0]}")
    print(f"image_files[0]={image_files[0]}")
    return timestamps, image_files


def loadImageToRosMsg(filename: str):
    image_np = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    timestamp_nsecs = os.path.splitext(os.path.basename(filename))[0]
    timestamp = rospy.Time(secs=int(timestamp_nsecs[0:-9]), nsecs=int(timestamp_nsecs[-9:]))

    rosimage = Image()
    rosimage.header.stamp = timestamp
    rosimage.height = image_np.shape[0]
    rosimage.width = image_np.shape[1]
    rosimage.step = rosimage.width  # only with mono8! (step = width * byteperpixel * numChannels)
    rosimage.encoding = "mono8"
    rosimage.data = image_np.tostring()

    return rosimage, timestamp


def createImuMessge(timestamp_int, omega, alpha):
    timestamp_nsecs = str(timestamp_int)
    timestamp = rospy.Time(int(timestamp_nsecs[0:-9]), int(timestamp_nsecs[-9:]))

    rosimu = Imu()
    rosimu.header.stamp = timestamp
    rosimu.angular_velocity.x = float(omega[0])
    rosimu.angular_velocity.y = float(omega[1])
    rosimu.angular_velocity.z = float(omega[2])
    rosimu.linear_acceleration.x = float(alpha[0])
    rosimu.linear_acceleration.y = float(alpha[1])
    rosimu.linear_acceleration.z = float(alpha[2])

    return rosimu, timestamp


def create_bag(data_dir: str):
    try:
        data_dir = os.path.join(data_dir, "cam-imu")
        result_dir = os.path.join(data_dir, "rosbag")
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)

        imu_file = os.path.join(data_dir, "mav0", "imu0", "data.csv")
        if not os.path.exists(imu_file):
            print(f"imu file not exist,file={imu_file}")
            exit(-1)

        bag_path = os.path.join(result_dir, 'data.bag')
        bag = rosbag.Bag(bag_path, 'w')

        # write images
        timestamps, image_files = getImageFilesFromDir(data_dir)
        for image_filename in image_files:
            image_msg, timestamp = loadImageToRosMsg(image_filename)
            bag.write("/cam0/image_raw", image_msg, timestamp)

        # write imu data
        # topics: /cam0/image_raw       msgs: sensor_msgs / Image
        #        /imu0       msgs: sensor_msgs / Imu
        with open(imu_file, 'rb') as f:
            reader = csv.reader(f, delimiter=',')
            # headers = next(reader, None)
            for row in reader:
                imu_msg, timestamp = createImuMessge(row[0], row[1:4], row[4:7])
                bag.write("/imu0", imu_msg, timestamp)

    finally:
        bag.close()


# create the bag
if __name__ == "__main__":
    # setup the argument list
    parser = argparse.ArgumentParser(description='Create a ROS bag using the images and imu data.')
    parser.add_argument('data_dir', metavar='folder', nargs='?', help='Data folder')
    parser.add_argument('--output-bag', metavar='output_bag', default="output.bag", help='ROS bag file %(default)s')

    # print help if no argument is specified
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    # parse the args
    args = parser.parse_args()
    create_bag(args.data_dir)
