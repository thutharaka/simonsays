import subprocess
import options
import os

UIED_PATH = os.getenv("UIED_PATH")
if not UIED_PATH:
    UIED_PATH = options.UIED_DEFAULT_PATH

def invoke_UIED(scrot_path: str):
    try:
        result = subprocess.run(
            ["python", f"{UIED_PATH}/run_single.py", scrot_path,
             options.DEFAULT_CACHE_DIR],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"UIED failed with error code {e.returncode}")
        print(f"Stderr:\n{e.stderr}")
