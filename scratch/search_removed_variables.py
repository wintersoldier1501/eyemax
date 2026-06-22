import re

def search_vars():
    removed_vars = [
        "catalogVerificationSection",
        "toggleCatalogPageBtn",
        "catalogPageAccordionContent",
        "accordionArrow",
        "catalogCropContainer",
        "catalogCropImg"
    ]
    
    with open("templates/index.html", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for var in removed_vars:
        print(f"\n--- References to '{var}' ---")
        for idx, line in enumerate(lines):
            # Check if variable is used (excluding its declaration lines, but actually let's just see all lines)
            if var in line:
                print(f"Line {idx+1}: {line.strip()}")

if __name__ == "__main__":
    search_vars()
