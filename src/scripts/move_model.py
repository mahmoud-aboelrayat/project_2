#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
from pid_controller import PID

class movement :

    def __init__(self):
        rospy.init_node('move_robot_node', anonymous=False)
        self.pub_move = rospy.Publisher("/cmd_vel",Twist,queue_size=10)
        self.move = Twist()
        self.f = 10 
        self.t = 0.5 
        self.v_max = 0
        self.v = 0
        self.v_step = self.v_max / (self.f * self.t)
        self.u = 0 



    def publish_vel(self):
        self.pub_move.publish(self.move)

    def move_forward(self):
        if self.v <= self.v_max:
            self.move.linear.x= self.v
            self.v += self.v_step
        self.move.linear.x = self.v_max
        self.move.angular.z = -0.5* self.u 

    def move_backward(self):    
        if self.v != -self.v_max:
            self.move.linear.x= self.v
            self.v -= self.v_step  
        self.move.angular.z=0.0

    def stop(self):        
        self.v  = 0
        self.move.linear.x= self.v
        self.move.angular.z=0.0  


if __name__ == "__main__":
    mov = movement()
    pid = PID(kp = 1.1, kd = 0.6 , ki = 0.01, rate = mov.f)
    rate = rospy.Rate(mov.f)
    
    while not rospy.is_shutdown() :
        c = rospy.wait_for_message("/command", Float32)
        if c.data == 0:
            movement = "stop"
        else:
            movement = "forward"
            mov.v_max = c.data 

        pid.error_listner()
        pid.compute()
        mov.u = pid.output
        print(movement)
        if movement == 'forward':
            mov.move_forward()

        if movement == 'backward':
            mov.move_backward()

        if movement == 'stop':
            mov.stop()

        mov.publish_vel()
        rate.sleep()

#rosservice call /gazebo/reset_simulation "{}"