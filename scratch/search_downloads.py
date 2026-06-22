import os

def search_downloads():
    downloads = r"c:\Users\Accesorizate1\Downloads"
    print(f"Searching for server.py and index.html in: {downloads}")
    
    for root, dirs, files in os.walk(downloads):
        # Skip .venv or node_modules to avoid deep search
        if ".venv" in root or "node_modules" in root or ".git" in root:
            continue
        for file in files:
            if file in ["server.py", "index.html"]:
                path = os.path.join(root, file)
                try:
                    size = os.path.getsize(path)
                    print(f"Found {file}: {path} ({size} bytes)")
                except Exception as e:
                    pass

if __name__ == "__main__":
    search_downloads()
