#!/usr/bin/env python
import rospy
from std_msgs.msg import Float32

class PID:
    def __init__(self, kp = 1.1, kd = 0.6 , ki = 0.01, rate = 10):
        self.kp = kp
        self.ki = ki 
        self.kd = kd 
        self.past_error = 0
        self.error_sum = 0
        self.e = 0
        self.output  = 0 
        self.t = 1 / rate

    def error_listner(self):
        error = rospy.wait_for_message("lane_value", Float32)
        self.e = error.data
    
    def compute(self):
        if self.e != 0 :
            p  = self.e * self.kp 
            d = self.kd * (self.e - self.past_error) / self.t
            i = self.ki * (self.error_sum + self.e * self.t)
            self.output = p + i + d 
            self.past_error =  self.e 
            self.error_sum = (self.error_sum + self.e) * 0.1 

        else:
            self.past_error =  0 
            self.error_sum = 0
            self.output = 0