#!/usr/bin/env python
from math import pi
import rospy
from geometry_msgs.msg import PoseArray,Pose, PoseWithCovarianceStamped
from nav_msgs.msg import OccupancyGrid
import numpy as np 
from tf.transformations import quaternion_from_euler
import tf 

class particales:
    def __init__(self):
        rospy.init_node('particale', anonymous=False)
        self.f = 10
        self.pub_par = rospy.Publisher("/particlecloud",PoseArray,queue_size=10 ,latch=True)
        self.particals = PoseArray()
        self.n = 4 
        self.width = 0
        self.height = 0
        self.res = 0
        self.map_origin_x = 0
        self.map_origin_y = 0
        self.free = [] 
        self.oriantation = []
        self.init_pose = [] 
       

    
    def init_particales(self):
        rand = np.random.randint(0,len(self.free))
        p = Pose()
        p.position.x = (self.free[rand][1] ) * self.res + self.map_origin_x
        p.position.y = (self.free[rand][0]) * self.res +  self.map_origin_y
        
        p.position.z = 0
        par_yaw = np.random.uniform(0, 2 * pi)
        self.oriantation = quaternion_from_euler(0, 0, par_yaw)
        p.orientation.x = self.oriantation[0]
        p.orientation.y = self.oriantation[1]
        p.orientation.z = self.oriantation[2]
        p.orientation.w = self.oriantation[3]
        self.particals.poses.append(p)
        
    def sub(self):
        map = rospy.wait_for_message("/map", OccupancyGrid)
        self.occ_map(map)
        
    def occ_map(self, msg):
        self.width = msg.info.width 
        self.height = msg.info.height
        self.res = msg.info.resolution
        self.map_origin_x = msg.info.origin.position.x
        self.map_origin_y = msg.info.origin.position.y
        data =  np.reshape(msg.data,(self.width,self.height))
        for i in range(self.width):
            for j in range(self.height):
                if data[i][j] == 0:
                    self.free.append([i,j])
    def pub(self):
        self.particals.header.frame_id = "map"
        self.particals.header.seq = 0
        self.particals.header.stamp = rospy.Time.now()
        self.pub_par.publish(self.particals)


if __name__ == "__main__":
    particle_num= 3000
    par = particales()
    br = tf.TransformBroadcaster()
    rate = rospy.Rate(par.f)
    n = par.n
    par.sub()

    for i in range(particle_num):
        par.init_particales()

    par.pub()
    while not rospy.is_shutdown() :
        br.sendTransform((0,0, 0),
                        quaternion_from_euler(0,0,0),
                        rospy.Time.now(),
                        "odom",
                        "map")
        
        rate.sleep()

