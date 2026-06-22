import json
import os

def search_views():
    log_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"
    if not os.path.exists(log_path):
        print("Log not found")
        return

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                step = json.loads(line)
            except Exception:
                continue
            
            step_idx = step.get("step_index")
            if step_idx is not None and step_idx >= 3828:
                continue
                
            # Check tool_calls or type == "VIEW_FILE" / content
            content = step.get("content", "")
            # Look for lines like "File Path: `file:///c:/Users/Accesorizate1/Downloads/Eyemax/...`"
            if "File Path:" in content and "Downloads/Eyemax" in content:
                # Get the filename
                filename = ""
                if "templates/index.html" in content:
                    filename = "index.html"
                elif "server.py" in content:
                    filename = "server.py"
                
                if filename:
                    print(f"Step {step_idx}: View of {filename}")
                    # Print line count and range if shown
                    for l in content.splitlines()[:10]:
                        if "Total Lines:" in l or "Showing lines" in l:
                            print(f"  {l}")

if __name__ == "__main__":
    search_views()
