#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\generate_integrity_manifest.py
# JUMLAH BARIS : 75
#######################################################################

import os
import json
import hashlib
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
def calculate_sha256(file_path):
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None
def main():
    """
    [MODIFIED V2] Scans files and directories specified in 'lock.txt' to generate
    a flexible core integrity manifest.
    """
    print("--- Generating CORE ENGINE integrity manifest from lock.txt ---")
    ignore_list = [
        "__pycache__", ".pyc", ".git", "temp_uploads",
        "core_integrity.json",
        "addon_integrity.json",
        "data", "logs", ".vscode", ".idea",
        "lock.txt" # ADDED: Ensure the lock file itself is not included in the hash.
    ]
    integrity_manifest = {}
    lock_file_path = os.path.join(project_root, 'lock.txt')
    if not os.path.exists(lock_file_path):
        print(f"\n[FATAL ERROR] 'lock.txt' not found in the project root.")
        print("Please create it to specify which core files and directories to protect.")
        sys.exit(1)
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        paths_to_lock = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    print(f"Found {len(paths_to_lock)} entries to process in lock.txt...")
    for relative_path_entry in paths_to_lock:
        full_path = os.path.join(project_root, relative_path_entry)
        if not os.path.exists(full_path):
            print(f"  -> WARNING: Path '{relative_path_entry}' from lock.txt not found. Skipping.")
            continue
        if os.path.isdir(full_path):
            print(f"Scanning protected directory: {relative_path_entry}...")
            for root, dirs, files in os.walk(full_path):
                dirs[:] = [d for d in dirs if d not in ignore_list]
                for file in files:
                    if any(ignored in file for ignored in ignore_list):
                        continue
                    file_path = os.path.join(root, file)
                    file_hash = calculate_sha256(file_path)
                    if file_hash:
                        relative_path_for_manifest = os.path.relpath(file_path, project_root).replace(os.sep, '/')
                        integrity_manifest[relative_path_for_manifest] = file_hash
        elif os.path.isfile(full_path):
            print(f"Scanning protected file: {relative_path_entry}...")
            file_hash = calculate_sha256(full_path)
            if file_hash:
                relative_path_for_manifest = os.path.relpath(full_path, project_root).replace(os.sep, '/')
                integrity_manifest[relative_path_for_manifest] = file_hash
    output_path = os.path.join(project_root, "core_integrity.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(integrity_manifest, f, indent=4, sort_keys=True)
    print(f"\nSuccessfully generated 'core_integrity.json' with {len(integrity_manifest)} entries based on lock.txt.")
    print("This manifest now contains hashes for assets specified in lock.txt.")
if __name__ == "__main__":
    main()
