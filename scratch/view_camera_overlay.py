def find():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if "camera-overlay" in line:
            print(f"Line {idx+1}: {line.strip()}")
            # Print next 5 lines
            for i in range(idx+1, min(len(lines), idx+6)):
                print(f"  Line {i+1}: {lines[i].strip()}")

if __name__ == "__main__":
    find()
