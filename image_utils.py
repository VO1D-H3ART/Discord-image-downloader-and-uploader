import os
import zipfile
import tempfile

def zip_images(image_paths, output_folder, zip_filename):
    zip_path = os.path.join(output_folder, zip_filename)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for img in image_paths:
            zipf.write(img, os.path.basename(img))
    return zip_path

def unzip_images(zip_path):
    extract_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_dir)
    return extract_dir
