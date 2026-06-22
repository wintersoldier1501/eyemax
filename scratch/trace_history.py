import json
import os

def trace():
    log_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"
    if not os.path.exists(log_path):
        print("Log not found")
        return

    records = []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                step = json.loads(line)
            except Exception:
                continue
            
            step_idx = step.get("step_index")
            if step_idx is not None and step_idx >= 3828:
                continue

            tool_calls = step.get("tool_calls", [])
            for call in tool_calls:
                name = call.get("name")
                args = call.get("args", {})
                target = args.get("TargetFile") or args.get("Target")
                if not target:
                    continue
                target = target.replace("\\", "/").lower()
                if "templates/index.html" in target or "server.py" in target:
                    records.append({
                        "step": step_idx,
                        "file": "index.html" if "templates/index.html" in target else "server.py",
                        "tool": name,
                        "has_code_content": "CodeContent" in args,
                        "code_len": len(args.get("CodeContent", "")) if "CodeContent" in args else 0,
                    })

    for r in sorted(records, key=lambda x: (x["file"], x["step"])):
        print(f"File: {r['file']}, Step: {r['step']}, Tool: {r['tool']}, HasCodeContent: {r['has_code_content']}, Len: {r['code_len']}")

if __name__ == "__main__":
    trace()
