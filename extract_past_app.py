import json
import os

transcript_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\a80eaae8-eb2c-45da-b12a-b6c0d56bdd0a\.system_generated\logs\transcript.jsonl"

if os.path.exists(transcript_path):
    with open(transcript_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            try:
                d = json.loads(line)
                content = d.get("content", "")
                if content and "import flet" in content:
                    print(f"Index: {idx}, Step: {d.get('step_index')}, Type: {d.get('type')}, Length: {len(content)}")
                    # Write to file
                    with open(f"candidate_{idx}.py", "w", encoding="utf-8") as out:
                        out.write(content)
            except Exception as e:
                pass
else:
    print("Transcript not found")
