import os
import platform
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


def list_drives():
    """
    List all drives, works on Windows, Linux, and macOS.
    :return: List of drive letters or mount points.
    """
    if platform.system() == "Windows":
        import win32api
        import win32file

        drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
        return [drive for drive in drives if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE]
    elif platform.system() == "Linux":
        drives = [f"/dev/{device}" for device in os.listdir("/dev") if device.startswith("sd") and os.path.exists(f"/dev/{device}")]
        return drives
    elif platform.system() == "Darwin":  # macOS
        result = subprocess.run(["diskutil", "list"], stdout=subprocess.PIPE, text=True)
        drives = [line.split()[0] for line in result.stdout.splitlines() if line.startswith("/dev/disk")]
        return drives
    else:
        return []


def get_drive_size(drive_path):
    """
    Get the size of the target drive in GB.
    :param drive_path: Path to the drive (e.g., '/dev/sdb').
    :return: Size in GB or None on failure.
    """
    try:
        if platform.system() in ["Linux", "Darwin"]:
            result = subprocess.run(
                ["lsblk", "-b", "-d", "-o", "SIZE", "-n", drive_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                raise Exception(result.stderr.strip())
            size_bytes = int(result.stdout.strip())
            return size_bytes / (1024 ** 3)  # Convert to GB
        elif platform.system() == "Windows":
            import ctypes
            free_bytes = ctypes.c_ulonglong()
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(drive_path), None, ctypes.byref(free_bytes), None
            )
            return free_bytes.value / (1024 ** 3)
        else:
            raise Exception("Unsupported platform")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get drive size: {e}")
        return None


def clear_drive(drive_path):
    """
    Clear the partition table of the target drive.
    :param drive_path: Path to the drive (e.g., '/dev/sdb').
    """
    try:
        if platform.system() in ["Linux", "Darwin"]:
            command = f"sudo dd if=/dev/zero of={drive_path} bs=1M count=10 conv=fsync && sync"
        elif platform.system() == "Windows":
            # Assuming drive letter like D:
            drive_letter = drive_path.strip(':')
            script_content = f"select disk {drive_letter}\nclean"
            script_path = "diskpart_script.txt"
            with open(script_path, "w") as script_file:
                script_file.write(script_content)
            command = f"diskpart /s {script_path}"
        else:
            raise Exception("Unsupported platform")

        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to clear drive: {e}")
        raise


def write_iso_to_usb(iso_path, drive_path, on_complete, update_status):
    """
    Write an ISO file to a USB drive in a separate thread.
    :param iso_path: Path to the ISO file.
    :param drive_path: Path to the USB drive.
    :param on_complete: Callback function to handle completion.
    :param update_status: Callback to update UI with status messages.
    """
    try:
        update_status("Clearing the drive...")
        clear_drive(drive_path)

        update_status("Writing ISO to USB...")

        if platform.system() == "Windows":
            command = f"powershell -Command \"Copy-Item -Path '{iso_path}' -Destination '{drive_path}' -Recurse\""
        elif platform.system() in ["Linux", "Darwin"]:
            command = f"sudo dd if={iso_path} of={drive_path} bs=4M status=progress conv=fsync && sync"
        else:
            raise Exception("Unsupported platform")

        subprocess.run(command, shell=True, check=True)
        update_status("Bootable USB created successfully!")
        on_complete(success=True, message="Bootable USB created successfully!")
    except subprocess.CalledProcessError as e:
        update_status(f"Error: {e}")
        on_complete(success=False, message=f"Failed to create bootable USB: {e}")
    except Exception as e:
        update_status(f"Error: {e}")
        on_complete(success=False, message=f"Error: {e}")


def on_write_iso():
    iso_path = iso_entry.get()
    drive_path = drive_combo.get()

    if not iso_path:
        messagebox.showerror("Error", "No ISO file selected.")
        return
    if not drive_path:
        messagebox.showerror("Error", "No drive selected.")
        return

    try:
        iso_size = os.path.getsize(iso_path) / (1024 ** 3)  # Convert to GB
        drive_size = get_drive_size(drive_path)

        if drive_size is None:
            messagebox.showerror("Error", "Could not determine the size of the USB drive.")
            return

        if drive_size < iso_size:
            messagebox.showerror("Error", f"The selected USB drive ({drive_size:.2f} GB) is too small for the ISO file ({iso_size:.2f} GB).")
            return

        confirm = messagebox.askyesno(
            "Confirm",
            f"Are you sure you want to write the ISO to {drive_path}? This will erase all data on the drive!"
        )

        if confirm:
            write_btn.config(state=tk.DISABLED)
            status_label.config(text="Writing ISO... Please wait.")

            def update_status(message):
                status_label.config(text=message)

            def on_complete(success, message):
                write_btn.config(state=tk.NORMAL)
                if success:
                    messagebox.showinfo("Success", message)
                else:
                    messagebox.showerror("Error", message)

            threading.Thread(target=write_iso_to_usb, args=(iso_path, drive_path, on_complete, update_status), daemon=True).start()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# GUI Setup
root = tk.Tk()
root.title("Drive Flash Tool")
root.geometry("800x400")

# Styles
button_style = {"font": ("Helvetica", 12), "bg": "#4CAF50", "fg": "white"}
label_style = {"font": ("Helvetica", 12)}

# Drive Selection
drive_label = tk.Label(root, text="Select Drive:", **label_style)
drive_label.pack(pady=5)

drive_combo = ttk.Combobox(root, values=list_drives(), state="readonly")
drive_combo.pack(pady=5)

drive_combo.bind("<<ComboboxSelected>>", lambda event: drive_combo.set(drive_combo.get()))

# ISO Selection
iso_label = tk.Label(root, text="Select ISO File:", **label_style)
iso_label.pack(pady=5)

iso_entry = tk.Entry(root, width=50)
iso_entry.pack(pady=5)

browse_iso_btn = tk.Button(root, text="Browse", **button_style, command=lambda: iso_entry.insert(0, filedialog.askopenfilename()))
browse_iso_btn.pack(pady=5)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

write_btn = tk.Button(button_frame, text="Write ISO", command=on_write_iso, **button_style)
write_btn.pack(side="left", padx=10)

status_label = tk.Label(root, text="", **label_style)
status_label.pack(pady=10)

root.mainloop()