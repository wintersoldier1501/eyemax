def find_api_url():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if "API_URL" in line:
            print(f"Line {idx+1}: {line.strip()}")

if __name__ == "__main__":
    find_api_url()
