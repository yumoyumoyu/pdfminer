try:
    import tkinter
    import tkinterdnd2
    import pdfminer
    import pdf2image
    import pytesseract
    import PIL
    print("All imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
