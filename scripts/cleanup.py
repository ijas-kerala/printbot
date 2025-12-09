import os
import shutil
import time

UPLOAD_DIR = "/home/ijas/printbot1/uploads"
MAX_AGE_SECONDS = 3600 * 24 # 24 Hours

def cleanup():
    now = time.time()
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > MAX_AGE_SECONDS:
                print(f"Deleting old file: {filename}")
                os.remove(file_path)

if __name__ == "__main__":
    cleanup()
