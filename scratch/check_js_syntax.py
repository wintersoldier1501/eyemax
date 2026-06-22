import re
import subprocess
import sys

def check_syntax():
    html_path = "templates/index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Extraer el contenido del bloque <script>
    # Usamos una expresión regular floja que capture el contenido de <script> ... </script>
    script_match = re.search(r"<script>(.*?)</script>", html_content, re.DOTALL)
    if not script_match:
        print("No se encontró ningún bloque <script> en index.html")
        return

    script_content = script_match.group(1)
    
    # Escribir el script en un archivo temporal
    temp_js_path = "scratch/temp_check.js"
    with open(temp_js_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    print("Corriendo 'node --check scratch/temp_check.js'...")
    res = subprocess.run(["node", "--check", temp_js_path], capture_output=True, text=True)
    if res.returncode == 0:
        print("SUCCESS: El codigo JavaScript es sintacticamente VALIDO.")
    else:
        print("ERROR: Se encontro un error de sintaxis en el JavaScript:")
        print(res.stderr)
        sys.exit(1)

if __name__ == "__main__":
    check_syntax()
