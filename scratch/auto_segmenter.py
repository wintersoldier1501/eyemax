import os
import json
import pandas as pd
import fitz

def classify_product(name):
    name_upper = name.upper()
    categories = []
    
    # Exclusive primary categories
    if "ARETE" in name_upper or "BROQUEL" in name_upper or "ARRACADA" in name_upper or "TOPITO" in name_upper:
        categories.append("ARETE")
    elif "PIERCING" in name_upper:
        categories.append("PIERCING")
    elif "EARCUFF" in name_upper or "EAR CUFF" in name_upper:
        categories.append("EARCUFF")
    elif "ANILLO" in name_upper:
        categories.append("ANILLO")
    elif "PULSERA" in name_upper or "SEMANARIO" in name_upper or "BRAZALETE" in name_upper or "TOBILLERA" in name_upper:
        categories.append("PULSERA")
    elif "COLLAR" in name_upper or "CADENA" in name_upper or "GARGANTILLA" in name_upper or "CHOKER" in name_upper or "GARGANTILLAS" in name_upper:
        categories.append("COLLAR")
    elif "LLAVERO" in name_upper:
        categories.append("LLAVERO")
    else:
        if "DIJE" in name_upper:
            categories.append("COLLAR")
            
    # Orthogonal characteristics
    if "GRABABLE" in name_upper or "PLACA" in name_upper or "ESCLAVA" in name_upper or "MEDALLA" in name_upper:
        categories.append("GRABABLE")
        
    if "PERSONALIZADO" in name_upper or "NOMBRE" in name_upper or "LETRA" in name_upper:
        categories.append("PERSONALIZADO")
        
    return categories

def build_range_string(pages, gap_tolerance=15):
    if not pages:
        return "none"
        
    sorted_pages = sorted(list(set(pages)))
    
    ranges = []
    start = sorted_pages[0]
    prev = sorted_pages[0]
    
    for p in sorted_pages[1:]:
        if p - prev <= gap_tolerance:
            prev = p
        else:
            if start == prev:
                ranges.append(f"{start}")
            else:
                ranges.append(f"{start}-{prev}")
            start = p
            prev = p
            
    if start == prev:
        ranges.append(f"{start}")
    else:
        ranges.append(f"{start}-{prev}")
        
    return ", ".join(ranges)

def main():
    excel_path = "MICROSIP.xlsx"
    config_path = "config_paginas.json"
    
    print("\n=== EJECUTANDO AUTO-SEGMENTACIÓN DE PÁGINAS ===")
    
    # 1. Load Excel
    if not os.path.exists(excel_path):
        print(f"Error: No se encontró el Excel en {excel_path}")
        return
        
    df = pd.read_excel(excel_path, sheet_name='Report', header=0)
    df.columns = [str(c).strip() for c in df.columns]
    
    name_col = None
    for col in df.columns:
        if "nombre" in col.lower() or "art" in col.lower():
            name_col = col
            break
            
    if not name_col:
        print("Error: No se pudo identificar la columna de nombre del artículo.")
        return
        
    prod_map = {}
    for idx, row in df.iterrows():
        clave = str(row.get('Clave', '')).strip().upper()
        name = str(row.get(name_col, '')).strip().upper()
        prod_map[clave] = name
        
    claves_set = set(prod_map.keys())
    
    # 2. Define catalogs
    catalogs = [
        {"file": "CATALOGO 1.pdf", "key": "catalogo1"},
        {"file": "CATALOGO 2.pdf", "key": "catalogo2"}
    ]
    
    # Categories to index
    categories_list = [
        "ARETE", "PIERCING", "EARCUFF", "ANILLO", 
        "PULSERA", "COLLAR", "GRABABLE", "PERSONALIZADO", "LLAVERO"
    ]
    
    # Initialize page range dict
    pages_by_cat = {cat: {"catalogo1": [], "catalogo2": []} for cat in categories_list}
    
    for cat_info in catalogs:
        pdf_file = cat_info["file"]
        cat_key = cat_info["key"]
        
        if not os.path.exists(pdf_file):
            print(f"Catálogo '{pdf_file}' no encontrado. Saltando...")
            continue
            
        print(f"Escaneando '{pdf_file}' para segmentación...")
        try:
            doc = fitz.open(pdf_file)
            for p_idx in range(len(doc)):
                page_num = p_idx + 1
                text = doc[p_idx].get_text("text").upper()
                
                # Check which keys are present on this page
                found_keys = []
                for clave in claves_set:
                    if clave in text:
                        found_keys.append(clave)
                        
                # Classify the keys and add page to category lists
                page_cats = {}
                total_matches = 0
                for key in found_keys:
                    p_cats = classify_product(prod_map[key])
                    for c in p_cats:
                        page_cats[c] = page_cats.get(c, 0) + 1
                        total_matches += 1
                        
                if total_matches == 0:
                    continue
                    
                # If a category is present and represents >= 30% of the page matches, register it
                for c, count in page_cats.items():
                    pct = count / total_matches
                    is_valid = False
                    if pct >= 0.30:
                        is_valid = True
                    elif total_matches <= 2 and count >= 1:
                        is_valid = True
                        
                    if is_valid:
                        pages_by_cat[c][cat_key].append(page_num)
                        
            doc.close()
        except Exception as e:
            print(f"Error al escanear {pdf_file}: {e}")
            
    # 3. Post-process to merge Piercing and Earcuff
    processed_config = {}
    for cat in categories_list:
        processed_config[cat] = {}
        
    for cat_key in ["catalogo1", "catalogo2"]:
        piercing_pages = pages_by_cat["PIERCING"][cat_key]
        earcuff_pages = pages_by_cat["EARCUFF"][cat_key]
        
        if piercing_pages or earcuff_pages:
            union_pages = list(set(piercing_pages + earcuff_pages))
            pages_by_cat["PIERCING"][cat_key] = union_pages
            pages_by_cat["EARCUFF"][cat_key] = union_pages
            
        for cat in categories_list:
            pages = pages_by_cat[cat][cat_key]
            processed_config[cat][cat_key] = build_range_string(pages, gap_tolerance=15)
            
    # 4. Save to config_paginas.json
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(processed_config, f, indent=2, ensure_ascii=False)
        print(f"[ÉXITO] Configuración de páginas guardada exitosamente en '{config_path}'")
    except Exception as e:
        print(f"Error al guardar configuración de páginas: {e}")

if __name__ == "__main__":
    main()
