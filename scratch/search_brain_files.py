import os

def search_brain():
    brain_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\a80eaae8-eb2c-45da-b12a-b6c0d56bdd0a"
    print(f"Searching in: {brain_path}")
    
    for root, dirs, files in os.walk(brain_path):
        for file in files:
            if file in ["server.py", "index.html"] or "server" in file.lower() or "index" in file.lower():
                path = os.path.join(root, file)
                try:
                    size = os.path.getsize(path)
                    print(f"Found: {path} ({size} bytes)")
                except Exception as e:
                    pass

if __name__ == "__main__":
    search_brain()
