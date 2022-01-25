#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Float32

from cv_bridge import CvBridge

from lane_detection import get_lane_value, set_publisher

lane_value = -1

def callback(ros_rgb_image):
    global lane_value

    bridge = CvBridge()
    cv_image = bridge.imgmsg_to_cv2(ros_rgb_image, desired_encoding='bgr8')
    value = get_lane_value(cv_image)
    if value is not None:
        lane_value = value

def listener():
    rospy.init_node('image_lane_finder', anonymous=True)

    rospy.Subscriber("/camera/rgb/image_raw", Image, callback)

def publisher():
    pub = rospy.Publisher('lane_value', Float32, queue_size=10)
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        pub.publish(lane_value)
        rate.sleep()

if __name__ == '__main__':
    listener()
    set_publisher(rospy.Publisher('image_cv2', Image, queue_size=1))
    publisher()