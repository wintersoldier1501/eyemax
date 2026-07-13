import os
import fitz
import json
import pandas as pd
import re
import onnxruntime as ort
from PIL import Image
import numpy as np
import io
import sys

EXCEL_PATH = 'MICROSIP.xlsx'
VECTORS_INDEX_PATH = 'catalogo_vectores.json'
MODEL_PATH = "scratch/clip_vision.onnx"
CROPS_DIR = "assets/catalog_crops"

def main():
    print("=== INICIANDO INDEXADOR MULTIMODAL RAG ===")
    
    # 1. Load Excel
    if not os.path.exists(EXCEL_PATH):
        print(f"Error: No se encontró el archivo de inventario '{EXCEL_PATH}'.")
        sys.exit(1)
        
    print("Cargando inventario de Excel...")
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='Report', header=0)
        df.columns = [str(c).strip() for c in df.columns]
        if 'Clave' not in df.columns:
            print("Error: No se encontró la columna 'Clave' en el archivo Excel.")
            sys.exit(1)
        claves = df['Clave'].dropna().astype(str).str.strip().unique().tolist()
        print(f"Total de claves únicas encontradas en Excel: {len(claves)}")
    except Exception as e:
        print(f"Error al cargar Excel: {e}")
        sys.exit(1)

    # 2. Load existing index
    existing_index = {}
    if os.path.exists(VECTORS_INDEX_PATH):
        try:
            with open(VECTORS_INDEX_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    # Solo reutilizar si tiene la dimensión correcta (512 de CLIP)
                    if 'vector_embeddings' in item and len(item['vector_embeddings']) == 512:
                        existing_index[item['codigo']] = item
            print(f"Cargado índice existente con {len(existing_index)} registros en formato CLIP (512d).")
        except Exception as e:
            print(f"Error al leer índice existente: {e}")

    # 3. Load PDF texts to memory for ultra-fast string matching
    print("Cargando textos de los PDFs a memoria para búsqueda rápida...")
    pdf_files = [("CATALOGO 1.pdf", "CATALOGO 1.pdf"), ("CATALOGO 2.pdf", "CATALOGO 2.pdf")]
    pdf_docs = {}
    pdf_texts = {}

    for display_name, file_path in pdf_files:
        if not os.path.exists(file_path):
            print(f"Catálogo '{file_path}' no encontrado localmente. Saltando...")
            continue
        try:
            doc = fitz.open(file_path)
            pdf_docs[display_name] = doc
            pages_texts = []
            for p_num in range(len(doc)):
                page_text = doc[p_num].get_text("text").upper()
                pages_texts.append(page_text)
            pdf_texts[display_name] = pages_texts
            print(f"Cargado '{display_name}' con {len(doc)} páginas en caché de texto.")
        except Exception as e:
            print(f"Error al cargar '{file_path}': {e}")

    if not pdf_docs:
        print("Error: No se pudo cargar ningún catálogo PDF.")
        sys.exit(1)

    # 4. Load ONNX model session
    if not os.path.exists(MODEL_PATH):
        print(f"Error: No se encontró el modelo ONNX en '{MODEL_PATH}'.")
        sys.exit(1)
        
    print("Cargando sesión de ONNX Runtime...")
    try:
        ort_session = ort.InferenceSession(MODEL_PATH)
        input_name = ort_session.get_inputs()[0].name
    except Exception as e:
        print(f"Error al cargar sesión de ONNX: {e}")
        sys.exit(1)

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

    # 5. Processing Loop
    indexed_count = 0
    skipped_count = 0
    not_found_count = 0

    output_records = list(existing_index.values())

    print("\nIniciando extracción y vectorización...")
    try:
        for idx, code in enumerate(claves):
            code_upper = code.upper().strip()
            if not code_upper:
                continue
                
            if code_upper in existing_index:
                skipped_count += 1
                continue
                
            # Search in memory text lists
            found_catalog = None
            found_page_idx = None
            
            # 1. Exact Match Search
            for catalog_name, pages_texts in pdf_texts.items():
                for p_idx, text in enumerate(pages_texts):
                    if code_upper in text:
                        found_catalog = catalog_name
                        found_page_idx = p_idx
                        break
                if found_catalog:
                    break
                    
            # 2. Base Match Search (fallback: AX1362P -> AX1362)
            if not found_catalog:
                base_match = re.match(r'^([A-Z0-9]+?\d+)', code_upper)
                if base_match:
                    base_code = base_match.group(1)
                    if base_code != code_upper and len(base_code) >= 3:
                        for catalog_name, pages_texts in pdf_texts.items():
                            for p_idx, text in enumerate(pages_texts):
                                if base_code in text:
                                    found_catalog = catalog_name
                                    found_page_idx = p_idx
                                    break
                            if found_catalog:
                                break
                                
            if not found_catalog:
                not_found_count += 1
                continue
                
            # Crop & Index the item
            try:
                doc = pdf_docs[found_catalog]
                page = doc[found_page_idx]
                
                # Find the search term (try full code first, then base code if needed)
                rects = page.search_for(code_upper)
                if not rects:
                    base_match = re.match(r'^([A-Z0-9]+?\d+)', code_upper)
                    if base_match:
                        rects = page.search_for(base_match.group(1))
                        
                if rects:
                    rect = rects[0]
                    cx = (rect.x0 + rect.x1) / 2
                    cy = (rect.y0 + rect.y1) / 2
                    
                    # Bounding box of 300x300 shifted vertically upward by 80 points
                    # because catalog images are placed above their code texts
                    x0 = max(0, cx - 150)
                    y0 = max(0, cy - 230)
                    x1 = min(page.rect.width, cx + 150)
                    y1 = min(page.rect.height, cy + 70)
                    crop_rect = fitz.Rect(x0, y0, x1, y1)
                    
                    # Render to 150 DPI
                    zoom = 150 / 72
                    matrix = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=matrix, clip=crop_rect)
                    
                    # Save crop file
                    safe_catalog_name = found_catalog.replace(" ", "_").replace(".pdf", "")
                    page_dir = os.path.join(CROPS_DIR, safe_catalog_name, f"page_{found_page_idx + 1}")
                    os.makedirs(page_dir, exist_ok=True)
                    
                    safe_code_name = code_upper.replace("/", "_").replace("\\", "_")
                    crop_filename = f"{safe_code_name}.jpg"
                    crop_filepath = os.path.join(page_dir, crop_filename)
                    
                    pix.save(crop_filepath)
                    
                    # Compute vector embedding
                    with open(crop_filepath, 'rb') as img_f:
                        img_bytes = img_f.read()
                    vector = extract_vector(img_bytes)
                    
                    # Add to index
                    record = {
                        "codigo": code_upper,
                        "catalogo": found_catalog,
                        "pagina": found_page_idx + 1,
                        "crop_path": crop_filepath.replace("\\", "/"),
                        "vector_embeddings": vector
                    }
                    
                    output_records.append(record)
                    existing_index[code_upper] = record
                    indexed_count += 1
                    
                    print(f"[{idx+1}/{len(claves)}] Indexado con éxito: {code_upper} -> {found_catalog} pág. {found_page_idx + 1}")
                    
                    # Save periodically
                    if indexed_count % 50 == 0:
                        with open(VECTORS_INDEX_PATH, 'w', encoding='utf-8') as f:
                            json.dump(output_records, f, indent=2, ensure_ascii=False)
                        print(f"\n--- Guardado parcial: {len(output_records)} registros indexados ---")
                else:
                    not_found_count += 1
            except Exception as crop_err:
                print(f"Error al procesar recorte para '{code_upper}': {crop_err}")
                
    finally:
        # Save final index
        if indexed_count > 0:
            with open(VECTORS_INDEX_PATH, 'w', encoding='utf-8') as f:
                json.dump(output_records, f, indent=2, ensure_ascii=False)
            print(f"\nProceso finalizado. Total indexados en esta sesión: {indexed_count}.")
            
        print(f"\nResumen de sesión:")
        print(f" - Ya indexados previamente (omitidos): {skipped_count}")
        print(f" - Indexados en esta sesión: {indexed_count}")
        print(f" - No encontrados en catálogos (o sin coordenadas): {not_found_count}")

    # Close PDF documents
    for doc in pdf_docs.values():
        doc.close()

if __name__ == "__main__":
    main()
