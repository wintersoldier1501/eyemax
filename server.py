import os
import sys
import random
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
import json
import re
import google.generativeai as genai
import datetime
import fitz
import shutil
from functools import wraps
import onnxruntime as ort
import numpy as np
from PIL import Image
import urllib.request
import io

# ONNX Local Embeddings Config
ORT_SESSION = None
MODEL_PATH = "scratch/mobilenetv2.onnx"
MODEL_URL = "https://huggingface.co/onnxmodelzoo/mobilenetv2-12/resolve/main/mobilenetv2-12.onnx"

def initialize_onnx_model():
    global ORT_SESSION
    if ORT_SESSION is not None:
        return
        
    print("Verificando modelo local ONNX de MobileNetV2...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        print(f"Descargando modelo ONNX desde {MODEL_URL}...")
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("Descarga del modelo exitosa.")
        except Exception as e:
            print(f"Error al descargar el modelo ONNX: {e}")
            raise e
            
    print("Cargando sesión de ONNX Runtime...")
    try:
        ORT_SESSION = ort.InferenceSession(MODEL_PATH)
        print("Modelo ONNX cargado exitosamente.")
    except Exception as e:
        print(f"Error al inicializar sesión de ONNX: {e}")
        raise e

def extract_image_vector(image_bytes):
    """
    Extrae un vector de 1000 dimensiones (logits) usando MobileNetV2 ONNX
    a partir de los bytes de una imagen.
    """
    global ORT_SESSION
    if ORT_SESSION is None:
        try:
            initialize_onnx_model()
        except Exception as e:
            print(f"No se pudo inicializar el modelo ONNX al extraer vector: {e}")
            return None
        
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Redimensionar a 224x224 (entrada de MobileNetV2)
        img_resized = img.resize((224, 224), Image.Resampling.BILINEAR)
        img_data = np.array(img_resized).astype(np.float32)
        
        # Transponer de HWC a CHW (3, 224, 224)
        img_data = img_data.transpose(2, 0, 1)
        
        # Normalizar con la media y desviación estándar de ImageNet
        mean = np.array([0.485, 0.456, 0.406]).reshape(3, 1, 1)
        std = np.array([0.229, 0.224, 0.225]).reshape(3, 1, 1)
        img_data = (img_data / 255.0 - mean) / std
        
        # Agregar dimensión de lote (1, 3, 224, 224)
        input_data = np.expand_dims(img_data, axis=0).astype(np.float32)
        
        # Correr inferencia
        input_name = ORT_SESSION.get_inputs()[0].name
        outputs = ORT_SESSION.run(None, {input_name: input_data})
        vector = outputs[0][0].tolist() # Convertir a lista de floats de Python
        return vector
    except Exception as e:
        print(f"Error al extraer vector de la imagen: {e}")
        return None

def cosine_similarity(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    arr1 = np.array(v1)
    arr2 = np.array(v2)
    dot = np.dot(arr1, arr2)
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return float(dot / (norm1 * norm2))

def migrate_training_history():
    """
    Recorre 'historial_entrenamiento.json' y para cada registro que no tenga
    'vector_embeddings', lee la imagen local (si existe) y le calcula su embedding.
    """
    history_file = 'historial_entrenamiento.json'
    if not os.path.exists(history_file):
        return
    print("Iniciando migración silenciosa de historial de entrenamiento para vectorización...")
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        modified = False
        for item in history:
            if 'vector_embeddings' not in item:
                image_path = item.get('image_path')
                if image_path and os.path.exists(image_path):
                    print(f"Migrando {image_path}...")
                    try:
                        with open(image_path, 'rb') as img_f:
                            img_bytes = img_f.read()
                        vector = extract_image_vector(img_bytes)
                        if vector:
                            item['vector_embeddings'] = vector
                            modified = True
                    except Exception as e:
                        print(f"Error al migrar entrada {image_path}: {e}")
                        
        if modified:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            print("Migración de historial completada y guardada.")
        else:
            print("Historial ya estaba completamente migrado o vacío.")
    except Exception as e:
        print(f"Error durante la migración del historial: {e}")

def get_queries_count():
    """Lee el archivo registro_consultas.json y retorna el número de consultas hechas hoy."""
    file_path = 'registro_consultas.json'
    today = datetime.date.today().isoformat()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('fecha') == today:
                return data.get('consultas_realizadas', 0)
        except Exception as e:
            print(f"Error al leer registro_consultas.json: {e}")
    return 0

def increment_query_count():
    """Incrementa el contador de consultas de hoy en registro_consultas.json y lo guarda."""
    file_path = 'registro_consultas.json'
    today = datetime.date.today().isoformat()
    current_count = 0
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('fecha') == today:
                current_count = data.get('consultas_realizadas', 0)
        except Exception as e:
            print(f"Error al leer registro_consultas.json al incrementar: {e}")
    
    current_count += 1
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({"fecha": today, "consultas_realizadas": current_count}, f, indent=2)
        print(f"[API QUOTA] Consulta de Gemini registrada. Total hoy: {current_count}")
    except Exception as e:
        print(f"Error al guardar registro_consultas.json: {e}")
    return current_count

ADMIN_PIN = "5161"

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permite autenticación simple mediante cookie o header Authorization
        token = request.headers.get("Authorization") or request.cookies.get("admin_token")
        if token == f"eyemax_auth_{ADMIN_PIN}":
            return f(*args, **kwargs)
        return jsonify({"error": "No autorizado. PIN inválido o sesión expirada."}), 401
    return decorated_function

def find_page_for_code(code):
    """
    Busca en qué página de CATALOGO 1.pdf o CATALOGO 2.pdf se encuentra el texto 'code'.
    Retorna (catalog_name, page_num) o (None, None).
    """
    if not code:
        return None, None
        
    code_clean = str(code).strip().upper()
    if not code_clean:
        return None, None
        
    pdf_files = [("CATALOGO 1.pdf", "CATALOGO 1.pdf"), ("CATALOGO 2.pdf", "CATALOGO 2.pdf")]
    
    # 1. Intentar con el código exacto completo
    for display_name, file_path in pdf_files:
        if not os.path.exists(file_path):
            continue
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text").upper()
                if code_clean in text:
                    doc.close()
                    return display_name, page_num + 1
            doc.close()
        except Exception as e:
            print(f"Error al buscar código completo en PDF '{display_name}': {e}")
            
    # 2. Intentar con el código base (removiendo sufijos P/G de plata/oro o guiones)
    # Por ejemplo, AX1362P -> AX1362, AX1362-G -> AX1362
    base_match = re.match(r'^([A-Z0-9]+?\d+)', code_clean)
    if base_match:
        base_code = base_match.group(1)
        if base_code != code_clean and len(base_code) >= 3:
            for display_name, file_path in pdf_files:
                if not os.path.exists(file_path):
                    continue
                try:
                    doc = fitz.open(file_path)
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        text = page.get_text("text").upper()
                        if base_code in text:
                            doc.close()
                            return display_name, page_num + 1
                    doc.close()
                except Exception as e:
                    print(f"Error al buscar código base en PDF '{display_name}': {e}")
                    
    return None, None


app = Flask(__name__, static_url_path='', static_folder='assets')

# Configuración global
EXCEL_PATH = 'MICROSIP.xlsx'
CATALOGS = []

# Cargar variables de entorno desde un archivo .env si existe localmente
if os.path.exists('.env'):
    print("Detectado archivo '.env'. Cargando configuración local...")
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    # Quitar comillas si el valor las tiene
                    val = v.strip().strip("'").strip('"')
                    os.environ[k.strip()] = val
    except Exception as e:
        print(f"Advertencia al leer el archivo '.env': {e}")

# Variables globales para almacenar el DataFrame y las referencias de archivos en Gemini
df_inventario = None
gemini_configured = False
catalog_file_names = []  # Almacena los nombres de recurso de los PDFs subidos en Gemini

def initialize_gemini_catalogs():
    """Verifica si CATALOGO 1.pdf y CATALOGO 2.pdf están subidos a Gemini. Si no, los sube y espera a que estén activos."""
    global catalog_file_names, gemini_configured
    if not gemini_configured:
        print("Gemini no está configurado, saltando inicialización de catálogos.")
        return

    print("Verificando catálogos PDF en Gemini Files API...")
    try:
        existing_files = list(genai.list_files())
        existing_map = {f.display_name: f for f in existing_files}
    except Exception as e:
        print(f"Error al listar archivos en Gemini: {e}")
        return

    pdfs_to_upload = [
        ("CATALOGO 1.pdf", "CATALOGO 1.pdf"),
        ("CATALOGO 2.pdf", "CATALOGO 2.pdf")
    ]

    loaded_refs = []
    import time
    for display_name, file_path in pdfs_to_upload:
        if not os.path.exists(file_path):
            print(f"Catálogo local no encontrado: {file_path}")
            continue
            
        file_ref = None
        if display_name in existing_map:
            cached_ref = existing_map[display_name]
            if cached_ref.state.name in ["ACTIVE", "PROCESSING"]:
                print(f"Catálogo '{display_name}' ya está en Gemini: {cached_ref.name} ({cached_ref.state.name})")
                file_ref = cached_ref
            else:
                print(f"Catálogo '{display_name}' en Gemini está en estado {cached_ref.state.name}. Volviendo a subir...")
        
        if file_ref is None:
            print(f"Subiendo {file_path} a Gemini Files API (puede tardar un momento)...")
            try:
                file_ref = genai.upload_file(file_path, display_name=display_name)
                print(f"Subido con éxito. Nombre recurso: {file_ref.name}")
            except Exception as e:
                print(f"Error al subir catálogo {file_path}: {e}")
                continue

        # Esperar a que pase el procesamiento si es necesario
        try:
            while file_ref.state.name == "PROCESSING":
                print(f"Esperando que se procese '{display_name}' ({file_ref.name})...")
                time.sleep(5)
                file_ref = genai.get_file(file_ref.name)
            
            if file_ref.state.name == "ACTIVE":
                print(f"Catálogo '{display_name}' está ACTIVO.")
                loaded_refs.append(file_ref)
            else:
                print(f"Advertencia: El catálogo '{display_name}' tiene un estado no activo: {file_ref.state.name}")
        except Exception as e:
            print(f"Error al verificar estado del archivo {display_name}: {e}")
            loaded_refs.append(file_ref)

    catalog_file_names = loaded_refs
    print(f"Inicialización completa. {len(catalog_file_names)} catálogos cargados en memoria global.")


def clean_detected_code(raw_code):
    if not raw_code:
        return ""
    # Eliminar bloques de código markdown y comillas
    cleaned = raw_code.replace("```json", "").replace("```", "")
    cleaned = cleaned.replace('"', '').replace("'", "").replace("`", "").strip()
    
    # Buscar patrones de códigos comunes
    # Los códigos suelen ser palabras alfanuméricas de 3 a 30 caracteres
    words = cleaned.split()
    for word in words:
        word_clean = word.strip(".,:;()[]{}*-")
        if 3 <= len(word_clean) <= 30:
            upper_word = word_clean.upper()
            if any(c.isdigit() for c in upper_word) and any(c.isalpha() for c in upper_word):
                return upper_word
            if any(upper_word.startswith(prefix) for prefix in ['AX', 'CH', 'ER', 'CAX', 'COL']):
                return upper_word
                
    # Si no encontramos nada con el filtro, tomamos la primera línea limpia
    lines = [l.strip().upper() for l in cleaned.splitlines() if l.strip()]
    if lines:
        return lines[0]
    return cleaned.upper()

def load_inventory():
    """Carga y limpia el archivo de inventario en un DataFrame de Pandas."""
    global df_inventario
    print(f"Cargando inventario desde '{EXCEL_PATH}'...")
    try:
        # Leer la hoja 'Report' usando la fila 1 (índice 0) como cabecera (header=0)
        df = pd.read_excel(EXCEL_PATH, sheet_name='Report', header=0)
        
        # Limpiar nombres de columnas (eliminar espacios en blanco)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Asegurar que 'Clave' no tenga espacios y sea string
        if 'Clave' in df.columns:
            df['Clave'] = df['Clave'].astype(str).str.strip()
            
        df_inventario = df
        print(f"Inventario cargado exitosamente. Total de registros: {len(df_inventario)}")
        print(f"Columnas disponibles: {list(df_inventario.columns)}")
    except Exception as e:
        print(f"Error crítico al cargar el inventario: {e}", file=sys.stderr)
        sys.exit(1)

# Inicializar cliente de Gemini si existe la API Key usando la librería google.generativeai
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or "AIzaSyA3o_FvXy2h6qbS3KQ7wzfdZuuAf9ZRicw"
if GEMINI_API_KEY:
    try:
        print("GEMINI_API_KEY detectada. Configurando google.generativeai...")
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_configured = True
    except Exception as e:
        print(f"Error al configurar google.generativeai: {e}", file=sys.stderr)
else:
    print("\n" + "="*80)
    print("AVISO: GEMINI_API_KEY no configurada. El servidor correrá en MODO SIMULACIÓN (MOCK).")
    print("Para usar reconocimiento real, configura la variable de entorno GEMINI_API_KEY.")
    print("="*80 + "\n")

import hashlib

def compute_file_sha256(path):
    if not os.path.exists(path):
        return ""
    try:
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error computing hash: {e}")
        return ""

def get_image_visual_description(image_path):
    """Llama a Gemini de forma rápida para obtener una descripción de 5 a 10 palabras descriptivas de la joya."""
    global gemini_configured
    if not gemini_configured or not os.path.exists(image_path):
        return "joyeria"
    try:
        print(f"Generando descripción visual para '{image_path}' con Gemini...")
        model = genai.GenerativeModel('gemini-3.5-flash')
        with open(image_path, 'rb') as f:
            img_bytes = f.read()
        
        mime_type = 'image/jpeg'
        if image_path.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_path.lower().endswith('.gif'):
            mime_type = 'image/gif'
        elif image_path.lower().endswith('.webp'):
            mime_type = 'image/webp'
            
        prompt = (
            "Describe esta pieza de joyería en una frase corta de 5 a 10 palabras descriptivas en español. "
            "Enfócate estrictamente en características visuales obvias: tipo de pieza (anillo, pulsera, arete, piercing), color del metal (dorado, plata), material (cuero, acero, etc.) y dijes o patrones distintivos. "
            "Ejemplo de salida: pulsera de cuero negro con tres aros dorados."
        )
        
        response = model.generate_content([
            {'mime_type': mime_type, 'data': img_bytes},
            prompt
        ])
        increment_query_count()
        desc = response.text.strip()
        print(f"Descripción visual generada: {desc}")
        return desc
    except Exception as e:
        print(f"Error generando descripción: {e}")
        return "joyeria"

def load_page_config():
    config_path = 'config_paginas.json'
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al leer {config_path}: {e}")
    return {}

def get_category_from_product(product):
    if not product:
        return "UNKNOWN"
    desc = str(product.get('DESCRIPCION', '')).upper()
    code = str(product.get('CODIGO', '')).upper()
    
    # LLAVERO es una categoría específica que puede ser grabable
    if "LLAVERO" in desc:
        return "LLAVERO"
    # Grabable / personalizado general
    if any(x in desc for x in ["GRABABLE", "PERSONALIZADO", "GRABADO", "INICIALES"]):
        return "GRABABLE"
    if "PIERCING" in desc:
        return "PIERCING"
    if "EARCUFF" in desc:
        return "EARCUFF"
    if any(x in desc for x in ["ARETE", "STUD", "ARRACADA", "BROQUEL"]):
        return "ARETE"
    if "ANILLO" in desc:
        return "ANILLO"
    if any(x in desc for x in ["PULSERA", "BRAZALETE", "TOBILLERA"]):
        return "PULSERA"
    if any(x in desc for x in ["COLLAR", "GARGANTILLA", "DIJE", "CADENA"]):
        return "COLLAR"
        
    return "UNKNOWN"

def save_to_training_history(image_path, code):
    history_file = 'historial_entrenamiento.json'
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception as e:
            print(f"Error al leer {history_file}: {e}")
    
    image_path_norm = image_path.replace("\\", "/")
    image_hash = compute_file_sha256(image_path)
    
    # Calcular embedding vector
    vector = None
    if os.path.exists(image_path):
        try:
            with open(image_path, 'rb') as f:
                img_bytes = f.read()
            vector = extract_image_vector(img_bytes)
        except Exception as err:
            print(f"Error al extraer embedding para guardar en historial: {err}")

    # Verificar si el hash o ruta ya está en el historial para evitar duplicaciones
    for item in history:
        if (image_hash and item.get('image_hash') == image_hash) or (item.get('image_path') == image_path_norm):
            # Si ya coincide con el código correcto, actualizar el vector y salir
            if item.get('codigo') == code:
                print(f"[HISTORIAL] El archivo o hash ya existe con la misma clave: {code}")
                if vector and 'vector_embeddings' not in item:
                    item['vector_embeddings'] = vector
                    try:
                        with open(history_file, 'w', encoding='utf-8') as f:
                            json.dump(history, f, indent=2, ensure_ascii=False)
                    except Exception as e:
                        print(f"Error al actualizar vector en historial existente: {e}")
                return
            else:
                # Si es un código diferente, actualizar
                item['codigo'] = code
                item['descripcion_visual'] = get_image_visual_description(image_path)
                if vector:
                    item['vector_embeddings'] = vector
                try:
                    with open(history_file, 'w', encoding='utf-8') as f:
                        json.dump(history, f, indent=2, ensure_ascii=False)
                    print(f"[HISTORIAL] Actualizado entrenamiento por hash/ruta: {image_path_norm} -> {code}")
                except Exception as e:
                    print(f"Error al escribir actualización: {e}")
                return

    # Si es nuevo registro, aplicar poda a un máximo de 3 imágenes para este código
    code_records = [item for item in history if item.get('codigo') == code]
    if len(code_records) >= 3:
        oldest_record = code_records[0]
        oldest_path = oldest_record.get('image_path')
        print(f"[HISTORIAL PRUNING] El código '{code}' ya tiene {len(code_records)} fotos asociadas. Eliminando la más antigua: {oldest_path}")
        
        # Eliminar archivo físico de la imagen de entrenamiento más antigua
        if oldest_path and os.path.exists(oldest_path):
            try:
                os.remove(oldest_path)
                print(f"[HISTORIAL PRUNING] Archivo físico eliminado: {oldest_path}")
            except Exception as err:
                print(f"[HISTORIAL PRUNING] Error al eliminar archivo físico {oldest_path}: {err}")
        
        # Filtrar del historial
        history = [item for item in history if not (item.get('image_path') == oldest_path or 
                                                    (oldest_record.get('image_hash') and item.get('image_hash') == oldest_record.get('image_hash')))]

    # Generar descripción visual en el momento
    desc = get_image_visual_description(image_path)
    new_record = {
        'image_path': image_path_norm,
        'image_hash': image_hash,
        'codigo': code,
        'descripcion_visual': desc
    }
    if vector:
        new_record['vector_embeddings'] = vector
    
    history.append(new_record)
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"[HISTORIAL] Guardado entrenamiento nuevo: {image_path_norm} -> {code} ({desc})")
    except Exception as e:
        print(f"Error al escribir en {history_file}: {e}")


def load_diversified_training_examples(category_filter=None, limit=15):
    """Retorna ejemplos diversificados del historial de entrenamiento (máximo 1 foto por código único), filtrados opcionalmente por categoría."""
    history_file = 'historial_entrenamiento.json'
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        unique_examples = {}
        for item in reversed(history):
            code = item.get('codigo')
            img_path = item.get('image_path')
            if code and img_path and os.path.exists(img_path):
                # Aplicar filtrado por categoría si se solicita
                if category_filter and category_filter != "UNKNOWN":
                    prod = get_product_by_code(code)
                    prod_cat = get_category_from_product(prod)
                    if prod_cat != category_filter:
                        continue
                        
                if code not in unique_examples:
                    unique_examples[code] = item
                    if len(unique_examples) >= limit:
                        break
                        
        return list(unique_examples.values())
    except Exception as e:
        print(f"Error al leer ejemplos diversificados de {history_file}: {e}")
        return []

def lookup_code_by_image_hash(image_hash):
    """Busca si alguna imagen con el mismo hash ya ha sido confirmada por el usuario."""
    if not image_hash:
        return None
    history_file = 'historial_entrenamiento.json'
    if not os.path.exists(history_file):
        return None
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        for item in reversed(history):
            if item.get('image_hash') == image_hash:
                return item.get('codigo')
    except Exception as e:
        print(f"Error al buscar por hash: {e}")
    return None

def get_image_path_by_hash(image_hash):
    if not image_hash:
        return None
    history_file = 'historial_entrenamiento.json'
    if not os.path.exists(history_file):
        return None
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        for item in reversed(history):
            if item.get('image_hash') == image_hash:
                return item.get('image_path')
    except Exception as e:
        pass
    return None

def get_product_by_code(code):
    """Busca un producto en el inventario por su clave y lo mapea para compatibilidad con el frontend."""
    global df_inventario
    if df_inventario is None or df_inventario.empty:
        return None
    
    # Búsqueda insensible a mayúsculas/minúsculas y sin espacios
    code_clean = str(code).strip().upper()
    result = df_inventario[df_inventario['Clave'].astype(str).str.strip().str.upper() == code_clean]
    
    if not result.empty:
        row = result.iloc[0]
        
        # Mapear columnas de MICROSIP a los nombres que espera el frontend
        product = {
            'CODIGO': str(row.get('Clave', '')).strip(),
            'DESCRIPCION': str(row.get('Nombre del artículo', '')).strip(),
            'MATERIAL': 'ACERO INOXIDABLE', # Fallback por defecto
            'PRECIO venta publico': float(row.get('Precio público', 0.0))
        }
        
        # Mantener además todas las columnas originales de MICROSIP
        for col in df_inventario.columns:
            val = row[col]
            if pd.isna(val):
                if col in ['Precio público', 'Precio mayoreo', 'Almacén general', 'Vista hermosa', 'Paseo']:
                    product[col] = 0.0
                else:
                    product[col] = ""
            else:
                if col in ['Precio público', 'Precio mayoreo', 'Almacén general', 'Vista hermosa', 'Paseo']:
                    try:
                        product[col] = float(val)
                    except ValueError:
                        product[col] = 0.0
                else:
                    if isinstance(val, (int, float)):
                        product[col] = val
                    else:
                        product[col] = str(val)
        return product
    return None

@app.route('/api/recognize', methods=['POST'])
def recognize_product():
    """Endpoint principal para procesar la imagen de joyería y reconocerla usando Gemini."""
    if 'image' not in request.files:
        return jsonify({"error": "No se recibió ninguna imagen en el campo 'image'"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400
        
    print(f"\n--- Nueva solicitud de reconocimiento recibida: {file.filename} ---")
    
    # Cargar obligatoriamente el inventario de Excel antes de procesar
    load_inventory()
    
    # Búsqueda directa en Pandas: si el nombre base del archivo es un código existente en el inventario,
    # se retorna la información real de forma dinámica e inmediata sin llamar a Gemini.
    filename_lower = file.filename.lower()
    if filename_lower.endswith(('.jpg', '.png', '.jpeg')):
        code_candidate = os.path.splitext(file.filename)[0].upper().strip()
    else:
        code_candidate = file.filename.upper().strip()

    product_data = get_product_by_code(code_candidate)
    if product_data:
        print(f"[BUSQUEDA DIRECTA PANDAS] Código '{code_candidate}' detectado. Retornando datos de inventario sin llamar a Gemini.")
        product_data['mode'] = 'PANDAS_DIRECT'
        catalog_name, page_num = find_page_for_code(code_candidate)
        if catalog_name and page_num:
            product_data['catalog_page_url'] = f"/api/catalog_page/{catalog_name}/{page_num}"
        return jsonify(product_data)

    # Leer los bytes de la imagen directamente del request
    image_bytes = file.read()
    if not image_bytes:
        return jsonify({"error": "Archivo de imagen vacío o corrupto."}), 400

    # Stage 1: Búsqueda rápida por hash de imagen (SHA-256)
    import hashlib
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    confirmed_code_from_hash = lookup_code_by_image_hash(image_hash)
    if confirmed_code_from_hash:
        print(f"[MEMORIA EXACTA] Imagen idéntica encontrada en el historial con el código '{confirmed_code_from_hash}'.")
        product_data = get_product_by_code(confirmed_code_from_hash)
        if product_data:
            product_data['mode'] = 'MEMORY_HASH_MATCH'
            product_data['type'] = 'exact'
            product_data['image_path'] = get_image_path_by_hash(image_hash) or ""
            catalog_name, page_num = find_page_for_code(confirmed_code_from_hash)
            if catalog_name and page_num:
                product_data['catalog_page_url'] = f"/api/catalog_page/{catalog_name}/{page_num}"
            return jsonify(product_data)

    # Stage 2: Búsqueda por similitud de vectores locales (ONNX Runtime)
    scanned_vector = extract_image_vector(image_bytes)
    best_similarity = -1.0
    best_match_item = None
    
    # Lista de candidatos prioritarios para Gemini (similitud entre 75% y 92%)
    vector_candidates = []
    
    if scanned_vector:
        history_file = 'historial_entrenamiento.json'
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # Agrupar las puntuaciones por código para encontrar el mejor score por producto
                scores_by_code = {}
                for item in history:
                    item_vector = item.get('vector_embeddings')
                    code = item.get('codigo')
                    if item_vector and code:
                        sim = cosine_similarity(scanned_vector, item_vector)
                        if code not in scores_by_code or sim > scores_by_code[code]['sim']:
                            scores_by_code[code] = {'sim': sim, 'item': item}
                
                # Encontrar el mejor en general
                for code, data in scores_by_code.items():
                    sim = data['sim']
                    item = data['item']
                    if sim > best_similarity:
                        best_similarity = sim
                        best_match_item = item
                    
                    # Si tiene similitud considerable, considerarlo candidato prioritario
                    if 0.75 <= sim < 0.92:
                        vector_candidates.append((code, sim))
            except Exception as e:
                print(f"Error al buscar similitud de vectores en historial: {e}")
                
        # Ordenar candidatos por mayor similitud
        vector_candidates.sort(key=lambda x: x[1], reverse=True)
        # Quedarse con los 3 mejores
        vector_candidates = vector_candidates[:3]

    if best_similarity >= 0.92 and best_match_item:
        match_code = best_match_item.get('codigo')
        print(f"[VECTOR MATCH] Coincidencia por vector de similitud: {best_similarity:.4f} con el código '{match_code}'. Bypasseando Gemini.")
        product_data = get_product_by_code(match_code)
        if product_data:
            product_data['mode'] = 'VECTOR_EXACT_MATCH'
            product_data['type'] = 'exact'
            product_data['image_path'] = best_match_item.get('image_path', '')
            product_data['vector_similarity'] = best_similarity
            catalog_name, page_num = find_page_for_code(match_code)
            if catalog_name and page_num:
                product_data['catalog_page_url'] = f"/api/catalog_page/{catalog_name}/{page_num}"
            return jsonify(product_data)

    # Guardar la imagen en el directorio de entrenamiento con un nombre único para el Feedback Loop
    import time
    os.makedirs('assets/entrenamiento', exist_ok=True)
    temp_filename = f"img_{int(time.time())}_{random.randint(1000, 9999)}"
    ext = ".jpg"
    if file.filename.lower().endswith('.png'):
        ext = ".png"
    elif file.filename.lower().endswith('.gif'):
        ext = ".gif"
    elif file.filename.lower().endswith('.webp'):
        ext = ".webp"
    
    image_path = f"assets/entrenamiento/{temp_filename}{ext}"
    try:
        with open(image_path, 'wb') as img_f:
            img_f.write(image_bytes)
    except Exception as e:
        print(f"Error al guardar imagen de entrenamiento: {e}")

    # Determinar el tipo mime de la imagen
    mime_type = 'image/jpeg'
    if file.filename.lower().endswith('.png'):
        mime_type = 'image/png'
    elif file.filename.lower().endswith('.gif'):
        mime_type = 'image/gif'
    elif file.filename.lower().endswith('.webp'):
        mime_type = 'image/webp'

    if not gemini_configured:
        print("Gemini no configurado. Retornando error.")
        return jsonify({"error": "La API de Gemini no está configurada en el servidor."}), 500

    try:
        # 1. Cargar configuración de segmentación de páginas
        page_config = load_page_config()
        page_config_text = json.dumps(page_config, indent=2)

        print(f"Procesando imagen '{file.filename}' buscando en los catálogos PDF registrados...")
        
        contents = []
        
        # Añadir referencias globales de los catálogos PDF ya subidos en Gemini Files API
        if catalog_file_names:
            print(f"Incluyendo {len(catalog_file_names)} catálogos PDF en la solicitud de Gemini...")
            contents.extend(catalog_file_names)
        else:
            print("ADVERTENCIA: No hay catálogos PDF globales inicializados en la memoria.")

        # 2. Cargar ejemplos Few-Shot diversificados desde el historial de entrenamiento para el Feedback Loop
        # Cargamos los últimos 10 ejemplos diversificados generales para que Gemini los use como memoria visual
        training_examples = load_diversified_training_examples(limit=10)
        history_rules = []
        if training_examples:
            print(f"Cargando {len(training_examples)} ejemplos de Few-Shot desde el historial...")
            for ex in training_examples:
                ex_path = ex.get('image_path')
                ex_code = ex.get('codigo')
                ex_desc = ex.get('descripcion_visual', 'joyeria')
                
                # Regla de texto para el prompt
                history_rules.append(f"- Código '{ex_code}': {ex_desc}")
                
                # Adjuntar imagen física si existe
                if ex_path and os.path.exists(ex_path):
                    try:
                        with open(ex_path, 'rb') as f:
                            ex_bytes = f.read()
                        
                        ex_mime = 'image/jpeg'
                        if ex_path.lower().endswith('.png'):
                            ex_mime = 'image/png'
                        elif ex_path.lower().endswith('.gif'):
                            ex_mime = 'image/gif'
                        elif ex_path.lower().endswith('.webp'):
                            ex_mime = 'image/webp'
                            
                        contents.append({
                            'mime_type': ex_mime,
                            'data': ex_bytes
                        })
                        contents.append(f"Ejemplo de entrenamiento real: Esta imagen corresponde al artículo con código '{ex_code}'. Características: {ex_desc}")
                    except Exception as err:
                        print(f"Error al cargar imagen de ejemplo {ex_path}: {err}")

        history_rules_text = "\n".join(history_rules) if history_rules else "Ninguno."

        # 3. Añadimos la imagen escaneada actual
        contents.append({
            'mime_type': mime_type,
            'data': image_bytes
        })
        
        contents.append(
            "Debes buscar visualmente el artículo de la imagen escaneada dentro de los catálogos PDF provistos.\n"
            "Debes responder estrictamente en formato JSON con la siguiente estructura:\n"
            "- Si la confianza/similitud calculada entre la imagen escaneada y una pieza del catálogo es IGUAL O MAYOR al 90%:\n"
            "  {\n"
            "    \"estatus\": \"EXITOSO\",\n"
            "    \"codigo_exacto\": \"CODIGO_EXACTO\",\n"
            "    \"opciones_sugeridas\": []\n"
            "  }\n"
            "- Si la confianza/similitud calculada es MENOR al 90%:\n"
            "  {\n"
            "    \"estatus\": \"DUDA\",\n"
            "    \"codigo_exacto\": \"\",\n"
            "    \"opciones_sugeridas\": [\"CODIGO1\", \"CODIGO2\", \"CODIGO3\"]\n"
            "  }\n"
            "Asegúrate de que los códigos de producto devueltos estén escritos exactamente como aparecen impresos al lado de las piezas en el catálogo PDF."
        )
        
        # 4. Configurar instrucciones del sistema y segmentación por categoría
        segmentation_instruction = (
            "REGLAS DE SEGMENTACIÓN POR CONFIGURACIÓN DE PÁGINAS:\n"
            "Para maximizar la precisión de búsqueda visual en el catálogo, primero identifica mentalmente a qué categoría pertenece el artículo escaneado "
            "(ARETE, PIERCING, EARCUFF, ANILLO, PULSERA, COLLAR, GRABABLE, LLAVERO).\n"
            "Si la pieza es personalizable, grabable, o tiene placas metálicas lisas para grabar, clasifícala como 'GRABABLE' o 'LLAVERO'.\n"
            "Utiliza la siguiente configuración de páginas en formato JSON para restringir tu búsqueda visual y de códigos estrictamente a los rangos de páginas indicados:\n"
            f"{page_config_text}\n\n"
            "Restringe tu comparación visual y extracción de códigos estrictamente a esos rangos de páginas para el catálogo respectivo. Si para un catálogo indica 'none', no busques en él."
        )

        # Candidatos sugeridos por el modelo de similitud local
        candidates_instruction = ""
        if vector_candidates:
            candidates_lines = [f"- Código '{code}' (Similitud visual por embedding: {sim*100:.1f}%)" for code, sim in vector_candidates]
            candidates_instruction = (
                "CANDIDATOS POTENCIALES POR SIMILITUD DE EMBEDDINGS LOCAL:\n"
                "Nuestro modelo de similitud visual local sugiere altamente que la pieza escaneada podría ser una de las siguientes:\n"
                + "\n".join(candidates_lines) + "\n"
                "Por favor, revisa visualmente con prioridad estas opciones en el catálogo para ver si coinciden con la pieza escaneada.\n\n"
            )

        print("Consultando a Gemini 3.5 Flash...")
        model = genai.GenerativeModel(
            model_name='gemini-3.5-flash',
            generation_config={"response_mime_type": "application/json"},
            system_instruction=(
                "Eres un asistente experto en reconocimiento visual de joyería para Eyemax.\n"
                "Compara de manera minuciosa la foto de joyería escaneada con las imágenes y las páginas de los dos catálogos PDF provistos.\n"
                "Encuentra la pieza en el catálogo que tenga exactamente la misma forma, color de metal, dijes y características visuales.\n"
                "Extrae el código o Clave escrito en el PDF junto a esa pieza encontrada (ej. AX1362, COL294, etc.).\n\n"
                f"{segmentation_instruction}\n\n"
                f"{candidates_instruction}"
                "MEMORIA DE ENTRENAMIENTO PREVIO (Fotos confirmadas por el usuario):\n"
                "El equipo ha confirmado anteriormente que ciertas imágenes reales corresponden a los siguientes códigos. "
                "Utiliza esta memoria para dar prioridad absoluta a estos códigos si la foto escaneada se asemeja visualmente al ejemplo provisto:\n"
                f"{history_rules_text}\n\n"
                "Reglas estrictas:\n"
                "1. Presta extrema atención al color del metal de la foto. Si es plateada, la clave debe corresponder a la pieza plateada en el PDF. Si es dorada, debe ser la dorada. Respeta siempre las letras o sufijos finales del código (como G para dorado y P para plata).\n"
                "2. Está prohibido inventar códigos. Los códigos que devuelvas deben ser legibles y existir en las páginas de los PDF provistos.\n"
                "3. Si tu nivel de confianza visual en la coincidencia exacta es igual o superior al 90%, establece 'estatus': 'EXITOSO' y pon el código en 'codigo_exacto'.\n"
                "4. Si la imagen es borrosa, tiene reflejos, o no estás 90% seguro de cuál de varias piezas similares es, establece 'estatus': 'DUDA', deja 'codigo_exacto' vacío y pon en 'opciones_sugeridas' los 3 códigos del catálogo que visualmente más se parezcan a la pieza escaneada."
            )
        )
        
        response = model.generate_content(contents)
        increment_query_count()
        raw_text = response.text.strip()
        print(f"Respuesta cruda de Gemini: {raw_text}")
        
        # Parsear respuesta JSON
        try:
            res_data = json.loads(raw_text)
        except Exception as parse_err:
            print(f"Error al parsear respuesta JSON de Gemini: {parse_err}")
            return jsonify({"error": f"La respuesta de la IA no es un JSON válido: {raw_text}"}), 500
 
        estatus = res_data.get("estatus", "").upper()
        if estatus == "EXITOSO":
            code = res_data.get("codigo_exacto", "")
            if not code:
                return jsonify({"error": "La respuesta de la IA no incluyó el código exacto del producto."}), 500
            
            code_clean = clean_detected_code(code)
            product_data = get_product_by_code(code_clean)
            if product_data:
                product_data['mode'] = 'GEMINI_REAL'
                product_data['type'] = 'exact'
                product_data['image_path'] = image_path
                catalog_name, page_num = find_page_for_code(code_clean)
                if catalog_name and page_num:
                    product_data['catalog_page_url'] = f"/api/catalog_page/{catalog_name}/{page_num}"
                return jsonify(product_data)
            else:
                print(f"[GEMINI] Código '{code_clean}' no encontrado en inventario. Retornando vista duda con opciones vacías.")
                return jsonify({
                    "type": "suggestions",
                    "products": [],
                    "image_path": image_path
                })
                
        elif estatus == "DUDA":
            suggestions = res_data.get("opciones_sugeridas", [])
            if not isinstance(suggestions, list):
                suggestions = []
            
            products = []
            for sug_code in suggestions[:3]:
                sug_clean = clean_detected_code(sug_code)
                sug_prod = get_product_by_code(sug_clean)
                if sug_prod:
                    sug_prod['mode'] = 'GEMINI_REAL'
                    products.append(sug_prod)
            
            return jsonify({
                "type": "suggestions",
                "products": products,
                "image_path": image_path
            })
        else:
            # Fallback en caso de estatus inesperado
            code = res_data.get("codigo_exacto") or res_data.get("codigo")
            if code:
                code_clean = clean_detected_code(code)
                product_data = get_product_by_code(code_clean)
                if product_data:
                    product_data['mode'] = 'GEMINI_REAL'
                    product_data['type'] = 'exact'
                    product_data['image_path'] = image_path
                    catalog_name, page_num = find_page_for_code(code_clean)
                    if catalog_name and page_num:
                        product_data['catalog_page_url'] = f"/api/catalog_page/{catalog_name}/{page_num}"
                    return jsonify(product_data)
            
            print(f"[GEMINI] Estatus inesperado o código no encontrado. Retornando vista duda con opciones vacías.")
            return jsonify({
                "type": "suggestions",
                "products": [],
                "image_path": image_path
            })
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error en el proceso de Gemini: {error_msg}")
        if "429" in error_msg or "quota" in error_msg.lower():
            return jsonify({"error": "Límite de cuota de la API de Gemini excedido (Error 429). Por favor, espera un momento antes de volver a escanear o ingresa la clave manualmente."}), 429
        return jsonify({"error": f"Error al procesar la imagen con Gemini: {error_msg}"}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)), 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)), 'sw.js')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    pin = data.get('pin', '').strip()
    if pin == ADMIN_PIN:
        return jsonify({"success": True, "token": f"eyemax_auth_{ADMIN_PIN}"})
    return jsonify({"error": "PIN de acceso incorrecto"}), 401

@app.route('/api/admin/upload_inventory', methods=['POST'])
@admin_required
def admin_upload_inventory():
    if 'file' not in request.files:
        return jsonify({"error": "No se recibió ningún archivo"}), 400
    file = request.files['file']
    if not file.filename.endswith('.xlsx'):
        return jsonify({"error": "El archivo debe ser un Excel .xlsx"}), 400
        
    backup_path = EXCEL_PATH + ".bak"
    # Respaldar
    if os.path.exists(EXCEL_PATH):
        try:
            shutil.copy(EXCEL_PATH, backup_path)
        except Exception as e:
            print(f"Error al respaldar Excel: {e}")
            
    try:
        file.save(EXCEL_PATH)
        # Intentar cargar en memoria para verificar validez
        load_inventory()
        return jsonify({"success": True, "records": len(df_inventario)})
    except Exception as e:
        print(f"Error al cargar nuevo inventario: {e}")
        # Restaurar respaldo
        if os.path.exists(backup_path):
            shutil.copy(backup_path, EXCEL_PATH)
            load_inventory()
        return jsonify({"error": f"Error al procesar el Excel: {str(e)}"}), 500

@app.route('/api/admin/upload_catalog', methods=['POST'])
@admin_required
def admin_upload_catalog():
    if 'file' not in request.files:
        return jsonify({"error": "No se recibió ningún archivo"}), 400
    file = request.files['file']
    catalog_name = request.form.get('catalog_name', '').strip()
    if catalog_name not in ["CATALOGO 1.pdf", "CATALOGO 2.pdf"]:
        return jsonify({"error": "Nombre de catálogo inválido"}), 400
        
    try:
        file.save(catalog_name)
        # Limpiar caché de páginas renderizadas del PDF viejo
        cache_dir = os.path.join(app.root_path, "assets", "cache_paginas")
        if os.path.exists(cache_dir):
            safe_name = catalog_name.replace(" ", "_")
            for f in os.listdir(cache_dir):
                if f.startswith(f"page_{safe_name}_"):
                    try:
                        os.remove(os.path.join(cache_dir, f))
                    except Exception as err:
                        print(f"Error al limpiar caché {f}: {err}")
                        
        # Si Gemini está configurado, re-subir
        if gemini_configured:
            print(f"[ADMIN] Catálogo '{catalog_name}' actualizado. Volviendo a subir a Gemini...")
            initialize_gemini_catalogs()
            
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error al subir catálogo: {e}")
        return jsonify({"error": f"Error al procesar el catálogo: {str(e)}"}), 500

@app.route('/api/admin/config', methods=['GET', 'POST'])
@admin_required
def admin_config():
    config_path = 'config_paginas.json'
    if request.method == 'GET':
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return jsonify(json.load(f))
            except Exception as e:
                return jsonify({"error": f"Error al leer la configuración: {e}"}), 500
        return jsonify({})
    else:
        # POST
        data = request.get_json() or {}
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": f"Error al guardar la configuración: {e}"}), 500

@app.route('/api/admin/history', methods=['GET'])
@admin_required
def admin_history_get():
    history_file = 'historial_entrenamiento.json'
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except Exception as e:
            return jsonify([])
    return jsonify([])

@app.route('/api/admin/history/<image_hash>', methods=['DELETE'])
@admin_required
def admin_history_delete(image_hash):
    history_file = 'historial_entrenamiento.json'
    if not os.path.exists(history_file):
        return jsonify({"error": "No hay historial disponible"}), 404
        
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        new_history = []
        deleted_count = 0
        for item in history:
            if item.get('image_hash') == image_hash:
                # Borrar archivo físico de la imagen
                path = item.get('image_path')
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as err:
                        print(f"Error al borrar archivo físico de entrenamiento: {err}")
                deleted_count += 1
            else:
                new_history.append(item)
                
        if deleted_count > 0:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(new_history, f, indent=2, ensure_ascii=False)
            return jsonify({"success": True, "deleted_count": deleted_count})
        return jsonify({"error": "Registro no encontrado en el historial"}), 404
    except Exception as e:
        return jsonify({"error": f"Error al eliminar registro: {e}"}), 500

@app.route('/api/catalog_page/<catalog_name>/<int:page_num>', methods=['GET'])
def api_catalog_page(catalog_name, page_num):
    catalog_name = os.path.basename(catalog_name)
    if catalog_name not in ["CATALOGO 1.pdf", "CATALOGO 2.pdf"]:
        return jsonify({"error": "Catálogo no válido"}), 400
        
    cache_dir = os.path.join(app.root_path, "assets", "cache_paginas")
    os.makedirs(cache_dir, exist_ok=True)
    
    safe_name = catalog_name.replace(" ", "_")
    cache_filename = f"page_{safe_name}_{page_num}.jpg"
    cache_filepath = os.path.join(cache_dir, cache_filename)
    
    if os.path.exists(cache_filepath):
        return send_from_directory(cache_dir, cache_filename)
        
    if not os.path.exists(catalog_name):
        return jsonify({"error": f"Archivo de catálogo {catalog_name} no encontrado"}), 404
        
    try:
        doc = fitz.open(catalog_name)
        if page_num < 1 or page_num > len(doc):
            doc.close()
            return jsonify({"error": f"Número de página inválido ({page_num})"}), 400
            
        page = doc[page_num - 1]
        zoom = 150 / 72  # 150 DPI
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix)
        pix.save(cache_filepath)
        doc.close()
        
        return send_from_directory(cache_dir, cache_filename)
    except Exception as e:
        print(f"Error al renderizar página {page_num}: {e}")
        return jsonify({"error": f"Error al procesar PDF: {str(e)}"}), 500



@app.route('/api/search', methods=['GET'])
def search_product():
    q = request.args.get('q', '').strip()
    if q:
        global df_inventario
        if df_inventario is None or df_inventario.empty:
            return jsonify({"products": []})
            
        q_upper = q.upper()
        # Buscar coincidencias en Clave o en el Nombre del artículo
        mask = (df_inventario['Clave'].astype(str).str.upper().str.contains(q_upper, na=False) |
                df_inventario['Nombre del artículo'].astype(str).str.upper().str.contains(q_upper, na=False))
                
        results = df_inventario[mask].head(15)
        
        products = []
        for _, row in results.iterrows():
            product = {
                'CODIGO': str(row.get('Clave', '')).strip(),
                'DESCRIPCION': str(row.get('Nombre del artículo', '')).strip(),
                'MATERIAL': 'ACERO INOXIDABLE',
                'PRECIO venta publico': float(row.get('Precio público', 0.0))
            }
            for col in df_inventario.columns:
                val = row[col]
                if pd.isna(val):
                    if col in ['Precio público', 'Precio mayoreo', 'Almacén general', 'Vista hermosa', 'Paseo']:
                        product[col] = 0.0
                    else:
                        product[col] = ""
                else:
                    if col in ['Precio público', 'Precio mayoreo', 'Almacén general', 'Vista hermosa', 'Paseo']:
                        try:
                            product[col] = float(val)
                        except ValueError:
                            product[col] = 0.0
                    else:
                        if isinstance(val, (int, float)):
                            product[col] = val
                        else:
                            product[col] = str(val)
            products.append(product)
            
        return jsonify({"products": products})
        
    code = request.args.get('code', '').strip()
    if not code:
        return jsonify({"error": "No se proporcionó ningún código o término de búsqueda"}), 400
    
    print(f"\n--- Nueva solicitud de búsqueda de código recibida: {code} ---")
    product_data = get_product_by_code(code)
    if product_data:
        print(f"[BUSQUEDA DIRECTA PANDAS] Código '{code}' encontrado en inventario.")
        product_data['mode'] = 'PANDAS_DIRECT'
        # Buscar la página del catálogo correspondiente
        catalog_name, page_num = find_page_for_code(code)
        if catalog_name and page_num:
            product_data['catalog_page_url'] = f"/api/catalog_page/{catalog_name}/{page_num}"
            print(f"[CATALOGO PAGE] Encontrado en '{catalog_name}', Página {page_num}")
        return jsonify(product_data)
    else:
        print(f"[BUSQUEDA DIRECTA PANDAS] Código '{code}' no encontrado.")
        return jsonify({"error": f"El código '{code}' no existe en el inventario."}), 404

@app.route('/buscar_codigo_manual', methods=['POST'])
def buscar_codigo_manual():
    data = request.get_json() or {}
    code = data.get('codigo', '').strip()
    image_path = data.get('image_path', '').strip()
    
    if not code:
        return jsonify({"error": "No se proporcionó ningún código"}), 400
        
    print(f"\n--- Rescate Manual: Buscando código '{code}' ---")
    product_data = get_product_by_code(code)
    
    if product_data:
        if image_path and os.path.exists(image_path):
            save_to_training_history(image_path, product_data['CODIGO'])
            print(f"[RESCATE MANUAL] Código confirmado: {product_data['CODIGO']} para la imagen: {image_path}")
        else:
            print(f"[RESCATE MANUAL] No se guardó en entrenamiento. Ruta de imagen inválida o vacía: {image_path}")
            
        product_data['mode'] = 'MANUAL_FORCE'
        product_data['type'] = 'exact'
        catalog_name, page_num = find_page_for_code(product_data['CODIGO'])
        if catalog_name and page_num:
            product_data['catalog_page_url'] = f"/api/catalog_page/{catalog_name}/{page_num}"
        return jsonify(product_data)
    else:
        print(f"[RESCATE MANUAL] Código '{code}' no encontrado en el inventario.")
        return jsonify({"error": f"El código '{code}' no existe en el inventario de Excel."}), 404

@app.route('/api/status', methods=['GET'])
def server_status():
    """Endpoint simple para verificar que el servidor esté activo."""
    global gemini_configured
    return jsonify({
        "status": "online",
        "mode": "GEMINI" if gemini_configured else "OFFLINE",
        "inventory_records": len(df_inventario) if df_inventario is not None else 0,
        "free_queries_remaining": max(0, 1500 - get_queries_count())
    })

# Carga global de datos del inventario (necesario para importación WSGI/gunicorn en producción)
load_inventory()
initialize_gemini_catalogs()
try:
    initialize_onnx_model()
    migrate_training_history()
except Exception as e:
    print(f"Advertencia al inicializar ONNX o migrar historial: {e}")


if __name__ == '__main__':
    # Obtener el puerto dinámico (por defecto 8080)
    port = int(os.environ.get("PORT", 8080))
    # Ejecutar servidor Flask en la IP fija local o en la indicada por entorno
    host = os.environ.get("HOST", "192.168.100.78")
    app.run(host=host, port=port, debug=False)

