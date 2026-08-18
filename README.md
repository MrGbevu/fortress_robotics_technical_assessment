## **Robotics Technical Assessment 2026 – Pose Controller (ROS 2, Python)**

This repository contains a simple ROS 2 pose controller for the TurtleBot3 simulation. The controller accepts a target pose via a ROS 2 service and drives the robot smoothly toward the requested position and orientation using continuous closed‑loop control.

---

## **1. Install Dependencies**

### **ROS 2 Humble**
Follow the official installation guide:  
`https://docs.ros.org/en/humble/Installation.html`

### **TurtleBot3 Packages**
Install TurtleBot3 simulation packages:

```bash
sudo apt install ros-humble-turtlebot3*
```

Set the model (recommended for simulation):

```bash
echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
source ~/.bashrc
```

### **Build the Workspace**

From the workspace root:

```bash
colcon build
source install/setup.bash
```

---

## **2. Run the TurtleBot3 Simulation**

Launch Gazebo with the TurtleBot3:

```bash
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

This starts the robot at:

- **x = 0**
- **y = 0**
- **yaw = 0°**

as required by the assessment.

---

## **3. Start the Pose Controller Node**

In a new terminal:

```bash
source install/setup.bash
ros2 run turtlebot3_pose_controller pose_controller_node
```

The node will:

- Subscribe to `/odom`  
- Publish velocity commands to `/cmd_vel`  
- Provide the `/target_pose` service  

---

## **4. Call the Pose Command Service**

Use the custom service to command a target pose:

```bash
ros2 service call /target_pose target_pose/srv/TargetPose "{x: 1.0, y: 0.5, yaw_deg: 45.0}"
```

Example test commands (from the assessment):

```bash
ros2 service call /target_pose target_pose/srv/TargetPose "{x: 1.0, y: 0.5, yaw_deg: 45.0}"
ros2 service call /target_pose target_pose/srv/TargetPose "{x: -1.0, y: 0.8, yaw_deg: 90.0}"
ros2 service call /target_pose target_pose/srv/TargetPose "{x: 0.5, y: -0.5, yaw_deg: -90.0}"
```

The robot will move smoothly toward each pose and stop within:

- **±5 cm** positional tolerance  
- **±5°** orientation tolerance  

---

## **Repository Contents**

- `turtlebot3_pose_controller/` — main ROS 2 package  
- `target_pose/` — custom service definition  
- `pose_controller.py` — continuous pose‑regulation controller  
- `.gitignore` — excludes build/install/log folders  

---

## **Notes**

- No navigation stack (Nav2) is used.  
- All control logic is implemented manually as required.  
- Motion is continuous (no rotate‑drive‑rotate sequences).  
