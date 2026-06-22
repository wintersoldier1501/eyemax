import os
import google.generativeai as genai
from PIL import Image
import io

# Setup key
api_key = "AQ.Ab8RN6K-2W_34Jw6MgIpO7emtU9TyBGqyWfJEgGuPGkQJ1Pfrw"
genai.configure(api_key=api_key)

# Create a small dummy image in memory
img = Image.new('RGB', (100, 100), color = 'red')
buf = io.BytesIO()
img.save(buf, format='JPEG')
image_bytes = buf.getvalue()

try:
    print("Testing multimodal generation with gemini-3.5-flash...")
    model = genai.GenerativeModel('gemini-3.5-flash')
    response = model.generate_content([
        {'mime_type': 'image/jpeg', 'data': image_bytes},
        "Describe what you see in the image in one word."
    ])
    print(f"Success! Response: {response.text.strip()}")
except Exception as e:
    print(f"Multimodal generation failed: {e}")
