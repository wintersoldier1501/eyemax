import json
import os

def trace():
    log_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"
    if not os.path.exists(log_path):
        print("Log not found")
        return

    steps_to_inspect = {3121, 3262, 3297, 3375, 3764}
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                step = json.loads(line)
            except Exception:
                continue
            
            step_idx = step.get("step_index")
            if step_idx in steps_to_inspect:
                print(f"\n--- STEP {step_idx} ---")
                tool_calls = step.get("tool_calls", [])
                for call in tool_calls:
                    print(f"Tool: {call.get('name')}")
                    args = call.get('args', {})
                    print(f"TargetFile: {args.get('TargetFile') or args.get('Target')}")
                    if "CodeContent" in args:
                        content = args["CodeContent"]
                        print(f"CodeContent Length: {len(content)}")
                        print("First 100 chars:")
                        print(repr(content[:100]))
                        print("Last 100 chars:")
                        print(repr(content[-100:]))
                    else:
                        print("No CodeContent in args")

if __name__ == "__main__":
    trace()
