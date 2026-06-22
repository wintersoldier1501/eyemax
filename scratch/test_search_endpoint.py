import httpx
import json

def test_search(query):
    url = f"http://192.168.100.78:8080/api/search?q={query}"
    try:
        response = httpx.get(url, timeout=5.0)
        print(f"\n--- Búsqueda: '{query}' (Status: {response.status_code}) ---")
        if response.status_code == 200:
            products = response.json().get("products", [])
            print(f"Resultados encontrados: {len(products)}")
            for i, p in enumerate(products[:5]):
                print(f" {i+1}. [{p.get('CODIGO')}] {p.get('DESCRIPCION')} (${p.get('PRECIO venta publico')} MXN)")
            return products
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def main():
    print("=== PROBANDO BUSQUEDAS EN /api/search ===")
    
    # 1. Búsqueda simple
    test_search("llavero herramientas")
    
    # 2. Búsqueda con palabras vacías (stop words)
    test_search("pulsera de acrilico rojo")
    
    # 3. Búsqueda usando sinónimos ("vino" -> "rojo/acrilico")
    test_search("pulsera color vino")
    
    # 4. Búsqueda de aretes dorados
    test_search("arete dorado estrellas")
    
if __name__ == "__main__":
    main()
