# Linux-System-Monitor
Python-based Linux system monitor for users, processes, services and network conections.
Linux System Monitor

A Python-based Linux system monitoring tool that collects and displays information about logged-in users, running processes, system services, and listening network connections.

The tool uses Linux system utilities through Python's "subprocess" module and presents the collected information in formatted tables and panels using Rich.

Features:

- Current User:
  
  - Identifies the current user using "whoami".

- Logged-In Users:
  
  - Lists currently logged-in users using "who".
  - Displays username, TTY, login time, and source/host.

- Running Processes:
  
  - Retrieves running processes using "ps aux".
  - Displays all detected processes.
  - Sorts processes by CPU usage.
  - Shows:
    - User
    - PID
    - CPU usage
    - Memory usage
    - VSZ
    - RSS
    - Full command

- System Services:
  
  - Retrieves system services using "systemctl".
  - Displays whether services are enabled and currently active.

- Network Connections:
  
  - Retrieves listening TCP ports using "ss -tlnp".
  - Falls back to "netstat -tlnp" if "ss" is unavailable.
  - Displays up to 20 detected listening connections.

- Rich Terminal Interface:
  
  - Uses Rich tables and panels to organize and display system information in the terminal.

Technologies:

- Python 3
- Rich
- Linux system utilities:
  - "who"
  - "whoami"
  - "ps"
  - "systemctl"
  - "ss"
  - "netstat" (fallback)

Project Structure:

linux-system-monitor/
├── security_check.py
├── README.md
└── requirements.txt

Requirements:

- Linux system
- Python 3
- Required Linux utilities available on the system
- Python package listed in "requirements.txt"

The "systemctl" command requires a system using systemd, while "ss" is normally provided by the system's networking utilities.

Installation:

Clone the repository and enter the project directory:

git clone <repository-url>
cd linux-system-monitor

Creating a virtual environment is recommended:

python3 -m venv .venv
source .venv/bin/activate

Install the required Python dependency:

python -m pip install -r requirements.txt

Usage:

Run the monitor with:

python security_check.py

The program will collect the available system information and display it in the terminal.

Permissions:

Some system information may depend on the permissions available to the user running the program. Process, service, and network information may be limited on some Linux systems.

Platform:

This project is designed for Linux systems and relies on standard Linux command-line utilities.

Purpose:

The project was built to practice Python-based system interaction, Linux administration concepts, process and service monitoring, and terminal-based information presentation.

It also demonstrates how Python can interact with operating-system utilities to collect and organize system information.
