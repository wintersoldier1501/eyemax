import re

def search_in_file(filepath, keywords):
    print(f"\n=== Searching in {filepath} ===")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            line_num = idx + 1
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', line, re.IGNORECASE):
                    print(f"Line {line_num} (keyword '{kw}'): {line.strip()}")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

if __name__ == "__main__":
    kws = ["crop", "recorte", "mask", "mascara", "box", "box_coords", "recortada", "rango", "pin"]
    search_in_file("server.py", kws)
    search_in_file("templates/index.html", kws)
