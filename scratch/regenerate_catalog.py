import os
import shutil
import subprocess
import sys

VECTORS_INDEX_PATH = 'catalogo_vectores.json'
CROPS_DIR = 'assets/catalog_crops'
INDEXER_SCRIPT = 'scratch/index_catalog_vectors.py'
SEGMENTER_SCRIPT = 'scratch/auto_segmenter.py'

def main():
    print("=== INICIANDO REGENERACIÓN DEL CATÁLOGO VECTORIAL ===")
    
    # 1. Clear old vector JSON
    if os.path.exists(VECTORS_INDEX_PATH):
        print(f"Eliminando archivo de vectores antiguo: '{VECTORS_INDEX_PATH}'")
        try:
            os.remove(VECTORS_INDEX_PATH)
        except Exception as e:
            print(f"Error al eliminar {VECTORS_INDEX_PATH}: {e}")
            
    # 2. Clear old cropped images
    if os.path.exists(CROPS_DIR):
        print(f"Eliminando carpeta de recortes antiguos: '{CROPS_DIR}'")
        try:
            shutil.rmtree(CROPS_DIR)
        except Exception as e:
            print(f"Error al eliminar la carpeta {CROPS_DIR}: {e}")
            
    # 3. Run the indexer script
    if not os.path.exists(INDEXER_SCRIPT):
        print(f"Error: No se encontró el script de indexación '{INDEXER_SCRIPT}'.")
        sys.exit(1)
        
    print("\nEjecutando el indexador sobre los nuevos archivos...")
    python_exe = sys.executable  # Uses the active virtual environment python
    try:
        # Run indexer and print output in real-time
        result = subprocess.run([python_exe, INDEXER_SCRIPT], check=True)
        if result.returncode == 0:
            print("\n[ÉXITO] El catálogo vectorial ha sido completamente regenerado.")
            
            # 4. Run the auto-segmenter script
            if os.path.exists(SEGMENTER_SCRIPT):
                print("\nEjecutando la segmentación automática de páginas...")
                seg_result = subprocess.run([python_exe, SEGMENTER_SCRIPT], check=True)
                if seg_result.returncode == 0:
                    print("[ÉXITO] Segmentación y rangos de páginas actualizados.")
                else:
                    print("[ERROR] Falló el script de segmentación automática.")
            else:
                print(f"[Aviso] No se encontró el script de segmentación '{SEGMENTER_SCRIPT}'.")
                
            print("IMPORTANTE: Recuerda reiniciar el servidor Flask para cargar la nueva base de datos de vectores.")
        else:
            print("\n[ERROR] Ocurrió un fallo durante la indexación.")
    except Exception as e:
        print(f"\nError al ejecutar el pipeline de indexación/segmentación: {e}")

if __name__ == "__main__":
    main()
