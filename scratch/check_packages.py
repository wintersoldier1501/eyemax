import subprocess
import sys

def check():
    print("Listing installed packages in the virtual environment...")
    res = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    print(res.stdout)

if __name__ == "__main__":
    check()
