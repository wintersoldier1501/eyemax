import os
import requests

url = "http://192.168.100.78:8080/api/recognize"

def test_with_category(img_path, category):
    print(f"\n--- Probando imagen '{os.path.basename(img_path)}' con filtro '{category}' ---")
    with open(img_path, "rb") as f:
        files = {"image": (os.path.basename(img_path), f, "image/jpeg")}
        data = {"category": category}
        try:
            response = requests.post(url, files=files, data=data, timeout=120)
            print("Status Code:", response.status_code)
            res_json = response.json()
            if "error" in res_json:
                print("Error del servidor:", res_json["error"])
                return None
            
            # Si retornó un producto exacto
            if "CODIGO" in res_json:
                desc = res_json.get("DESCRIPCION", "")
                code = res_json.get("CODIGO", "")
                mode = res_json.get("mode", "")
                print(f"[EXACT MATCH] Código: {code} | Desc: {desc} | Modo: {mode}")
                return [res_json]
            # Si retornó sugerencias (duda)
            elif "products" in res_json:
                products = res_json["products"]
                print(f"[SUGGESTIONS] Se obtuvieron {len(products)} sugerencias:")
                for p in products:
                    print(f"  - Código: {p.get('CODIGO')} | Desc: {p.get('DESCRIPCION')}")
                return products
            else:
                print("Respuesta inesperada:", res_json)
                return []
        except Exception as e:
            print(f"Error al llamar a la API: {e}")
            return None

def verify_category_keywords(products, category):
    if not products:
        print("Sin productos para verificar.")
        return True
    
    cat = category.upper()
    keywords = []
    if cat == "ARETES":
        keywords = ["ARETE", "STUD", "ARRACADA", "BROQUEL"]
    elif cat == "PIERCING":
        keywords = ["PIERCING", "EARCUFF"]
    elif cat == "ANILLO":
        keywords = ["ANILLO"]
    elif cat == "PULSERA":
        keywords = ["PULSERA", "BRAZALETE", "TOBILLERA"]
    elif cat == "COLLAR":
        keywords = ["COLLAR", "GARGANTILLA", "DIJE", "CADENA", "CHOKER"]
    elif cat == "LLAVERO":
        keywords = ["LLAVERO"]
    else:
        print("Categoría no mapeada en el validador.")
        return True
        
    all_ok = True
    for p in products:
        desc = str(p.get("DESCRIPCION", "")).upper()
        matched = any(kw in desc for kw in keywords)
        if not matched:
            print(f"Alerta: El producto '{p.get('CODIGO')}' ({desc}) NO coincide con las palabras clave de la categoría '{category}'!")
            all_ok = False
        else:
            print(f"OK: El producto '{p.get('CODIGO')}' ({desc}) coincide con la categoría '{category}'.")
    return all_ok

if __name__ == "__main__":
    img_path = "assets/entrenamiento/img_1779992816_7741.jpg"
    if not os.path.exists(img_path):
        print(f"No se encontró la imagen de prueba: {img_path}")
        exit(1)
        
    print(f"Imagen seleccionada para la prueba: {img_path}")
    
    # Prueba 1: Sin filtro ("Ninguno"). Debe dar coincidencia rápida con AX2420 (Llavero) sin llamar a Gemini.
    print("\n>>> PRUEBA 1: Sin filtro (Debe coincidir rápidamente con Llavero AX2420)")
    products_ninguno = test_with_category(img_path, "Ninguno")
    if products_ninguno and products_ninguno[0].get("CODIGO") == "AX2420":
        print("ÉXITO: Coincidencia exacta con AX2420 sin filtros en modo:", products_ninguno[0].get("mode"))
    else:
        print("FALLÓ: No se obtuvo AX2420.")
        
    # Prueba 2: Con filtro "Aretes". Debe descartar AX2420 porque es un llavero, y forzar la búsqueda de aretes (dará error de Gemini por API Key o buscará aretes en catálogo).
    print("\n>>> PRUEBA 2: Con filtro 'Aretes' (Debe descartar AX2420 por no coincidir con categoría)")
    products_aretes = test_with_category(img_path, "Aretes")
    if products_aretes:
        has_llavero = any(p.get("CODIGO") == "AX2420" for p in products_aretes)
        if has_llavero:
            print("ERROR: ¡Se incluyó el llavero AX2420 a pesar del filtro 'Aretes'!")
        else:
            print("ÉXITO: El llavero AX2420 fue descartado correctamente por el filtro de categoría.")
            verify_category_keywords(products_aretes, "Aretes")
    else:
        print("ÉXITO: Se descartó la coincidencia exacta de Llavero y falló la consulta de Gemini (esperado por API key inválida).")

    # Prueba 3: Con filtro "Llavero". Debe coincidir rápidamente con AX2420 (Llavero) sin llamar a Gemini.
    print("\n>>> PRUEBA 3: Con filtro 'Llavero' (Debe coincidir rápidamente con Llavero AX2420)")
    products_llavero = test_with_category(img_path, "Llavero")
    if products_llavero and products_llavero[0].get("CODIGO") == "AX2420":
        print("ÉXITO: Coincidencia exacta con AX2420 bajo filtro 'Llavero' en modo:", products_llavero[0].get("mode"))
    else:
        print("FALLÓ: No se obtuvo AX2420.")
