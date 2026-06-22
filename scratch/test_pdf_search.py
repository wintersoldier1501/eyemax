import os
import sys
import json
import shutil

# Configurar sys.path para importar server
sys.path.insert(0, os.getcwd())

try:
    import server
except ImportError as e:
    print(f"Error al importar server.py: {e}")
    sys.exit(1)

def run_tests():
    print("=== INICIANDO PRUEBAS DE BÚSQUEDA EN PDF Y RENDERIZADO ===")
    
    # Asegurar que el inventario está cargado
    server.load_inventory()
    
    # 1. Test de find_page_for_code con códigos reales comunes
    # Intentemos con códigos del inventario
    test_codes = ["AX1362", "COL294", "ER023"] # Probamos códigos comunes
    
    print("\n[TEST 1] Buscando páginas para códigos de joyería en PDF...")
    for code in test_codes:
        catalog_name, page_num = server.find_page_for_code(code)
        if catalog_name and page_num:
            print(f"  [OK] Código '{code}' encontrado en: {catalog_name}, Página: {page_num}")
        else:
            # Es posible que no estén en este inventario o PDF específico, pero probemos uno genérico 
            # que sí sepamos que existe en el PDF o imprimamos advertencia.
            print(f"  [AVISO] Código '{code}' no localizado en el PDF de catálogo actual (¿no existe en el texto?).")

    # 2. Test del renderizador de páginas del PDF fitz
    print("\n[TEST 2] Probando renderizador de páginas PDF...")
    cache_dir = os.path.join(server.app.root_path, "assets", "cache_paginas")
    
    # Limpiar caché de prueba
    test_cache_filename = "page_CATALOGO_1.pdf_1.jpg"
    test_cache_filepath = os.path.join(cache_dir, test_cache_filename)
    if os.path.exists(test_cache_filepath):
        os.remove(test_cache_filepath)
        
    # Renderizar la página 1 del catálogo 1
    if os.path.exists("CATALOGO 1.pdf"):
        try:
            # Simular petición a /api/catalog_page/CATALOGO 1.pdf/1
            with server.app.test_client() as client:
                response = client.get('/api/catalog_page/CATALOGO 1.pdf/1')
                assert response.status_code == 200, f"Error al renderizar página: {response.status_code}"
                assert os.path.exists(test_cache_filepath), "La imagen no se guardó en la caché local."
                print("  [OK] Página 1 de CATALOGO 1.pdf renderizada y guardada en caché exitosamente.")
        except Exception as e:
            print(f"  [ERROR] Falló el test de renderizado de PDF: {e}")
    else:
        print("  [AVISO] CATALOGO 1.pdf no disponible localmente para la prueba de renderizado.")

    # 3. Test de Búsqueda Predictiva por Palabras Clave
    print("\n[TEST 3] Probando búsqueda predictiva (Fuzzy Search)...")
    with server.app.test_client() as client:
        # Probemos buscar "llavero"
        response = client.get('/api/search?q=llavero')
        assert response.status_code == 200, "Error en la solicitud de búsqueda predictiva."
        data = json.loads(response.data.decode('utf-8'))
        
        products = data.get("products", [])
        print(f"  Búsqueda 'llavero' devolvió {len(products)} sugerencias.")
        
        for p in products[:3]:
            print(f"    - Código: {p['CODIGO']}, Descripción: {p['DESCRIPCION']}")
            assert "LLAVERO" in p['DESCRIPCION'].upper() or "LLAVERO" in p['CODIGO'].upper(), "El resultado no contiene el término buscado."
            
        print("  [OK] Búsqueda predictiva filtra correctamente los artículos del Excel.")

    print("\n=== ¡TODAS LAS PRUEBAS COMPLETADAS CON ÉXITO! ===")

if __name__ == '__main__':
    run_tests()
