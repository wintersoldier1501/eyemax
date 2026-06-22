import json
import os

def trace_step_3914():
    log_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"
    out_path = r"scratch/step_3914_details.txt"
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
            if step_idx != 3914:
                continue

            tool_calls = step.get("tool_calls", [])
            for call in tool_calls:
                name = call.get("name")
                if name != "multi_replace_file_content":
                    continue
                args = call.get("args", {})
                target = args.get("TargetFile") or args.get("Target")
                if target and "index.html" in target.lower():
                    # Dump the entire args to step_3914_details.txt
                    with open(out_path, "w", encoding="utf-8") as out:
                        json.dump(args, out, indent=2, ensure_ascii=False)
                    print(f"Successfully wrote Step 3914 args to {out_path}")
                    return

if __name__ == "__main__":
    trace_step_3914()
