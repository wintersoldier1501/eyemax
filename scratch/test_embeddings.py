import os
import google.generativeai as genai

# Load API Key from .env
if os.path.exists('.env'):
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip("'").strip('"')

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("API Key not found in env")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
try:
    for model in genai.list_models():
        if 'embed' in model.name.lower():
            print(f"Model: {model.name}, Supported Methods: {model.supported_generation_methods}")
except Exception as e:
    print("Error listing models:", e)
