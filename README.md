# PalletSim to UR
 
A simple simulation application for executing palletizing tasks with steps to integrate with UR (Universal Robots) cobot using TCP/IP.

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)  
   - [1.1 Installation of Python](#11-installation-of-python)  
   - [1.2 Virtual Environment Setup (With venv)](#12-virtual-environment-setup-with-venv)  
     - [1.2.1 Bypass Errors When Accessing `myenv/Scripts/activate` in PowerShell](#121-bypass-errors-when-accessing-myenvscriptsactivate-in-powershell)  
     - [1.2.2 Installation of Dependencies in venv](#122-installation-of-dependencies-in-venv)  
     - [1.2.3 Upload .urp File on UR Robot](#123-upload-urp-file-on-ur-robot)  
2. [Steps to Run Python Program](#2-steps-to-run-python-program)  
   - [2.1 Setup](#21-setup)  
     - [2.1.1 Connect Ethernet from PC to Robot](#211-connect-ethernet-from-pc-to-robot)  
     - [2.1.2 Change Ethernet IP Address](#212-change-ethernet-ip-address)  
   - [2.2 Running the Program](#22-running-the-program)  
     - [2.2.1 Get PC IP Address](#221-get-pc-ip-address)  
     - [2.2.2 Adding and Customizing Box Dimensions](#222-adding-and-customizing-box-dimensions)  
     - [2.2.3 Layers](#223-layers)  
     - [2.2.4 Send Box Pose](#224-send-box-pose)  
         - [2.2.4.1 Open Connection between PC and UR Cobot](#2241-open-connection-between-pc-and-ur-cobot)
       - [2.2.4.2 Poses of All Boxes in Current Layer](#2242-poses-of-all-boxes-in-current-layer)  
       - [2.2.4.3 Poses of Certain Boxes in Current Layer](#2243-poses-of-certain-boxes-in-current-layer)   
3. [Steps to Use the Application on UR Robot](#3-steps-to-use-the-application-on-ur-robot)  
   - [3.1 Creation of Plane-feature](#31-creation-of-plane-feature)  
   - [3.2 Approach and Exit Points](#32-approach-and-exit-points)  
4. [Additional Steps](#4-additional-steps)  
5. [License](#5-license)
---
## 1. Prerequisites

Before getting started, ensure that the following are installed on your system:

### 1.1 Installation of Python

1. Download and install the latest version of Python from the [official website](https://www.python.org/downloads/).
2. Ensure that the Python installation is added to your system's PATH.
3. Verify Python installation by running the following in the command prompt or terminal:

   ```bash
   python --version
   ```

### 1.2 Virtual Environment Setup (With venv)
Set up a Python virtual environment for dependency management.

```bash
cd path/to/your/project
```
Create a new virtual environment using the following command:

```bash
python -m venv myenv
```
To activate the virtual environment, follow the instructions based on your operating system:

- #### Windows:

```bash
myenv\Scripts\activate
```
- #### macOS/Linux:

```bash
source myenv/bin/activate
```

If you encounter errors/issues with activating the virtual environment, refer to the next section.

### 1.2.1 Bypass Errors When Accessing myenv/Scripts/activate in PowerShell
If you encounter an error while trying to activate the virtual environment in PowerShell, follow these steps:

Open PowerShell.

Run the following command to bypass the execution policy temporarily:

```bash
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

.\myenv\Scripts\activate
```

This will allow you to activate the virtual environment without encountering script execution policy errors

### (TO-DO) 1.2.2 Installation of Dependencies in venv
Once your virtual environment is activated, install the required dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all dependencies listed in your project's requirements.txt file.

### 1.2.3 Upload .urp file on UR robot
1. Copy the provided .urp program to a USB.

2. Plug the USB into the UR teach pendant.

3. Navigate to Program > Load > USB and select the .urp file.

4. Modify IP address in the script to match your PC’s IP (used for TCP communication).

## 2. Steps to Run Python Program

### 2.1 Setup

#### 2.1.1 Connect Ethernet from PC to Robot
Use a direct Ethernet cable and connect it from PC to robot.

#### 2.1.2 Change Ethernet IP Address

#### On your PC:

1. Open Control Panel > Network and Sharing Center > Adapter Settings

2. Right-click Ethernet > Properties > IPv4

3. Set a static IP (e.g., 192.168.1.100)

4. Set Subnet Mask to 255.255.255.0

#### On your UR Robot

1. Open Hamburger Menu (Top Right corner) > TODO > Network 

2. Select and set Static IP

3. Set robot IP the same for first 3 IP blocks "192.168.1.XXX". 

   - X value can be any other value other than the one that was used for the PC (100)

3. Set Subnet Mask to 255.255.255.0

4. Ensure it says "_Network is Connected_" 

#### Verify establishment of network connection 

Verify the connection via the PC for Windows/macOS/Linux using Command Prompt/Terminal respectively and type in:

```bash
ping 192.168.1.XXX
```

A successful connection will show a reply.  
An unsuccessful connection will "Request timed out" or there are Lost/no Received packets.

---

### 2.2 Running the Program
```bash
cd path/to/project
python multilayer_testing.py
```

### 2.2.1 Get PC IP Address  
From the dropdown, select the correct **Ethernet interface** that is connected to the robot.  

---

### 2.2.2 Adding & Customizing Box Dimensions  

This section mentions how you can define the dimensions of the Box/Object that the robot will pick.

🖼️ *[Insert screenshot or image of the interface highlighting the box here]*

1. **Configure box dimensions**  
   - You can manually input custom dimensions (length, width, height).  
   - *Note: The height of the box will determine the starting height of the next layer.*

2. **Box Actions**  
   - Add a new box  
   - Delete an existing box  
   - Jog (move) a box to fine-tune its position  
   - Rotate the box for better placement

---

### 2.2.3 Layers  
Use the available layer controls to manage multiple stacking layers:

- **Add** a new layer  
- **Delete** the current layer  
- **Duplicate** the current layer  
- **Go to Previous Layer**  
- **Go to Next Layer**

### 2.2.4 Send Box Pose  
Once you've created your boxes and layers, the buttons in this section allow you to **connect to the robot** and **send pose data (Position & Orientation)** for execution.

*[Insert screenshot or image of the interface here]*

---

### 2.2.4.1 Open Connection between PC and UR Cobot  
This button starts a **TCP/IP server** on your PC, which opens a socket that the robot can connect to.

---

### 2.2.4.2 Send Poses of All Boxes in Current Layer  
This section includes a dropdown with two options:

1. **Send poses for all boxes in the current layer only**
2. **Send poses for all boxes across all layers**

---

### 2.2.4.3 Send Poses of Specific Boxes in Current Layer  
This option allows you to test individual box poses before sending everything.

- Select a **box index** from the dropdown.
- Choose from the following actions:

1. **Send the pose of the selected box only**
2. **Send the pose of the selected box and all boxes after it** (on the same layer)

---


## 3. Steps to Use the Application on UR Robot  
The robot program has been configured for simple setup with just a few required inputs from your end.  
To get started, you'll need to configure the relevant fields in both the **UR Robot Program** and the **Installation tab**.

---

### 3.1 Creation of Plane Feature  
In the **UR Installation tab**, create a new **plane feature** that matches the origin and orientation of your Pallet Sim program.

- The **origin** of this plane should align with `(0, 0)` of the Pallet Sim.
- The **X and Y axes** should follow the **Right-Hand Rule** based on your physical setup.

This alignment ensures that the robot operates in the same coordinate space as the simulation.

---

### 3.2 Conveyor & Pallet: Approach, Exit, and Pick Points  
There are two sets of Approach and Exit points that must be taught manually:

1. **Conveyor Pick Point**  
   - Define the **Pick**, **Approach**, and **Exit** positions for the conveyor.  
   - These are determined by you based on your layout.

2. **Pallet Approach & Exit Points**  
   - Define where the robot should move before and after interacting with the pallet. This can be changed to 


These positions are critical for smooth motion planning and safe operation.

---

### 3.3 Gripper Actions  
You will also need to configure how the gripper operates. This can be done using:

- Digital/Analog **I/O signals**  
- **URCaps** (if you are using a custom or advanced gripper system)

Ensure the gripping logic matches your hardware capabilities.

---

## 4. Additional Steps
Reserved 

## 5.License
Reserved
