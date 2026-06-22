import json
import os

def trace_all_recent():
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
            if step_idx is None or step_idx < 3828:
                continue

            tool_calls = step.get("tool_calls", [])
            for call in tool_calls:
                name = call.get("name")
                if name not in ["replace_file_content", "multi_replace_file_content", "write_to_file"]:
                    continue
                args = call.get("args", {})
                target = args.get("TargetFile") or args.get("Target")
                if target:
                    print(f"Step {step_idx}: {name} -> {target}")

if __name__ == "__main__":
    trace_all_recent()
