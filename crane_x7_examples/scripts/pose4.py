#! /usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import moveit_commander
import math
import geometry_msgs.msg
from control_msgs.msg import GripperCommandAction, GripperCommandGoal
from tf.transformations import quaternion_from_euler
import rosnode
import actionlib
import time
import sys
import random
import choki 
import gu
import par

class GripperClient(object):
    def __init__(self):
        self._client = actionlib.SimpleActionClient("/crane_x7/gripper_controller/gripper_cmd",GripperCommandAction)
        self._goal = GripperCommandGoal()

        # Wait 10 Seconds for the gripper action server to start or exit
        self._client.wait_for_server(rospy.Duration(10.0))
        if not self._client.wait_for_server(rospy.Duration(10.0)):
            rospy.logerr("Exiting - Gripper Action Server Not Found.")
            rospy.signal_shutdown("Action Server not found.")
            sys.exit(1)
        self.clear()

    def command(self, position, effort):
        self._goal.command.position = position
        self._goal.command.max_effort = effort
        self._client.send_goal(self._goal,feedback_cb=self.feedback)

    def feedback(self,msg):
        print("feedback callback")
        print(msg)

    def stop(self):
        self._client.cancel_goal()

    def wait(self, timeout=0.1 ):
        self._client.wait_for_result(timeout=rospy.Duration(timeout))
        return self._client.get_result()

    def clear(self):
        self._goal = GripperCommandGoal()

def main():

    z = 0.2 #移動するときの高さ
    min_z = 0.15    #掴むときのアームの高さ
    y = 0.0      
    max_z = 0.25
    x1 = 0.1
    x2 = 0.15
    x3 = 0.2
    x4 = 0.25
    x5 = 0.3

    i = random.randint(1, 3)
    #rospy.init_node("gripper_action_client")
    robot = moveit_commander.RobotCommander()
    arm = moveit_commander.MoveGroupCommander("arm")
    #アームの動きの速さを示している
    arm.set_max_velocity_scaling_factor(1.0)

    gripper = moveit_commander.MoveGroupCommander("gripper")
    

    while len([s for s in rosnode.get_node_names() if 'rviz' in s]) == 0:
        rospy.sleep(1.0)
    rospy.sleep(1.0)

    print("Group names:")
    print(robot.get_group_names())

    print("Current state:")
    print(robot.get_current_state())

    # アーム初期ポーズを表示
    arm_initial_pose = arm.get_current_pose().pose
    print("Arm initial pose:")
    print(arm_initial_pose)

    # SRDFに定義されている"home"の姿勢にする
    arm.set_named_target("home")
    arm.go()
    gripper.set_joint_value_target([0.01, 0.01])
    gripper.go()
    
    
    #繰り返し呼び出すのでmove関数を定義する
    def move(x,y,z):
        target_pose = geometry_msgs.msg.Pose()
        target_pose.position.x = x
        target_pose.position.y = y
        target_pose.position.z = z
        q = quaternion_from_euler(-3.14, 0.0, 3.14)  
        target_pose.orientation.x = q[0]
        target_pose.orientation.y = q[1]
        target_pose.orientation.z = q[2]
        target_pose.orientation.w = q[3]
        arm.set_pose_target(target_pose)  
        arm.go()  
	
	#最初はグーの動き
    move(x1, y, z)   
    rospy.sleep(1.0)
    
    move(x1, y, min_z)
   # move(x2, y, z)
    move(x3, y, max_z)
   # move(x4, y, z)
    move(x5, y, min_z)
    move(x3, y, max_z)
    move(x1, y, min_z)
    move(x3, y, max_z)

    arm.set_named_target("home")
    arm.go() 

    if i==1:
		choki.main()
    elif i == 2:
		gu.main()
    else:
		par.main()
		

    print("done")


if __name__ == '__main__':

    try:
        if not rospy.is_shutdown():
            main()
    except rospy.ROSInterruptException:
        pass
