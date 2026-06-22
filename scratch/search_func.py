with open("server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for idx, line in enumerate(lines):
    if "def get_product_by_code" in line:
        print(f"Line {idx+1}: {line.strip()}")
        # print next 30 lines
        for i in range(idx+1, min(len(lines), idx+35)):
            print(f"  Line {i+1}: {lines[i].strip()}")
