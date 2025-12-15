import shutil
import os
import sys

def check_command(cmd):
    path = shutil.which(cmd)
    if path:
        print(f"[OK] '{cmd}' found at: {path}")
        return True
    else:
        print(f"[MISSING] '{cmd}' not found in PATH.")
        return False

def check_common_paths():
    print("\nChecking common install locations...")
    
    # Tesseract
    common_tesseract = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe")
    ]
    found_tesseract = None
    for p in common_tesseract:
        if os.path.exists(p):
            print(f"[FOUND] Tesseract binary found at: {p}")
            found_tesseract = p
            break
    
    if not found_tesseract:
        print("[NOT FOUND] Tesseract binary not found in common locations.")

    # Poppler
    # Poppler is harder as it's often manual. Checking regular Program Files folders for 'poppler' keyword might be too slow or permission heavy.
    # We will just rely on explicit PATH check above for poppler tools like pdftoppm or pdfinfo.
    
    return found_tesseract

print("--- Diagnostic Start ---")
tesseract_ok = check_command("tesseract")
poppler_ok = check_command("pdftoppm") # Part of poppler

install_tesseract_path = None
if not tesseract_ok:
    install_tesseract_path = check_common_paths()

if not tesseract_ok or not poppler_ok:
    print("\n--- Summary ---")
    if not tesseract_ok:
        if install_tesseract_path:
            print(f"Tesseract is installed at '{install_tesseract_path}' but not in PATH.")
            print("Action: Add it to PATH or configure the app to use this path.")
        else:
            print("Tesseract does not appear to be installed (or is in a custom location).")
            print("Please install Tesseract OCR.")
    
    if not poppler_ok:
        print("Poppler (pdftoppm) is not in PATH.")
        print("Please install Poppler and add its 'bin' directory to PATH.")
else:
    print("\nBoth Tesseract and Poppler appear to be correctly in PATH.")

print("--- Diagnostic End ---")
