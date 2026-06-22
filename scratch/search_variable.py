with open("templates/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(x in line for x in ["catalogCropContainer", "catalogCropImg", "toggleCatalogPageBtn", "catalogPageAccordionContent", "accordionArrow"]):
        cleaned = line.encode('ascii', errors='ignore').decode('ascii').strip()
        print(f"Line {i+1}: {cleaned}")
