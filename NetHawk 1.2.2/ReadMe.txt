# NetHawk 1.2.2

NetHawk is a simple Windows network connection monitor written in Python.

It watches active TCP and UDP connections in real time, detects when new connections open or close, displays live statistics, and logs changes to a file.

## Features

- Live monitoring of TCP and UDP connections
- Detects new and closed connections
- Shows connection details (local address, remote address, state, PID)
- TCP / UDP statistics
- Timestamped logging to `nethawk_log.txt`
- Clean baseline on startup (avoids false "new connection" spam)
- Easy to stop with Ctrl + C

## Requirements

- Windows
- Python 3
- No external libraries required (uses only the Python standard library)

## How to Run

1. Download or clone this repository
2. Open a terminal in the project folder
3. Run:

```bash
python NetHawk.py