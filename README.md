# **Serial TCP Manager**


## Description

A server‑side executable that enables a client within the same LAN to send messages over TCP/IP to a serial device connected to the server’s PC.

At present, the executable is supported **exclusively on Windows Server**.


## Quick Start

**Prerequisites:** Python (>= 3.6) is installed

Before generating the executable, you must create a new Virtual Environment using the `requirements.txt` file provided in this repository:

### Step 1: Download Repository

Download the entire repository as zip.
Open command prompt and move to the download folder

### Step 2: Create a virtual environment

Use the desired Python version to create a virtual environment:

```bash
python -m venv my_venv
```

This creates a `my_venv` directory containing the virtual environment

### Step 3: Activate the Virtual Environment

Activate the environment:

- Windows (command prompt):

```bash
my_env\Scripts\activate.bat
```

- Windows (PowerShell):

```bash
\my_env\Scripts\Activate.ps1
```

### Step 4: Install Requirements
Once the environment is activated, verify the Python version inside and install the package list:

```bash
python --version
pip install -r requirements.txt
```

### Step 5: Create the Executable

Inside the download folder, with the environment activated, run the following command inside the command prompt:

```bash
pyinstaller --onefile --icon=tcp-ip.png serial_server_win.py
```

This will generate a new folder called `build` where you can find the .exe file


## Examples

With the configuration already provided inside the source files, you can directly connect to a COM port (specified as input) with a baudrate of **115200**, with all the other default parameters specified inside python `Serial` library.


## Contributing

This project is currently a solo-developed project.
You're welcome to contribute by:

- 🐛 Filling [Issues](https://github.com/FabioSpr/Serial-TCP-Manager/issues) — report bugs
- 💡 Filling [Issues](https://github.com/FabioSpr/Serial-TCP-Manager/issues) — propose new features
