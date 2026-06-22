import json
import os

def trace():
    log_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"
    if not os.path.exists(log_path):
        print("Log not found")
        return

    steps = {3644, 3646}
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                step = json.loads(line)
            except Exception:
                continue
            
            step_idx = step.get("step_index")
            if step_idx in steps:
                print(f"Step {step_idx}:")
                # Look at keys
                print("  Keys:", list(step.keys()))
                # Look at content length
                content = step.get("content", "")
                print(f"  Content length: {len(content)}")
                print(f"  First 100 chars:\n{repr(content[:100])}")
                print(f"  Last 100 chars:\n{repr(content[-100:])}")

if __name__ == "__main__":
    trace()
