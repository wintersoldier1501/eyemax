import json
import os
import re

transcript_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"

if os.path.exists(transcript_path):
    with open(transcript_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            try:
                d = json.loads(line)
                content = d.get("content", "")
                if content and "async def main(page: ft.Page):" in content:
                    print(f"Index: {idx}, Step: {d.get('step_index')}, Type: {d.get('type')}, Length: {len(content)}")
                    # Clean the lines from log prefix
                    clean_lines = []
                    for l in content.splitlines():
                        match = re.match(r"^\s*\d+:\s*(.*)", l)
                        if match:
                            clean_lines.append(match.group(1))
                        else:
                            clean_lines.append(l)
                    clean_code = "\n".join(clean_lines)
                    with open(f"current_candidate_{d.get('step_index')}_{idx}.py", "w", encoding="utf-8") as out:
                        out.write(clean_code)
            except Exception as e:
                pass
else:
    print("Transcript not found")
