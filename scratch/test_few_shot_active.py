import json
import os
import sys
import httpx
from PIL import Image
import io
import shutil

sys.path.append(os.getcwd())
from server import extract_image_vector

def main():
    print("=== TESTING ACTIVE DYNAMIC FEW-SHOT RETRIEVAL ===")
    
    history_file = "historial_entrenamiento.json"
    backup_file = "historial_entrenamiento.json.bak"
    
    # 1. Back up history
    if os.path.exists(history_file):
        shutil.copy(history_file, backup_file)
        
    try:
        # Load current history
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
            
        # 2. Get CLIP vector for AX010P (silver stars earrings)
        silver_crop = "assets/catalog_crops/CATALOGO_1/page_109/AX010P.jpg"
        if not os.path.exists(silver_crop):
            print(f"[FAIL] Silver crop '{silver_crop}' not found.")
            return
            
        with open(silver_crop, 'rb') as f:
            silver_bytes = f.read()
            
        silver_vec = extract_image_vector(silver_bytes)
        if not silver_vec:
            print("[FAIL] Failed to extract vector for silver crop.")
            return
            
        # Add temporary item to history
        temp_item = {
            "image_path": silver_crop,
            "codigo": "AX010P",
            "descripcion_visual": "ARETES - STUD TRES ESTRELLAS PLATA AX010P",
            "vector_embeddings": silver_vec
        }
        history.append(temp_item)
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print("Temporarily added AX010P to training history.")
        
        # 3. Query with slightly altered AX010G (gold stars earrings)
        gold_crop = "assets/catalog_crops/CATALOGO_1/page_109/AX010G.jpg"
        img = Image.open(gold_crop)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        altered_bytes = buf.getvalue()
        
        url = "http://192.168.100.78:8080/api/recognize"
        files = {"image": ("query_stars.jpg", altered_bytes, "image/jpeg")}
        
        print("Sending query to /api/recognize...")
        response = httpx.post(url, files=files, timeout=60.0)
        print(f"Server response code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
    finally:
        # Restore backup
        if os.path.exists(backup_file):
            shutil.copy(backup_file, history_file)
            os.remove(backup_file)
            print("Restored training history backup.")
            
if __name__ == "__main__":
    main()
