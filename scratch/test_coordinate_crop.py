import os
import fitz
import json
import requests

def test_local_pdf_crop():
    print("=== TEST 1: Prueba de recorte local de PDF con PyMuPDF ===")
    pdf_path = "CATALOGO 2.pdf"
    if not os.path.exists(pdf_path):
        print(f"Catálogo '{pdf_path}' no encontrado localmente. Saltando prueba local.")
        return
    
    code = "AX1362-P" # Un código conocido en el catálogo 2
    try:
        doc = fitz.open(pdf_path)
        print(f"Abierto {pdf_path} con éxito. Total páginas: {len(doc)}")
        
        # Buscar el código
        found_page = None
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").upper()
            if code in text:
                found_page = page_num
                break
                
        if found_page is None:
            print(f"Código '{code}' no encontrado en ninguna página. Intentando buscar 'AX1362'.")
            code = "AX1362"
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text").upper()
                if code in text:
                    found_page = page_num
                    break
        
        if found_page is not None:
            print(f"Código '{code}' encontrado en la página {found_page + 1}.")
            page = doc[found_page]
            rects = page.search_for(code)
            if rects:
                rect = rects[0]
                cx = (rect.x0 + rect.x1) / 2
                cy = (rect.y0 + rect.y1) / 2
                print(f"Coordenadas del código: cx={cx}, cy={cy}")
                
                # Definir rectángulo de 300x300 (rango de 150 a cada lado)
                x0 = max(0, cx - 150)
                y0 = max(0, cy - 150)
                x1 = min(page.rect.width, cx + 150)
                y1 = min(page.rect.height, cy + 150)
                crop_rect = fitz.Rect(x0, y0, x1, y1)
                
                # Renderizar a 150 DPI (zoom = 150/72)
                zoom = 150 / 72
                matrix = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=matrix, clip=crop_rect)
                
                output_dir = "assets/cache_recortes"
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"test_crop_{code}.jpg")
                pix.save(output_path)
                print(f"Recorte guardado exitosamente en: {output_path}")
                print(f"Dimensiones de la imagen generada: {pix.width}x{pix.height}")
                assert os.path.exists(output_path), "La imagen recortada debería existir en el disco."
                assert pix.width > 0 and pix.height > 0, "Las dimensiones de la imagen recortada deben ser mayores a 0."
                print("OK: Prueba local de recorte de PDF completada con exito.")
            else:
                print("Fallo al obtener rectangulos de busqueda del texto.")
        else:
            print(f"El codigo '{code}' no se encuentra en el PDF. No se pudo probar el recorte.")
            
        doc.close()
    except Exception as e:
        print(f"Error en prueba local de PDF: {e}")
        raise e

def test_api_endpoints():
    print("\n=== TEST 2: Prueba de Endpoints del Servidor ===")
    base_url = "http://192.168.100.78:8080"
    
    # 1. Comprobar /api/status
    try:
        res = requests.get(f"{base_url}/api/status")
        print(f"/api/status status_code: {res.status_code}")
        if res.status_code == 200:
            print(f"Respuesta /api/status: {res.json()}")
        else:
            print("El servidor local no esta corriendo en http://127.0.0.1:8080. Saltando pruebas HTTP de API.")
            return
    except Exception as e:
        print(f"No se pudo conectar al servidor local en http://127.0.0.1:8080: {e}")
        print("Asegurate de que el servidor Flask este corriendo antes de ejecutar esta parte de las pruebas.")
        return

    # 2. Comprobar busqueda de codigo
    code_query = "AX1362-P"
    try:
        res = requests.get(f"{base_url}/api/search?code={code_query}")
        print(f"/api/search?code={code_query} status_code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("Datos de respuesta:")
            print(json.dumps(data, indent=2))
            assert "catalog_page_url" in data, "La respuesta debe contener 'catalog_page_url'"
            assert "catalog_crop_url" in data, "La respuesta debe contener 'catalog_crop_url'"
            print(f"OK: urls encontradas: page={data['catalog_page_url']}, crop={data['catalog_crop_url']}")
            
            # 3. Comprobar que el crop_url realmente sirve una imagen
            crop_res = requests.get(f"{base_url}{data['catalog_crop_url']}")
            print(f"Peticion a crop_url status_code: {crop_res.status_code}")
            assert crop_res.status_code == 200, "El endpoint de recorte deberia retornar status 200"
            assert crop_res.headers.get("Content-Type", "").startswith("image/jpeg"), "El tipo de contenido del recorte debe ser image/jpeg"
            print("OK: Endpoint de recorte sirve la imagen correctamente.")
        else:
            print(f"Búsqueda de código falló con status {res.status_code}: {res.text}")
    except Exception as e:
        print(f"Error durante llamadas de prueba HTTP: {e}")
        raise e

if __name__ == "__main__":
    test_local_pdf_crop()
    test_api_endpoints()
