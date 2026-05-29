import json
import os

transcript_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\a80eaae8-eb2c-45da-b12a-b6c0d56bdd0a\.system_generated\logs\transcript.jsonl"

if os.path.exists(transcript_path):
    with open(transcript_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            try:
                d = json.loads(line)
                content = d.get("content", "")
                if "write_to_file" in line and "app_movil.py" in line:
                    print(f"Write in step {d.get('step_index')}: length {len(content)}")
                    with open(f"past_write_{d.get('step_index')}_{idx}.py", "w", encoding="utf-8") as out:
                        out.write(content)
            except Exception as e:
                pass
else:
    print("Transcript not found")
