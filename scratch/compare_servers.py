import difflib

def compare():
    with open(r"c:\Users\Accesorizate1\Downloads\versiones\server.py", "r", encoding="utf-8") as f:
        old_lines = f.readlines()
    with open("server.py", "r", encoding="utf-8") as f:
        new_lines = f.readlines()
        
    diff = list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile="versiones/server.py",
        tofile="server.py",
        n=2
    ))
    
    print(f"Total diff lines: {len(diff)}")
    
    # Save the diff to scratch/server_diff.txt
    with open("scratch/server_diff.txt", "w", encoding="utf-8") as out:
        out.writelines(diff)
    print("Unified diff saved to scratch/server_diff.txt")

if __name__ == "__main__":
    compare()
