import os
import glob
import json

def search_backups():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        print("APPDATA not found in environment")
        return
        
    vscode_history = os.path.join(appdata, "Code", "User", "History")
    print(f"Searching VS Code History at: {vscode_history}")
    
    if not os.path.exists(vscode_history):
        print("VS Code history directory does not exist")
        # Try finding anywhere in AppData/Local or Roaming
        return
        
    # Search for all entries in VS Code history
    # The structure is typically User/History/<random_folder>/entries.json containing original file paths
    # and files in that folder are the historical versions
    found_server = []
    found_index = []
    
    for root, dirs, files in os.walk(vscode_history):
        if "entries.json" in files:
            entries_path = os.path.join(root, "entries.json")
            try:
                with open(entries_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                resource = data.get("resource", "")
                if "server.py" in resource.lower():
                    # Find all historical files in this directory
                    for entry in data.get("entries", []):
                        id_val = entry.get("id")
                        timestamp = entry.get("timestamp")
                        hist_file = os.path.join(root, id_val)
                        if os.path.exists(hist_file):
                            found_server.append((timestamp, hist_file, os.path.getsize(hist_file)))
                elif "index.html" in resource.lower():
                    for entry in data.get("entries", []):
                        id_val = entry.get("id")
                        timestamp = entry.get("timestamp")
                        hist_file = os.path.join(root, id_val)
                        if os.path.exists(hist_file):
                            found_index.append((timestamp, hist_file, os.path.getsize(hist_file)))
            except Exception as e:
                pass

    print("\n--- Found server.py backups in VS Code History ---")
    # Sort by timestamp (which is epoch ms)
    found_server.sort()
    for ts, path, size in found_server:
        print(f"Timestamp: {ts}, Path: {path}, Size: {size} bytes")
        
    print("\n--- Found index.html backups in VS Code History ---")
    found_index.sort()
    for ts, path, size in found_index:
        print(f"Timestamp: {ts}, Path: {path}, Size: {size} bytes")

if __name__ == "__main__":
    search_backups()
