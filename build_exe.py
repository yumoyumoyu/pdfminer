import PyInstaller.__main__
import os

print("Starting build process...")

# Define build arguments
args = [
    'main.py',                       # Script to convert
    '--name=PDFProcessor',           # Name of the executable
    '--onefile',                     # Create a single executable
    '--noconsole',                   # Do not show console window
    '--collect-all=tkinterdnd2',     # Collect tkinterdnd2 package data
    '--clean',                       # Clean cache
    '--noconfirm',                   # Replace output directory without asking
]

# Run PyInstaller
PyInstaller.__main__.run(args)

print("Build complete. Check the 'dist' folder.")
