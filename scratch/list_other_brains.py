import os

def list_brains():
    brain_parent = r"C:\Users\Accesorizate1\.gemini\antigravity\brain"
    if not os.path.exists(brain_parent):
        print("Brain parent not found")
        return
    for item in os.listdir(brain_parent):
        path = os.path.join(brain_parent, item)
        if os.path.isdir(path):
            print(f"Conversation: {item} (modified: {os.path.getmtime(path)})")

if __name__ == "__main__":
    list_brains()
