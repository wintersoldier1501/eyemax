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
                target_lower = target.replace("\\", "/").lower()
                if "templates/index.html" in target_lower or target_lower.endswith("/server.py") or target_lower == "server.py":
                    records.append({
                        "step": step_idx,
                        "file": target,
                        "tool": name,
                        "has_code_content": "CodeContent" in args,
                        "code_len": len(args.get("CodeContent", "")) if "CodeContent" in args else 0,
                    })

    for r in sorted(records, key=lambda x: (x["file"], x["step"])):
        print(f"Step: {r['step']}, File: {r['file']}, Tool: {r['tool']}, HasCode: {r['has_code_content']}, Len: {r['code_len']}")

if __name__ == "__main__":
    trace()
