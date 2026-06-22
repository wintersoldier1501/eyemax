import json
import sys

# Configure stdout to use utf-8
sys.stdout.reconfigure(encoding='utf-8')

def view_chunks():
    with open("scratch/step_3914_details.txt", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    chunks = data.get("ReplacementChunks", [])
    if isinstance(chunks, str):
        chunks = json.loads(chunks)
        
    print(f"Total chunks: {len(chunks)}")
    for idx, chunk in enumerate(chunks):
        print(f"\n--- CHUNK {idx+1} ---")
        print(f"Lines: [{chunk.get('StartLine')}, {chunk.get('EndLine')}]")
        print(f"TargetContent:\n{chunk.get('TargetContent')}")
        print(f"ReplacementContent:\n{chunk.get('ReplacementContent')}")

if __name__ == "__main__":
    view_chunks()
