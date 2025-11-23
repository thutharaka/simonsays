import subprocess
import os

import analyzer.options as options

def scrot() -> str:
    os.makedirs(options.DEFAULT_CACHE_DIR, exist_ok=True)
    filename = options.DEFAULT_SCROT_FILE
    try:
        subprocess.run(['scrot', '-o', filename], check=True)
        print("Screenshot successful")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
    return filename
