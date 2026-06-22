import os
import sys
import urllib.request
import subprocess

def run_test():
    # 1. Install onnxruntime
    print("Installing onnxruntime...")
    subprocess.run([sys.executable, "-m", "pip", "install", "onnxruntime"], capture_output=True)
    
    # Try importing
    try:
        import onnxruntime as ort
        import numpy as np
        from PIL import Image
        print("Imports successful!")
    except Exception as e:
        print("Failed to import libraries:", e)
        return

    # 2. Download ONNX model
    model_url = "https://huggingface.co/onnxmodelzoo/mobilenetv2-12/resolve/main/mobilenetv2-12.onnx"
    model_path = "scratch/mobilenetv2.onnx"
    
    if not os.path.exists(model_path):
        print(f"Downloading MobileNetV2 model from: {model_url}")
        try:
            urllib.request.urlretrieve(model_url, model_path)
            print("Download successful!")
        except Exception as e:
            print("Failed to download model:", e)
            return
    else:
        print("Model already exists locally.")

    # 3. Load model and run inference on an image
    print("Loading ONNX session...")
    try:
        session = ort.InferenceSession(model_path)
        print("Model loaded successfully!")
    except Exception as e:
        print("Failed to load model session:", e)
        return

    # Test image preprocessing
    test_img_path = "assets/logo.png"
    if not os.path.exists(test_img_path):
        # Fallback to any file or generate a dummy image
        img = Image.new('RGB', (224, 224), color = (73, 109, 137))
    else:
        img = Image.open(test_img_path).convert('RGB')
        
    # Resize and normalize
    img_resized = img.resize((224, 224), Image.Resampling.BILINEAR)
    img_data = np.array(img_resized).astype(np.float32)
    
    # Transpose to Channel-First (3, 224, 224) and normalize (ImageNet standard)
    img_data = img_data.transpose(2, 0, 1) # HWC to CHW
    
    # Normalize with standard ImageNet mean and std dev
    mean = np.array([0.485, 0.456, 0.406]).reshape(3, 1, 1)
    std = np.array([0.229, 0.224, 0.225]).reshape(3, 1, 1)
    img_data = (img_data / 255.0 - mean) / std
    
    # Add batch dimension (1, 3, 224, 224)
    input_data = np.expand_dims(img_data, axis=0).astype(np.float32)
    
    # Run session
    input_name = session.get_inputs()[0].name
    print(f"Running inference with input name: {input_name}")
    try:
        outputs = session.run(None, {input_name: input_data})
        vector = outputs[0]
        print(f"Inference successful! Output shape: {vector.shape}")
        # Print a small part of the vector
        print("First 10 values:", vector[0][:10])
    except Exception as e:
        print("Failed during inference:", e)

if __name__ == "__main__":
    run_test()
