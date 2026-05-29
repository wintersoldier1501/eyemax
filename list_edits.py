import json
import os

transcript_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"

if os.path.exists(transcript_path):
    with open(transcript_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            try:
                d = json.loads(line)
                # Check for tool calls
                # In the transcript, tool calls are represented in some fields or content
                content = d.get("content", "")
                if "replace_file_content" in line or "multi_replace_file_content" in line:
                    if "app_movil.py" in line:
                        print(f"Step {d.get('step_index')}: {d.get('type')}")
                        # Print some snippet
                        print(content[:1000])
                        print("-" * 50)
            except Exception as e:
                pass
else:
    print("Transcript not found")
