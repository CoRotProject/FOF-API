import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import quaternionTransforms

def poseToMove(x, y, Yaw):
    #transformation de l angle en yaw en quaternion
    quaternion = quaternionTransforms.euler_to_quaternion(Yaw,0,0)

    client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
    client.wait_for_server()

    #remplissage de l objet goal, pour l'envoyer par la suite (les valeurs non precisees sont par defaut a 0)
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.orientation.z = quaternion[2]
    goal.target_pose.pose.orientation.w = quaternion[3]

    client.send_goal(goal)
    wait = client.wait_for_result()
    if not wait:
        rospy.logerr("Action server not available!")
        rospy.signal_shutdown("Action server not available!")
    else:
        return client.get_result()


if __name__ == '__main__':
    position = [3]
    position.insert(0, int(input("entrez la position en x :")))
    position.insert(1, int(input("entrez la position en y :")))
    position.insert(2, int(input("entrez la rotation :")))
    try:
        rospy.init_node('movebase_client_py')
        result = poseToMove(position[0], position[1], position[2])
        if result:
            rospy.loginfo("Goal execution done!")
    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation test finished.")
        