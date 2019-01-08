#!/usr/bin/env python  
#import roslib
#roslib.load_manifest('learning_tf')
import rospy
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Header

from dynamic_reconfigure.server import Server
from marker_based_localisation.cfg import PoseBiasAdjustConfig

class Bias_corrector:
    
    def __init__(self):
        #get private NS params from bash or launch file
        self.init_message = rospy.get_param('~start message','Adjust Node started')
        self.input_topic = rospy.get_param('~input_topic','/vrpn_client_node/Solo/pose')
        self.output_topic = rospy.get_param('~output_topic','/ground_truth/pose')
        self.make_zero = rospy.get_param('~make_zero',False)
        self.reset = True
        rospy.loginfo('Input_topic: %s', self.input_topic)
        rospy.loginfo('Output_topic: %s', self.output_topic)

        #Start dynamic reconfigure server
        self.server = Server(PoseBiasAdjustConfig,self.reconfigure)

        self.sub = rospy.Subscriber(self.input_topic,PoseStamped,self.correct_bias)
        self.pub = rospy.Publisher(self.output_topic,PoseStamped,queue_size = 10)
        rospy.spin()

    def correct_bias(self,data):

        self.input_topic = self.input_topic 
        self.output_topic = self.output_topic
        # rospy.loginfo('New Input_topic: %s', self.input_topic)
        # rospy.loginfo('New Output_topic: %s', self.output_topic)
        
        #construct a new message from Pose data Class and add header
        msg = PoseStamped(header=Header(stamp=rospy.get_rostime(),frame_id ='map_fid'))
        pos = data.pose.position
        ori = data.pose.orientation

        # if self.make_zero == True and self.reset == True:
        #     msg.pose.position.x = pos.y - pos.y
        #     msg.pose.position.y = 0.0-pos.x +pos.x
        #     msg.pose.position.z = pos.z - pos.z 

        #     msg.pose.orientation.x = ori.x - ori.x
        #     msg.pose.orientation.y = ori.y - ori.y
        #     msg.pose.orientation.z = ori.z - ori.z
        #     msg.pose.orientation.w = ori.w - ori.w
            
        # adjust bad data by subracting bias 
        msg.pose.position.x = pos.y + self.x_posbiasinput
        msg.pose.position.y = 0.0-pos.x + self.y_posbiasinput
        msg.pose.position.z = pos.z + self.z_posbiasinput

        msg.pose.orientation.x = ori.y + self.x_rotbiasinput +0.005
        msg.pose.orientation.y = 0.0-ori.x + self.y_rotbiasinput + 0.009
        msg.pose.orientation.z = ori.z + self.z_rotbiasinput
        msg.pose.orientation.w = ori.w + self.w_rotbiasinput
              
        self.pub.publish(msg)
        # rospy.loginfo('Bias corrected IMU linear acc')
        rospy.loginfo_throttle(120,self.init_message)
        
        
    # Create a callback function for the dynamic reconfigure server.
    def reconfigure(self, config, level):
        # Fill in local variables with values received from dynamic reconfigure clients (typically the GUI).
        self.input_topic = config["input_topic"]
        self.output_topic = config["output_topic"]
        self.make_zero = config["make_zero"]
        rospy.loginfo('Input_topic: %s', self.input_topic)
        rospy.loginfo('Output_topic: %s', self.output_topic)
        self.x_posbiasinput = config["X_position"]
        self.y_posbiasinput = config["Y_position"]
        self.z_posbiasinput = config["Z_position"]
        self.x_rotbiasinput = config["X_orientation"]
        self.y_rotbiasinput = config["Y_orientation"]
        self.z_rotbiasinput = config["Z_orientation"]
        self.w_rotbiasinput = config["W_orientation"]
        return config

if __name__ == '__main__':
    try:
        rospy.init_node('pose_adjuster')
        bc = Bias_corrector()
    except rospy.ROSInterruptException:
        pass