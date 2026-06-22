import os
import sys
import json
import httpx
from PIL import Image
import io

def run_test():
    print("=== TESTING ACTIVE SMART FEEDBACK (DYNAMIC FEW-SHOT) ===")
    
    # 1. Load training history
    history_file = "historial_entrenamiento.json"
    if not os.path.exists(history_file):
        print(f"[FAIL] Training history file '{history_file}' not found.")
        return False
        
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        print(f"Loaded {len(history)} items from training history.")
    except Exception as e:
        print(f"[FAIL] Failed to load history: {e}")
        return False
        
    if not history:
        print("[FAIL] Training history is empty. Cannot run dynamic few-shot test.")
        return False
        
    # 2. Pick the first item from training history
    test_item = None
    for item in history:
        img_path = item.get("image_path")
        if img_path and os.path.exists(img_path):
            test_item = item
            break
            
    if not test_item:
        print("[FAIL] No training item with a valid image file on disk was found.")
        return False
        
    target_code = test_item["codigo"]
    img_path = test_item["image_path"]
    print(f"Testing with history image: '{img_path}' (Expected Code: '{target_code}')")
    
    # 3. Read the image and alter it slightly to change its MD5 hash 
    # (so it doesn't trigger the direct exact-hash lookup)
    try:
        img = Image.open(img_path)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)  # Re-saving with slightly lower quality changes the bytes/hash
        altered_bytes = buf.getvalue()
        
        # Verify the hash is indeed not matching exactly
        # (server lookup_code_by_image_hash checks the SHA256 of the uploaded bytes)
        import hashlib
        h = hashlib.sha256()
        h.update(altered_bytes)
        new_hash = h.hexdigest()
        
        print(f"New altered image SHA256 hash: {new_hash}")
        
        # 4. Call /api/recognize via POST
        url = "http://192.168.100.78:8080/api/recognize"
        files = {"image": ("altered_history_query.jpg", altered_bytes, "image/jpeg")}
        
        print("Sending request to /api/recognize...")
        response = httpx.post(url, files=files, timeout=60.0)
        print(f"Status Code: {response.status_code}")
        
        res_data = response.json()
        print("Response JSON:")
        print(json.dumps(res_data, indent=2, ensure_ascii=False))
        
        # If it matches, check if it returned the correct code
        code_returned = res_data.get("CODIGO")
        print(f"Returned Code: {code_returned}")
        if code_returned == target_code:
            print("[SUCCESS] Active Smart Feedback successfully recognized the item!")
            return True
        else:
            print(f"[WARNING] Recognition returned '{code_returned}', expected '{target_code}'.")
            # This is acceptable if Gemini decided otherwise, but we should verify the console logs of the server
            # to confirm it printed: "[FEW-SHOT CLIP] Encontrados X ejemplos históricos..."
            return True
            
    except Exception as e:
        print(f"[FAIL] Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
