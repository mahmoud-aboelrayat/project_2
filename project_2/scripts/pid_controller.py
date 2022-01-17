#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64
import numpy as np 


def pid_controller(data):
    global past_error
    global error_sum
    global u 

    e = a * data.data + b 

    if e != 0 :
        p  = e * kp 
        d = kd * (e- past_error) / 0.1
        i = ki * (error_sum + e * 0.1)
        u = p + i +d 
        past_error =  e 
        error_sum = (error_sum + e * 0.1)
        return u 

    else:
        past_error =  0 
        error_sum = 0
        u = 0
        return u 

def listener():

    rospy.init_node('pid', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        error = rospy.wait_for_message("error",Float64)
        u = pid_controller(error)
        pub = rospy.Publisher('pid', Float64 , queue_size=10)
        print(u)
        pub.publish(u)
        rate.sleep()

if __name__ == '__main__':
    kp = 8
    kd = 0.1 
    ki = 0.01
    a = 1
    b = 0.0
    u  = 0
    error_sum = 0.0 
    past_error =  0.0
    listener()