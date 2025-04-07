# PalletSim to UR
 
A simple simulation application for executing palletizing tasks with steps to integrate with UR (Universal Robots) cobot using TCP/IP.

## Table of Contents
1. [Prerequisites](#prerequisites)
   - [Installation of Python](#installation-of-python)
   - [Virtual Environment Setup (With venv)](#virtual-environment-setup-with-venv)
     - [Bypass Errors When Accessing `myenv/Scripts/activate` in PowerShell](#bypass-errors-when-accessing-myenvscriptsactivate-in-powershell)
     - [Installation of Dependencies in venv](#installation-of-dependencies-in-venv)
     - [1.2.3 Upload .urp file on UR robot](#upload .urp file on UR Robot robot)
2. [Steps to Run Python Program](#steps-to-run-python-program)
3. [Steps to Use the Application](#steps-to-use-the-application)
4. [Additional Steps](#additional-steps)
5. [License](#License)

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
This should return the Python version installed on your system.

### 1.2 Virtual Environment Setup (With venv)
A virtual environment helps you manage project dependencies in isolation. Here's how to set it up:

Open your terminal or command prompt.

Navigate to your project directory.

```bash
cd path/to/your/project
```
Create a new virtual environment using the following command:

```bash
python -m venv myenv
```
To activate the virtual environment, follow the instructions based on your operating system:

#### Windows:

```bash
myenv\Scripts\activate
```
#### macOS/Linux:

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
```

Now, activate your virtual environment:

```bash
.\myenv\Scripts\activate
```

This will allow you to activate the virtual environment without encountering script execution policy errors

### (TO-DO) 1.2.2 Installation of Dependencies in venv
Once your virtual environment is activated, install the required dependencies by running:

```bash
pip install -r requirements.txt
```
### 1.2.3 Upload .urp file on UR robot
1. Download the pre-programmed *filename*.urp onto a USB-drive
2. Plug in USB-drive into Teachpendant and upload .urp file on robot

This will install all dependencies listed in your project's requirements.txt file.

## 2. Steps to Run Python Program
Once the virtual environment is set up and dependencies are installed, you can run your Python program by executing the following command:

```bash
cd *PATHTOFOLDER*
python ./multilayer_testing.py
```

## 3. Steps to use the Application
#### 3.1 Application
In this section, you can add detailed instructions on how to use the application once its features are defined. For now, you can leave it as "To figure out later."

### 3.2 . Robot 
## 4. Additional Steps
If there are any additional setup steps or configuration required, list them here.

## 5.License
Include licensing information here if applicable.
