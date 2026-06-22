import json
import os

def trace():
    log_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"
    if not os.path.exists(log_path):
        print("Log not found")
        return

    targets = set()
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                step = json.loads(line)
            except Exception:
                continue
            
            tool_calls = step.get("tool_calls", [])
            for call in tool_calls:
                args = call.get("args", {})
                target = args.get("TargetFile") or args.get("Target")
                if target and "server.py" in target.lower():
                    targets.add(target)

    for t in sorted(targets):
        print(t)

if __name__ == "__main__":
    trace()
