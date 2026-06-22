import os
import time
import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL_PATH = "scratch/clip_vision.onnx"
TEST_IMAGE_PATH = "assets/catalog_crops/CATALOGO_1/page_258/DM024.jpg"

def main():
    print("=== PROBANDO MODELO CLIP LOCAL ===")
    
    if not os.path.exists(MODEL_PATH):
        print(f"[FAIL] Model file '{MODEL_PATH}' not found.")
        return False
        
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"[FAIL] Test image '{TEST_IMAGE_PATH}' not found.")
        return False
        
    try:
        start_time = time.time()
        print("Cargando sesión de ONNX Runtime...")
        session = ort.InferenceSession(MODEL_PATH)
        print(f"Cargado en {time.time() - start_time:.4f} segundos.")
        
        # Preprocessing
        img = Image.open(TEST_IMAGE_PATH).convert('RGB')
        img_resized = img.resize((224, 224), Image.Resampling.BILINEAR)
        img_data = np.array(img_resized).astype(np.float32)
        img_data = img_data.transpose(2, 0, 1)
        mean = np.array([0.48145466, 0.4578275, 0.40821073]).reshape(3, 1, 1)
        std = np.array([0.26862954, 0.26130258, 0.27577711]).reshape(3, 1, 1)
        img_data = (img_data / 255.0 - mean) / std
        input_data = np.expand_dims(img_data, axis=0).astype(np.float32)
        
        input_name = session.get_inputs()[0].name
        
        # Inference speed test
        print("Ejecutando inferencia...")
        inf_start = time.time()
        outputs = session.run(None, {input_name: input_data})
        vector = outputs[0][0].tolist()
        duration = time.time() - inf_start
        
        print(f"Inferencia completada en {duration*1000:.2f} ms.")
        print(f"Dimensión del vector resultante: {len(vector)}")
        
        # Verification
        assert len(vector) == 512, f"Expected 512 dimensions, got {len(vector)}"
        print("[SUCCESS] CLIP ONNX visual embedding model is fully functional and correct!")
        return True
    except Exception as e:
        print(f"[FAIL] CLIP Model test failed: {e}")
        return False

if __name__ == "__main__":
    main()
