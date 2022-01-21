#!/usr/bin/env python
import rospy
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist


def move(lane_val):
    
    vel_msg = Twist()

    vel_msg.linear.x = 0.2
    vel_msg.linear.y = 0
    vel_msg.linear.z = 0
    vel_msg.angular.x = 0
    vel_msg.angular.y = 0
    vel_msg.angular.z = -lane_val.data
    
    velocity_publisher.publish(vel_msg)

if __name__ == "__main__":
    rospy.init_node('robot_cleaner', anonymous=True)
    velocity_publisher = rospy.Publisher('cmd_vel', Twist, queue_size=10)
    rospy.Subscriber('lane_value', Float32, move)
    rospy.spin()