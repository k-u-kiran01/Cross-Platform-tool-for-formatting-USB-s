# Building a Cross-Platform Tool for Formatting Drives and Creating Bootable Linux USBs

## Overview
This project is a Python-based cross-platform tool designed to simplify the process of formatting drives and creating bootable Linux USBs. With a user-friendly GUI, it allows users to select drives, clear their partitions, and write ISO files for creating bootable USBs. It supports **Windows**, **Linux**, and **macOS**.

## Features
- **Cross-Platform Support**: Works seamlessly on Windows, Linux, and macOS.
- **Drive Detection**: Automatically lists available drives based on the operating system.
- **Drive Formatting**: Clears the partition table of the selected drive before writing the ISO.
- **Bootable USB Creation**: Writes ISO images to USB drives using platform-specific methods.
- **User-Friendly GUI**: Built using `Tkinter`, offering a simple and intuitive interface.
- **Threaded Operations**: Ensures the GUI remains responsive during long-running tasks.

## Prerequisites
### Windows
- Python 3.8 or later
- `pywin32` library (`pip install pywin32`)

### Linux/macOS
- Python 3.8 or later
- `dd` and `lsblk` (Linux only) utilities pre-installed
- `sudo` privileges for clearing and writing to drives

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/usb-tool.git
   cd usb-tool
2.Install required Python dependencies:
  pip install pywin32

Usage
Run the script:
bash
Copy
Edit
python drive_flash_tool.py
Use the GUI to:
Select a drive from the dropdown menu.
Choose an ISO file via the file browser.
Click Write ISO to begin the process.

      Key Functionality
Drive Detection
The tool identifies available drives based on the operating system:

Windows: Uses win32api to detect removable drives.
Linux: Scans /dev for block devices matching sd*.
macOS: Uses diskutil to list drives.
Drive Formatting
Before writing the ISO, the tool clears the partition table of the selected drive:

Linux/macOS: Utilizes the dd command to zero out the first few MB of the drive.
Windows: Uses diskpart with a script to clear the drive.
  ISO Writing
Linux/macOS: Writes ISO using the dd command.
Windows: Uses PowerShell to copy ISO content to the drive.

  Creating a Bootable USB
Select the desired USB drive from the dropdown.
Browse for the Linux ISO file you want to use.
Confirm your selection and click Write ISO.
Wait for the process to complete. The tool will notify you upon success.
  Known Limitations
Requires administrator privileges for certain operations (e.g., clearing drives, writing ISO).
ISO writing methods may vary slightly depending on the Linux distribution.

Disclaimer
Warning: This tool will erase all data on the selected USB drive. Use with caution and double-check your selections before proceeding.

