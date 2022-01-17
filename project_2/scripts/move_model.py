#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

class movement :

    def __init__(self):
        rospy.init_node('move_robot_node', anonymous=False)
        self.pub_move = rospy.Publisher("/cmd_vel",Twist,queue_size=10)
        self.move = Twist()
        self.f = 10 
        self.t = 0.5 
        self.v_max = 0.1 
        self.v = 0
        self.v_step = self.v_max / (self.f * self.t)
        self.u = 0 
        self.vr = 0 
        self.vl = 0
        self.l = 0.25 #robot width


    def publish_vel(self):
        self.pub_move.publish(self.move)

    def pid_sub(self):
        u = rospy.wait_for_message("pid", Float64)
        self.u = u.data
    
    def move_forward(self):
        if self.v <= self.v_max:
            self.move.linear.x= self.v
            self.v += self.v_step
        self.move.linear.x = self.v_max
        self.move.angular.z = -0.5 * self.u 

    def move_backward(self):    
        if self.v != -self.v_max:
            self.move.linear.x= self.v
            self.v -= self.v_step  
        self.move.angular.z=0.0

    def stop(self):        
        self.v  = 0
        self.move.angular.z=0.0  

    def diff_drive(self):
        self.vr = (self.l * self.u + self.v * 2) / 2
        self.vl = 2 * self.v - self.vr

        if self.vl * self.vr < 0: 
            self.vl = 0
            self.vr = self.l * self.u
        

if __name__ == "__main__":
    mov = movement()
    rate = rospy.Rate(mov.f)
    

    while not rospy.is_shutdown() :
        command= rospy.wait_for_message("my_cmd_vel", Twist)
        print(command)
        if command.linear.x == 0:
            movement = "stop"
        elif command.linear.x > 0:
            movement = "forward"
        elif command.linear.x < 0:
            movement = "backward"
        print(movement)

        mov.pid_sub()

        if movement == 'forward':
            mov.move_forward()

        if movement == 'backward':
            mov.move_backward()

        if movement == 'stop':
            mov.stop()

        mov.publish_vel()
        rate.sleep()

#rosservice call /gazebo/reset_simulation "{}"