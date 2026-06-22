import httpx
import json
import io
from PIL import Image

def test_api():
    url = "http://192.168.100.78:8080/api/recognize"
    img_path = "assets/entrenamiento/img_1780071740_9367.jpg"
    
    print(f"Modificando ligeramente '{img_path}' para cambiar su SHA-256...")
    try:
        # Load image and save with slightly lower quality to alter binary bytes but keep visual content
        img = Image.open(img_path)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=95)
        altered_bytes = buf.getvalue()
        
        print("Enviando bytes alterados al servidor...")
        files = {'image': ('altered_image.jpg', altered_bytes, 'image/jpeg')}
        response = httpx.post(url, files=files, timeout=30.0)
            
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        # Verify mode is VECTOR_EXACT_MATCH
        res_data = response.json()
        assert res_data.get('mode') == 'VECTOR_EXACT_MATCH', f"Expected mode 'VECTOR_EXACT_MATCH', got '{res_data.get('mode')}'"
        assert res_data.get('CODIGO') == 'AX1362-P', f"Expected product code 'AX1362-P', got '{res_data.get('CODIGO')}'"
        print(f"\n[SUCCESS] El servidor reconoció exitosamente la pieza mediante similitud de vectores con una similitud del {res_data.get('vector_similarity')*100:.2f}%.")
    except Exception as e:
        print(f"\n[FAIL] Error al probar el endpoint del servidor: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Server response text: {response.text}")

if __name__ == "__main__":
    test_api()
