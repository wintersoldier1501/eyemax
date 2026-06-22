import os
import json
import numpy as np
import onnxruntime as ort
from PIL import Image
import io
import time

VECTORS_INDEX_PATH = 'catalogo_vectores.json'
MODEL_PATH = "scratch/clip_vision.onnx"

def main():
    print("=== INICIANDO MIGRACIÓN DE VECTORES A CLIP ===")
    
    # 1. Load ONNX Session
    if not os.path.exists(MODEL_PATH):
        print(f"Error: No se encontró el modelo ONNX en '{MODEL_PATH}'. Descárgalo primero.")
        return
        
    print("Cargando sesión de ONNX Runtime para CLIP...")
    try:
        ort_session = ort.InferenceSession(MODEL_PATH)
        input_name = ort_session.get_inputs()[0].name
    except Exception as e:
        print(f"Error al cargar sesión de ONNX: {e}")
        return

    # Helper function to extract CLIP vector
    def extract_vector(image_bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_resized = img.resize((224, 224), Image.Resampling.BILINEAR)
        img_data = np.array(img_resized).astype(np.float32)
        img_data = img_data.transpose(2, 0, 1)
        mean = np.array([0.48145466, 0.4578275, 0.40821073]).reshape(3, 1, 1)
        std = np.array([0.26862954, 0.26130258, 0.27577711]).reshape(3, 1, 1)
        img_data = (img_data / 255.0 - mean) / std
        input_data = np.expand_dims(img_data, axis=0).astype(np.float32)
        outputs = ort_session.run(None, {input_name: input_data})
        return outputs[0][0].tolist()

    # 2. Load catalog index
    if not os.path.exists(VECTORS_INDEX_PATH):
        print(f"Error: No se encontró la base de datos de vectores '{VECTORS_INDEX_PATH}'.")
        return
        
    try:
        with open(VECTORS_INDEX_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Base de datos cargada. Total de registros a migrar: {len(data)}")
    except Exception as e:
        print(f"Error al cargar base de datos: {e}")
        return

    # 3. Processing loop
    migrated_count = 0
    missing_crops_count = 0
    start_time = time.time()
    
    for idx, item in enumerate(data):
        crop_path = item.get('crop_path')
        if not crop_path:
            # Try to build path if missing
            continue
            
        if not os.path.exists(crop_path):
            missing_crops_count += 1
            continue
            
        try:
            with open(crop_path, 'rb') as img_f:
                img_bytes = img_f.read()
            vector = extract_vector(img_bytes)
            item['vector_embeddings'] = vector
            migrated_count += 1
            
            if migrated_count % 200 == 0:
                print(f"Procesados {migrated_count}/{len(data)} registros...")
        except Exception as err:
            print(f"Error al procesar {crop_path}: {err}")
            
    # 4. Save final output
    try:
        with open(VECTORS_INDEX_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        duration = time.time() - start_time
        print("\n=== MIGRACIÓN FINALIZADA CON ÉXITO ===")
        print(f" - Registros migrados exitosamente: {migrated_count}")
        print(f" - Registros con recortes faltantes en disco: {missing_crops_count}")
        print(f" - Tiempo de ejecución: {duration:.2f} segundos ({duration/60:.2f} minutos)")
    except Exception as e:
        print(f"Error al guardar base de datos migrada: {e}")

if __name__ == "__main__":
    main()
