import os
import logging
from pdfminer.high_level import extract_text
import pdf2image
import pytesseract
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PDFProcessor:
    def __init__(self, tesseract_cmd=None, poppler_path=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        if poppler_path:
            self.poppler_path = poppler_path
        else:
            self.poppler_path = None # Rely on PATH

    def autodetect_tesseract(self):
        """Attempts to find Tesseract in common Windows locations."""
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def process_pdf(self, file_path):
        """
        Orchestrates the processing of a single PDF file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Auto-detect Tesseract if not set and not in PATH
        if pytesseract.pytesseract.tesseract_cmd == 'tesseract':
            import shutil
            if not shutil.which('tesseract'):
                detected = self.autodetect_tesseract()
                if detected:
                    pytesseract.pytesseract.tesseract_cmd = detected
                    logging.info(f"Auto-detected Tesseract at: {detected}")

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = os.path.join(os.path.dirname(file_path), base_name)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Created output directory: {output_dir}")

        # 1. Extract Text
        logging.info("Attempting text extraction...")
        text = self.extract_text_content(file_path)
        
        # 2. Save Text
        md_path = os.path.join(output_dir, f"{base_name}.md")
        self.save_to_markdown(text, md_path)
        logging.info(f"Saved text to: {md_path}")

        # 3. Convert to Images
        logging.info("Converting pages to images...")
        self.convert_to_images(file_path, output_dir)
        logging.info("Image conversion complete.")
        
        return output_dir

    def extract_text_content(self, file_path):
        """
        Extracts text using pdfminer. If empty, falls back to OCR.
        """
        try:
            text = extract_text(file_path)
        except Exception as e:
            logging.error(f"pdfminer failed: {e}")
            text = ""

        if not text or not text.strip():
            logging.info("No text found with pdfminer. Falling back to OCR...")
            return self.ocr_pdf(file_path)
        
        return text

    def ocr_pdf(self, file_path):
        """
        Converts PDF to images and runs OCR on them.
        """
        # Check available languages once
        try:
             langs = pytesseract.get_languages()
             if 'jpn' not in langs and 'jpn_vert' not in langs:
                 raise RuntimeError("Japanese language data ('jpn') for Tesseract is not installed.\nPlease run the Tesseract installer again and select 'Japanese' in 'Additional script data'.")
        except Exception as e:
             # If we can't check langs, we proceed but log warning, unless it was the runtime error we just raised
             if "Japanese language data" in str(e):
                 raise e
             logging.warning(f"Could not check installed languages: {e}")

        text_content = []
        try:
            # We explicitly pass poppler_path here if set
            images = pdf2image.convert_from_path(file_path, poppler_path=self.poppler_path)
            for i, image in enumerate(images):
                logging.info(f"OCR processing page {i+1}...")
                # Prioritize Japanese: jpn+eng
                page_text = pytesseract.image_to_string(image, lang='jpn+eng') 
                text_content.append(f"--- Page {i+1} ---\n{page_text}")
        except Exception as e:
            logging.error(f"OCR failed: {e}")
            # Reraise specific error so UI can handle it
            raise RuntimeError(f"OCR Error: {e}\nCheck Tesseract/Poppler paths.")
        
        return "\n\n".join(text_content)

    def save_to_markdown(self, text, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

    def convert_to_images(self, file_path, output_dir):
        """
        Converts all pages to 300 DPI JPG images.
        """
        try:
            # We convert in chunks or directly if not too large. 
            # uuid generation is automatic if we use output_folder? No, pdf2image saves to temp or returns list.
            # Ideally avoid loading all into memory for huge PDFs, but for now standard approach.
            images = pdf2image.convert_from_path(file_path, dpi=300, fmt='jpeg', poppler_path=self.poppler_path)
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            for i, image in enumerate(images):
                image_path = os.path.join(output_dir, f"{base_name}_page_{i+1:03d}.jpg")
                image.save(image_path, 'JPEG')
        except Exception as e:
            logging.error(f"Image conversion failed: {e}")
            raise e
