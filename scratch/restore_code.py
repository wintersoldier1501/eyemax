import json
import os

def find_last_writes():
    log_path = r"C:\Users\Accesorizate1\.gemini\antigravity\brain\68abaf9f-2185-4f27-b214-4f2f7a8055de\.system_generated\logs\transcript.jsonl"
    if not os.path.exists(log_path):
        print(f"Log file not found at: {log_path}")
        return

    print("Reading log file...")
    last_index_html = None
    last_server_py = None
    
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                step = json.loads(line)
            except Exception:
                continue
            
            # Buscar llamadas a herramientas de escritura o reemplazo
            tool_calls = step.get("tool_calls", [])
            for call in tool_calls:
                name = call.get("name")
                args = call.get("args", {})
                target_file = args.get("TargetFile") or args.get("Target")
                if not target_file:
                    continue
                
                # Normalizar ruta
                target_file = target_file.replace("\\", "/").lower()
                step_idx = step.get("step_index")
                
                # Ignorar escrituras a partir del paso actual (este turno empezó después del paso 3828)
                if step_idx is not None and step_idx >= 3828:
                    continue
                
                if "templates/index.html" in target_file:
                    last_index_html = (step_idx, name, args)
                elif "server.py" in target_file:
                    last_server_py = (step_idx, name, args)

    print("\n--- Last index.html write before step 3828 ---")
    if last_index_html:
        print(f"Step: {last_index_html[0]}, Tool: {last_index_html[1]}")
        # Guardar en un archivo temporal de inspección
        with open("scratch/last_index_html_args.json", "w", encoding="utf-8") as out:
            json.dump(last_index_html[2], out, indent=2)
    else:
        print("None found")

    print("\n--- Last server.py write before step 3828 ---")
    if last_server_py:
        print(f"Step: {last_server_py[0]}, Tool: {last_server_py[1]}")
        with open("scratch/last_server_py_args.json", "w", encoding="utf-8") as out:
            json.dump(last_server_py[2], out, indent=2)
    else:
        print("None found")

if __name__ == "__main__":
    find_last_writes()
