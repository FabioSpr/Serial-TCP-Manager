# **Serial TCP Manager**


## Description

A server‑side executable that enables a client within the same LAN to send messages over TCP/IP to a serial device connected to the server’s PC.

At present, the executable is supported **exclusively on Windows Server**.


## Quick Start

**Prerequisites:** Python (>= 3.6) is installed

Create a new Virtual Environment using the `requirements.txt` file provided in this repository:

### Step 1: Create a virtual environment

Use the desired Python version to create a virtual environment:

```bash
python -m venv my_venv
```

This creates a `my_venv` directory containing the virtual environment

### Step 2: Activate the Virtual Environment

Activate the environment:

- Windows (command prompt):

```bash
my_env\Scripts\activate.bat
```

- Windows (PowerShell):

```bash
\my_env\Scripts\Activate.ps1
```

### Step 3: Install Requirements
Once the environment is activated, verify the Python version inside and install the package list:

```bash
python --version
pip install -r requirements.txt
```


## Examples

With the configuration already provided inside the source files, you can directly connect to a COM port (specified as input) with a baudrate of **115200**, with all the other default parameters specified inside python `Serial` library.


## Contributing

This project is currently a solo-developed project.
You're welcome to contribute by:

- 🐛 Filling [Issues](https://github.com/FabioSpr/Serial-TCP-Manager/issues) — report bugs
- 💡 Filling [Issues](https://github.com/FabioSpr/Serial-TCP-Manager/issues) — propose new features