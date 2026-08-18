# import the necessary python libraries
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import math
from target_pose.srv import TargetPose
from geometry_msgs.msg import Twist

# creating the python ros2 node
class PoseController(Node):

    def __init__(self):
        super().__init__("pose_controller_node")
        self.get_logger().info("Pose controller started")

        # initializing variables for robot position
        self.pose_x = 0.0; self.pose_y = 0.0; self.pose_yaw = 0.0

        # initializing target position
        self.target = None

        # creating the robot position subscriber
        self.odometry_subscriber = self.create_subscription(Odometry, '/odom', self.odometry_callback, 10)

        # creating the service that handles the user target input
        self.srv = self.create_service(TargetPose, 'target_pose', self.handle_request)

        # creating the control command publisher
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # creating a timer that determines the frequency of the control loop
        self.timer = self.create_timer(0.05, self.control_loop)

    # the subscriber callback function that collects and correctly formats the odometry parameters to obtain the desired x, y and yaw
    def odometry_callback(self, msg: Odometry):
        self.pose_x = msg.pose.pose.position.x
        self.pose_y = msg.pose.pose.position.y

        qx = msg.pose.pose.orientation.x
        qy = msg.pose.pose.orientation.y
        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w

        self.pose_yaw = math.atan2(2.0*(qw*qz + qx*qy), 1.0-2.0*(qy*qy + qz*qz))

        self.get_logger().info(f"x={self.pose_x:.3f}, y={self.pose_y:.3f}, yaw={self.pose_yaw:.3f}")

    # the service callback that collects and processes the user input
    def handle_request(self, request, response):
        self.target = [request.input_x, request.input_y, math.radians(request.input_yaw)]
        self.get_logger().info(f"New target: {self.target}")
        response.success = True
        response.message = 'Goal accepted, moving to target'
        return response

    # control loop that processes user request with respect to the current position and sends required control signals
    def control_loop(self):
        if self.target is None:
            return

        dx = self.target[0] - self.pose_x
        dy = self.target[1] - self.pose_y
        distance = math.hypot(dx, dy)

        alpha = self.normalize_angle(math.atan2(dy,dx) - self.pose_yaw)
        beta = self.normalize_angle(self.target[2] - self.pose_yaw)

        if self.goal_reached(distance, beta):
            self.get_logger().info("Goal reached, stopping")
            self.stop_robot()
            self.target = None
            return

        cmd = Twist()
        kv = 0.6; ka = 1.8; 
             
        if distance > 0.05:
            kb = -0.5
            v = min(0.22, kv*distance) * max(0.0, math.cos(alpha))
            w = ka*alpha + kb*beta
        else:
           kb = 1.0
           v = 0.0
           w = kb*beta

        v = max(-0.22, min(0.22, v))
        w = max(-2.84, min(2.84, w))

        cmd.linear.x = v
        cmd.angular.z = w
        self.cmd_vel_pub.publish(cmd)


    # function to normalize an angle between -pi and +pi
    @staticmethod       
    def normalize_angle(angle: float) -> float:
        while angle > math.pi:
            angle -= 2.0*math.pi
        while angle < -math.pi:
            angle += 2.0*math.pi
        return angle

    # funtion to determine that the robot is within the accepted target tolerance
    @staticmethod           
    def goal_reached(d: float, yaw_err: float) -> bool:
        return d < 0.05 and abs(yaw_err) < math.radians(5.0)

    # function to stop the robot
    def stop_robot(self):
        cmd = Twist()
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = PoseController()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()