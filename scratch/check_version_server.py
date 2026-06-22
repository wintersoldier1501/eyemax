with open(r"c:\Users\Accesorizate1\Downloads\versiones\server.py", "r", encoding="utf-8") as f:
    code = f.read()

print("File size:", len(code), "bytes")
print("Number of lines:", len(code.splitlines()))

# Search for keywords
keywords = ["crop", "recorte", "mask", "mascara", "box", "300", "5161"]
for kw in keywords:
    count = code.lower().count(kw)
    print(f"Keyword '{kw}' count: {count}")

# Print first 20 lines
print("\n--- FIRST 20 LINES ---")
print("\n".join(code.splitlines()[:20]))

# Print last 20 lines
print("\n--- LAST 20 LINES ---")
print("\n".join(code.splitlines()[-20:]))
