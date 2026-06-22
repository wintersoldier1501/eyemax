import os
import sys
import numpy as np
from PIL import Image

# Add root directory to sys.path so we can import from server
sys.path.append(os.getcwd())

from server import extract_image_vector, cosine_similarity, initialize_onnx_model

def run_tests():
    print("=== TESTING VECTOR SIMILAIRITY PIPELINE ===")
    
    # 1. Initialize ONNX session
    try:
        initialize_onnx_model()
        print("[SUCCESS] ONNX model initialized.")
    except Exception as e:
        print(f"[FAIL] ONNX model initialization failed: {e}")
        return False
        
    # 2. Test Image Processing and Embedding Extraction
    test_img_path = "assets/logo.png"
    if not os.path.exists(test_img_path):
        # Create a dummy image if logo doesn't exist
        print(f"Creating dummy image at '{test_img_path}' for testing...")
        os.makedirs("assets", exist_ok=True)
        img = Image.new('RGB', (200, 200), color=(128, 0, 128))
        img.save(test_img_path)
        
    try:
        with open(test_img_path, 'rb') as f:
            img_bytes = f.read()
            
        vector1 = extract_image_vector(img_bytes)
        if vector1 is None:
            print("[FAIL] extract_image_vector returned None.")
            return False
            
        print(f"[SUCCESS] Extracted vector. Dimension: {len(vector1)}")
        
        # Verify length
        assert len(vector1) == 1000, f"Expected 1000 dimensions, got {len(vector1)}"
        
        # Extract again to verify deterministic output
        vector2 = extract_image_vector(img_bytes)
        sim_identical = cosine_similarity(vector1, vector2)
        print(f"Similarity with identical image: {sim_identical:.6f}")
        assert abs(sim_identical - 1.0) < 1e-5, f"Expected similarity to be 1.0, got {sim_identical}"
        print("[SUCCESS] Identical image matches with similarity 1.0.")
        
        # Test with a modified image
        img = Image.open(test_img_path).convert('RGB')
        # Add a tiny bit of noise / change color
        img_noise = Image.new('RGB', img.size, color=(130, 2, 126))
        img_blended = Image.blend(img, img_noise, 0.1)
        
        import io
        buf = io.BytesIO()
        img_blended.save(buf, format='JPEG')
        img_blended_bytes = buf.getvalue()
        
        vector_blended = extract_image_vector(img_blended_bytes)
        sim_blended = cosine_similarity(vector1, vector_blended)
        print(f"Similarity with slightly modified image: {sim_blended:.6f}")
        assert sim_blended > 0.85, f"Expected similarity to be high (e.g. >0.85) for slightly modified image, got {sim_blended}"
        print("[SUCCESS] Slightly modified image yields expected high similarity.")
        
        # Test with a completely different image
        different_img = Image.new('RGB', (200, 200), color=(255, 255, 255))
        buf_diff = io.BytesIO()
        different_img.save(buf_diff, format='JPEG')
        different_bytes = buf_diff.getvalue()
        
        vector_diff = extract_image_vector(different_bytes)
        sim_diff = cosine_similarity(vector1, vector_diff)
        print(f"Similarity with completely different image: {sim_diff:.6f}")
        assert sim_diff < 0.80, f"Expected low similarity for completely different image, got {sim_diff}"
        print("[SUCCESS] Completely different image yields low similarity.")
        
    except Exception as e:
        print(f"[FAIL] Error during vector similarity test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    print("=== ALL TESTS PASSED SUCCESSFULLY ===")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
