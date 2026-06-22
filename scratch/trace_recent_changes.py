import json
import os

def trace_recent():
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
                if not target:
                    continue
                target_lower = target.replace("\\", "/").lower()
                if "templates/index.html" in target_lower or "server.py" in target_lower:
                    print(f"\n==================================================")
                    print(f"STEP {step_idx}: {name} on {target}")
                    print(f"Description: {args.get('Description')}")
                    print(f"Instruction: {args.get('Instruction')}")
                    
                    if name == "replace_file_content":
                        print("--- replace_file_content ---")
                        print(f"StartLine: {args.get('StartLine')}, EndLine: {args.get('EndLine')}")
                        print(f"TargetContent:\n{args.get('TargetContent')}")
                        print(f"ReplacementContent:\n{args.get('ReplacementContent')}")
                        
                    elif name == "multi_replace_file_content":
                        print("--- multi_replace_file_content ---")
                        chunks = args.get("ReplacementChunks", [])
                        if isinstance(chunks, str):
                            try:
                                chunks = json.loads(chunks)
                            except Exception:
                                pass
                        
                        if isinstance(chunks, list):
                            for idx, chunk in enumerate(chunks):
                                if isinstance(chunk, str):
                                    try:
                                        chunk = json.loads(chunk)
                                    except Exception:
                                        pass
                                if isinstance(chunk, dict):
                                    print(f"Chunk {idx+1}: lines [{chunk.get('StartLine')}, {chunk.get('EndLine')}]")
                                    print(f"  TargetContent:\n{chunk.get('TargetContent')}")
                                    print(f"  ReplacementContent:\n{chunk.get('ReplacementContent')}")
                                else:
                                    print(f"Chunk {idx+1} (not a dict): {repr(chunk)}")
                        else:
                            print(f"Chunks is not a list: {repr(chunks)}")
                            
                    elif name == "write_to_file":
                        print("--- write_to_file ---")
                        print(f"Content Length: {len(args.get('CodeContent', ''))}")
                        print(args.get('CodeContent')[:500])

if __name__ == "__main__":
    trace_recent()
