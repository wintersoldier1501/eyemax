import os
import urllib.request
import onnxruntime as ort

MODEL_PATH = "scratch/clip_vision.onnx"
MODEL_URL = "https://huggingface.co/Qdrant/clip-ViT-B-32-vision/resolve/main/model.onnx"

def download_and_inspect():
    print("=== DESCARGANDO Y ANALIZANDO MODELO CLIP ONNX ===")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    if not os.path.exists(MODEL_PATH):
        print(f"Descargando {MODEL_URL}...")
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("¡Descarga completada con éxito!")
        except Exception as e:
            print(f"Error al descargar: {e}")
            return
    else:
        print("El modelo CLIP ya existe localmente.")
        
    print("\nInicializando sesión de ONNX Runtime para inspección...")
    try:
        session = ort.InferenceSession(MODEL_PATH)
        
        print("\n--- Inputs del Modelo ---")
        for i in session.get_inputs():
            print(f"Nombre: {i.name}")
            print(f"Tipo: {i.type}")
            print(f"Shape: {i.shape}")
            
        print("\n--- Outputs del Modelo ---")
        for o in session.get_outputs():
            print(f"Nombre: {o.name}")
            print(f"Tipo: {o.type}")
            print(f"Shape: {o.shape}")
            
        print("\n¡Inspección exitosa!")
    except Exception as e:
        print(f"Error al inspeccionar el modelo ONNX: {e}")

if __name__ == "__main__":
    download_and_inspect()
