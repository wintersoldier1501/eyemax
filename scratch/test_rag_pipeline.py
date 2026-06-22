import os
import sys
import json
import httpx
from PIL import Image
import io

# Add root directory to sys.path to import from server
sys.path.append(os.getcwd())

from server import extract_image_vector, cosine_similarity, load_catalog_vectors

def run_rag_test():
    print("=== TESTING MULTIMODAL RAG PIPELINE ===")
    
    # 1. Check if index JSON exists
    vectors_path = "catalogo_vectores.json"
    if not os.path.exists(vectors_path):
        print(f"[FAIL] Catalog vectors file '{vectors_path}' not found. Indexing may still be in progress.")
        return False
        
    try:
        with open(vectors_path, 'r', encoding='utf-8') as f:
            catalog_data = json.load(f)
        print(f"[SUCCESS] Loaded {len(catalog_data)} catalog items from {vectors_path}.")
    except Exception as e:
        print(f"[FAIL] Failed to load {vectors_path}: {e}")
        return False
        
    # 2. Pick a known item from catalog_data for testing
    if not catalog_data:
        print("[FAIL] Catalog vector list is empty.")
        return False
        
    test_item = None
    for item in catalog_data:
        # Find an item that has a valid crop path on disk
        crop_path = item.get('crop_path')
        if crop_path and os.path.exists(crop_path):
            test_item = item
            break
            
    if not test_item:
        print("[FAIL] Could not find any indexed item with a valid cropped image file on disk.")
        return False
        
    test_code = test_item['codigo']
    test_crop_path = test_item['crop_path']
    print(f"Using '{test_code}' (crop: '{test_crop_path}') as the test query item.")
    
    # 3. Read image, extract vector, and perform local search
    try:
        with open(test_crop_path, 'rb') as f:
            test_img_bytes = f.read()
            
        scanned_vector = extract_image_vector(test_img_bytes)
        if not scanned_vector:
            print("[FAIL] Failed to extract embedding vector for the test image.")
            return False
            
        print("[SUCCESS] Extracted query vector.")
        
        # Calculate similarities against all catalog items
        scores = []
        for item in catalog_data:
            item_vector = item.get('vector_embeddings')
            if item_vector:
                sim = cosine_similarity(scanned_vector, item_vector)
                scores.append((item['codigo'], sim, item.get('crop_path')))
                
        # Sort by similarity
        scores.sort(key=lambda x: x[1], reverse=True)
        print("\nTop 5 visual matches in catalog:")
        for i, (code, sim, path) in enumerate(scores[:5]):
            print(f" {i+1}. Code: {code} | Similarity: {sim*100:.2f}% | Path: {path}")
            
        # The best match should be the query itself with similarity ~1.0
        best_code, best_sim, _ = scores[0]
        assert best_code == test_code, f"Expected top match to be '{test_code}', got '{best_code}'"
        assert abs(best_sim - 1.0) < 1e-4, f"Expected similarity to be ~100%, got {best_sim*100:.2f}%"
        print(f"[SUCCESS] Semantic vector search accurately retrieved the correct catalog item.")
        
    except Exception as e:
        print(f"[FAIL] Local RAG search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    # 4. Test recognize API call to verify it runs via the RAG Pipeline
    # Create slightly altered bytes to bypass hash matching
    try:
        print("\nTesting recognize API endpoint via HTTP POST...")
        img = Image.open(test_crop_path)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=95)
        altered_bytes = buf.getvalue()
        
        url = "http://192.168.100.78:8080/api/recognize"
        files = {'image': ('altered_rag_query.jpg', altered_bytes, 'image/jpeg')}
        
        response = httpx.post(url, files=files, timeout=60.0)
        print(f"Response Status Code: {response.status_code}")
        
        res_data = response.json()
        print("Response JSON:")
        print(json.dumps(res_data, indent=2, ensure_ascii=False))
        
        # Verify result
        # Since it's a cropped catalog image matching itself visually, the similarity should be very high
        # and should match directly in server.py (or be selected correctly by Gemini from the crops)
        assert res_data.get('CODIGO') == test_code, f"Expected recognized code to be '{test_code}', got '{res_data.get('CODIGO')}'"
        print("\n=== ALL RAG PIPELINE TESTS PASSED ===")
        return True
    except Exception as e:
        print(f"\n[FAIL] API POST test failed: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Response text: {response.text}")
        return False

if __name__ == "__main__":
    success = run_rag_test()
    sys.exit(0 if success else 1)
