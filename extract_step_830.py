import json
import re

transcript_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            d = json.loads(line)
            if d.get("step_index") == 830:
                content = d.get("content", "")
                print(f"Step 830 type: {d.get('type')}, length: {len(content)}")
                # Clean the line prefixes
                clean_lines = []
                for l in content.splitlines():
                    match = re.match(r"^\s*\d+:\s*(.*)", l)
                    if match:
                        clean_lines.append(match.group(1))
                    else:
                        clean_lines.append(l)
                clean_code = "\n".join(clean_lines)
                with open("app_movil_step_830.py", "w", encoding="utf-8") as out:
                    out.write(clean_code)
                print("Written to app_movil_step_830.py")
        except Exception as e:
            print(f"Error: {e}")
