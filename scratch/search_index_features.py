import sys

# Configure stdout to use utf-8
sys.stdout.reconfigure(encoding='utf-8')

def search():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        code = f.read()
    
    # Search for keywords and print surrounding lines
    lines = code.splitlines()
    
    keywords = ["accordion", "crop", "mask", "cutout", "catalogCrop", "toggleCatalog"]
    for kw in keywords:
        print(f"\n--- Occurrences of '{kw}' ---")
        found = 0
        for idx, line in enumerate(lines):
            if kw.lower() in line.lower():
                found += 1
                # Print 2 lines before and after
                start = max(0, idx - 3)
                end = min(len(lines), idx + 4)
                print(f"L{idx+1}:")
                for i in range(start, end):
                    marker = ">>" if i == idx else "  "
                    print(f"{marker} {i+1}: {lines[i]}")
                if found >= 15:
                    print("... too many occurrences, truncating search")
                    break

if __name__ == "__main__":
    search()
