import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from pdf_processor import PDFProcessor

import json
import shutil
from tkinter import filedialog, messagebox

class PDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Processor")
        self.root.geometry("600x400")

        self.config_file = 'config.json'
        self.config = self.load_config()

        # Initialize processor with config paths if they exist
        self.processor = PDFProcessor(
            tesseract_cmd=self.config.get('tesseract_cmd'),
            poppler_path=self.config.get('poppler_path')
        )

        self.create_widgets()

        # Check for external dependencies and prompt if missing
        self.root.after(100, self.check_dependencies)

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def create_widgets(self):
        # Drag and Drop Area
        self.drop_frame = tk.LabelFrame(self.root, text="Drop Area", width=580, height=150)
        self.drop_frame.pack(pady=10, padx=10, fill=tk.X)
        self.drop_frame.pack_propagate(False)

        self.drop_label = tk.Label(self.drop_frame, text="Drag & Drop PDF files here", font=("Helvetica", 16))
        self.drop_label.pack(expand=True, fill=tk.BOTH)

        # Enable Drag and Drop
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.drop_handler)

        # Log Area
        self.log_area = scrolledtext.ScrolledText(self.root, state='disabled', height=10)
        self.log_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Settings Button
        self.settings_btn = tk.Button(self.root, text="Settings / Check Dependencies", command=self.check_dependencies)
        self.settings_btn.pack(pady=5)

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def check_dependencies(self):
        self.log("Checking dependencies...")
        
        # Check Tesseract
        tess_ok = False
        if self.config.get('tesseract_cmd') and os.path.exists(self.config.get('tesseract_cmd')):
            tess_ok = True
        elif shutil.which('tesseract'):
            tess_ok = True
        # Also check common paths if not found (brief check)
        elif self.processor.autodetect_tesseract(): 
             # We rely on processor's autodetect logic at runtime, but for UI feedback:
             tess_ok = True
        
        if not tess_ok:
            if messagebox.askyesno("Dependency Missing", "Tesseract OCR not found. Do you want to locate tesseract.exe manually?"):
                path = filedialog.askopenfilename(title="Select tesseract.exe", filetypes=[("Executable", "*.exe")])
                if path:
                    self.config['tesseract_cmd'] = path
                    self.save_config()
                    # Re-init processor
                    self.processor = PDFProcessor(
                        tesseract_cmd=self.config.get('tesseract_cmd'), 
                        poppler_path=self.config.get('poppler_path')
                    )
                    self.log(f"Configured Tesseract: {path}")

        # Check Poppler
        poppler_ok = False
        # Poppler check usually looks for pdftoppm or similar in path or configured path
        current_poppler = self.config.get('poppler_path')
        if current_poppler and os.path.exists(os.path.join(current_poppler, 'pdftoppm.exe')):
            poppler_ok = True
        elif shutil.which('pdftoppm'):
             poppler_ok = True
        
        if not poppler_ok:
             if messagebox.askyesno("Dependency Missing", "Poppler 'bin' directory not found. Do you want to locate it manually?\n(Select the folder containing pdftoppm.exe)"):
                path = filedialog.askdirectory(title="Select Poppler bin directory")
                if path:
                    # Validate
                    if os.path.exists(os.path.join(path, 'pdftoppm.exe')):
                        self.config['poppler_path'] = path
                        self.save_config()
                        self.processor = PDFProcessor(
                            tesseract_cmd=self.config.get('tesseract_cmd'), 
                            poppler_path=self.config.get('poppler_path')
                        )
                        self.log(f"Configured Poppler: {path}")
                    else:
                        messagebox.showerror("Invalid Path", "The selected directory does not contain pdftoppm.exe.")

    def drop_handler(self, event):
        files = self.root.tk.splitlist(event.data)
        for file_path in files:
            if file_path.lower().endswith('.pdf'):
                self.log(f"Processing: {file_path}")
                # Run in a separate thread
                threading.Thread(target=self.process_file, args=(file_path,), daemon=True).start()
            else:
                self.log(f"Skipped non-PDF file: {file_path}")

    def process_file(self, file_path):
        try:
            output_dir = self.processor.process_pdf(file_path)
            self.root.after(0, lambda: self.log(f"Success! Output saved to: {output_dir}"))
            self.root.after(0, lambda: messagebox.showinfo("Done", f"Processed: {os.path.basename(file_path)}"))
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.log(f"Error: {error_msg}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to process {os.path.basename(file_path)}\n{error_msg}"))

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFApp(root)
    root.mainloop()
