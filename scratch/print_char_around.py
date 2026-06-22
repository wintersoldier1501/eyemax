with open("scratch/step_3914_details.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Find the ReplacementChunks field value
start_idx = text.find('"ReplacementChunks":')
if start_idx != -1:
    sub = text[start_idx:start_idx+3000]
    print("Length of substring:", len(sub))
    print("Substring around character 2042:")
    print(sub[1900:2200])
else:
    print("ReplacementChunks key not found")
