import os
import zipfile
from pathlib import Path

# Create a temporary directory to build the structure
temp_dir = "temp_image_library_app"
os.makedirs(temp_dir, exist_ok=True)

# Define the folder structure with empty files
structure = {
    "app.py": "",
    "config.py": "",
    "requirements.txt": "",
    "database.sql": "",
    "uploads": None,  # directory
    "static": {
        "css": {
            "style.css": ""
        },
        "js": {
            "main.js": ""
        }
    },
    "templates": {
        "index.html": ""
    },
    "utils": {
        "__init__.py": "",
        "zip_handler.py": "",
        "excel_reader.py": ""
    }
}

def create_structure(base_path, structure_dict):
    for name, content in structure_dict.items():
        path = os.path.join(base_path, name)
        
        if content is None:  # It's a directory
            os.makedirs(path, exist_ok=True)
        elif isinstance(content, dict):  # It's a directory with contents
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:  # It's a file
            # Create parent directory if needed
            os.makedirs(os.path.dirname(path), exist_ok=True)
            # Create empty file
            with open(path, 'w') as f:
                pass  # Create empty file

# Create the structure
create_structure(temp_dir, structure)

# Create zip file
zip_filename = "image-library-app-structure.zip"
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, temp_dir)
            zipf.write(file_path, arcname)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            arcname = os.path.relpath(dir_path, temp_dir) + '/'
            zipf.write(dir_path, arcname)

# Clean up temporary directory
import shutil
shutil.rmtree(temp_dir)

print(f"Created {zip_filename} with the folder structure and empty files")
