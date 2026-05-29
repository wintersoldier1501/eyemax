import os
import ssl
import urllib.request
import subprocess
import sys

# Monkey patch SSL to avoid certificate verification errors
ssl._create_default_https_context = ssl._create_unverified_context

url = "https://github.com/git-for-windows/git/releases/download/v2.45.0.windows.1/PortableGit-2.45.0-64-bit.7z.exe"
dest_dir = r"C:\Users\Accesorizate1\PortableGit"
exe_path = "PortableGit-2.45.0-64-bit.7z.exe"

print(f"Downloading Portable Git from: {url}...")
try:
    urllib.request.urlretrieve(url, exe_path)
    print("Download complete!")
except Exception as e:
    print(f"Error downloading: {e}")
    sys.exit(1)

print(f"Extracting Portable Git to: {dest_dir}...")
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

try:
    # Run the self-extracting archive silently
    cmd = [exe_path, "-y", f"-o{dest_dir}"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print("Extraction completed successfully!")
    else:
        print(f"Extraction failed with code {result.returncode}. Stderr: {result.stderr}")
except Exception as e:
    print(f"Error running extractor: {e}")

# Clean up installer exe
if os.path.exists(exe_path):
    try:
        os.remove(exe_path)
    except Exception as cleanup_err:
        print(f"Warning: could not delete temporary installer: {cleanup_err}")

# Check if git is available now
git_exe = os.path.join(dest_dir, "cmd", "git.exe")
if os.path.exists(git_exe):
    print(f"Git is successfully installed and available at: {git_exe}")
    
    # Test running git version
    try:
        git_ver = subprocess.run([git_exe, "--version"], capture_output=True, text=True)
        print(f"Git version: {git_ver.stdout.strip()}")
    except Exception as run_err:
        print(f"Error running git --version: {run_err}")
else:
    print(f"Error: Git executable not found at expected path: {git_exe}")
