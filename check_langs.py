import pytesseract
import json
import os
import shutil

# Try to load config to get the user-specified path
config_file = 'config.json'
tesseract_cmd = None

if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            tesseract_cmd = config.get('tesseract_cmd')
    except:
        pass

if not tesseract_cmd:
    # Try default or auto-detect logic from pdf_processor
    if shutil.which('tesseract'):
        tesseract_cmd = 'tesseract'
    else:
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                tesseract_cmd = path
                break

if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    print(f"Using Tesseract at: {tesseract_cmd}")
    try:
        langs = pytesseract.get_languages()
        print("Installed Languages:", langs)
        if 'jpn' in langs:
            print("[OK] 'jpn' (Japanese) is installed.")
        else:
            print("[MISSING] 'jpn' (Japanese) is NOT installed.")
    except Exception as e:
        print(f"Error getting languages: {e}")
else:
    print("Could not find Tesseract Configure it in the app first.")
