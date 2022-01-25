#!/usr/bin/env python

import rospy
from std_msgs.msg import String, Float64
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion
from math import pi


def set_error(error):
    if error - dr > 0:
        error -= dr
    elif error +dr < 0:
        error += dr
    else:
        error =0

    return round(error,5)


def talker():
    pub = rospy.Publisher('error', Float64 , queue_size=10)
    rospy.init_node('error_publisher', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    
    while not rospy.is_shutdown():
        rotation = rospy.wait_for_message('odom', Odometry)
        ro = rotation.pose.pose.orientation
        roll, pitch, yaw = euler_from_quaternion([ro.x,ro.y,ro.z,ro.w ])
        error = yaw  / pi - desired_angle
        pub.publish(error)
        #error = set_error(error)
        
        rate.sleep()



if __name__ == '__main__':
    dr = 0.005
    desired_angle = 0 
    try:

        talker()
    except rospy.ROSInterruptException:

        pass
