#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\create_fingerprint.py
# JUMLAH BARIS : 72
#######################################################################

import os
import sys
import json
import hashlib
ITEMS_TO_IGNORE = [
    '.git',
    '.github',
    '__pycache__',
    'data', # Folder data pengguna tidak perlu di-update
    'repo_upload_temp',
    'repo_temp',
    'file_fingerprints.json', # Abaikan file sidik jari itu sendiri
    '.gitignore',
    'start_flowork_DEBUG.bat',
    'start_flowork_SMART.bat',
    'uploader.py',
    'updater.py',
    'downloader.py',
    'run_uploader.bat',
    'run_cleaner.bat',
    'run_downloader_admin.bat'
]
FINGERPRINT_FILENAME = "file_fingerprints.json"
def calculate_sha256(file_path):
    """Menghitung hash SHA-256 dari sebuah file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except IOError:
        print(f"  [WARN] Could not read file, skipping: {os.path.basename(file_path)}")
        return None
def generate_fingerprints(target_directory):
    """Membuat sidik jari untuk semua file di dalam direktori target."""
    print(f"  Scanning directory: {target_directory}")
    fingerprints = {}
    for root, dirs, files in os.walk(target_directory):
        dirs[:] = [d for d in dirs if d not in ITEMS_TO_IGNORE]
        for name in files:
            if name in ITEMS_TO_IGNORE:
                continue
            file_path = os.path.join(root, name)
            relative_path = os.path.relpath(file_path, target_directory).replace('\\', '/')
            file_hash = calculate_sha256(file_path)
            if file_hash:
                fingerprints[relative_path] = file_hash
    output_path = os.path.join(target_directory, FINGERPRINT_FILENAME)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fingerprints, f, indent=4, sort_keys=True)
        print(f"  [SUCCESS] Fingerprint file created with {len(fingerprints)} entries.")
        print(f"  -> Saved to: {output_path}")
    except IOError as e:
        print(f"  [ERROR] Could not write fingerprint file: {e}")
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_fingerprint.py <directory_to_scan>")
        sys.exit(1)
    scan_path = sys.argv[1]
    if not os.path.isdir(scan_path):
        print(f"Error: Provided path is not a valid directory: {scan_path}")
        sys.exit(1)
    generate_fingerprints(scan_path)
