import json
import os

def trace_index_edits():
    log_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"
    out_path = r"scratch/index_edits.txt"
    if not os.path.exists(log_path):
        print("Log not found")
        return

    steps_to_find = {3852, 3914, 3920, 3926, 3930, 3975}
    output_lines = []
    
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                step = json.loads(line)
            except Exception:
                continue
            
            step_idx = step.get("step_index")
            if step_idx not in steps_to_find:
                continue

            tool_calls = step.get("tool_calls", [])
            for call in tool_calls:
                name = call.get("name")
                if name not in ["replace_file_content", "multi_replace_file_content"]:
                    continue
                args = call.get("args", {})
                target = args.get("TargetFile") or args.get("Target")
                if not target or "index.html" not in target.lower():
                    continue
                
                output_lines.append(f"\n==================================================")
                output_lines.append(f"STEP {step_idx}: {name}")
                output_lines.append(f"Description: {args.get('Description')}")
                
                if name == "replace_file_content":
                    output_lines.append(f"Lines: [{args.get('StartLine')}, {args.get('EndLine')}]")
                    output_lines.append(f"TargetContent:\n{args.get('TargetContent')}")
                    output_lines.append(f"ReplacementContent:\n{args.get('ReplacementContent')}")
                elif name == "multi_replace_file_content":
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
                                output_lines.append(f"Chunk {idx+1}: lines [{chunk.get('StartLine')}, {chunk.get('EndLine')}]")
                                output_lines.append(f"  TargetContent:\n{chunk.get('TargetContent')}")
                                output_lines.append(f"  ReplacementContent:\n{chunk.get('ReplacementContent')}")
                            else:
                                output_lines.append(f"Chunk {idx+1} (not a dict): {repr(chunk)}")
                    else:
                        output_lines.append(f"Chunks is not a list (type {type(chunks)}): {repr(chunks)}")

    with open(out_path, "w", encoding="utf-8") as out:
        out.write("\n".join(output_lines))
    print(f"Successfully wrote index edits to {out_path}")

if __name__ == "__main__":
    trace_index_edits()
