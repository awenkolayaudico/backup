#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\lock_addons.py
# JUMLAH BARIS : 147
#######################################################################

import os
import json
import hashlib
import sys
import subprocess
import shutil
import platform
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
ignore_files_relative = {
    "plugins/system_diagnostics_plugin/diagnostics_config.json",
    "plugins/system_diagnostics_plugin/scanners/ai_copilot_health_scan.py",
    "plugins/system_diagnostics_plugin/scanners/cache_integrity_scan.py",
    "plugins/system_diagnostics_plugin/scanners/core_compiler_health_scan.py",
    "plugins/system_diagnostics_plugin/scanners/core_integrity_scan.py",
    "plugins/system_diagnostics_plugin/scanners/data_preview_readiness_scan.py",
    "plugins/system_diagnostics_plugin/scanners/manifest_completeness_scan.py",
    "plugins/system_diagnostics_plugin/scanners/manifest_mismatch_scan.py",
    "plugins/system_diagnostics_plugin/scanners/marketplace_integrity_scan.py",
    "plugins/system_diagnostics_plugin/scanners/phase_one_integrity_scan.py",
    "plugins/system_diagnostics_plugin/scanners/tier_attribute_scan.py",
}
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
    [V3] Scans addon directories based on lockplugin.txt and encode.txt.
    - lockplugin.txt: Compiles .py to .awenkaudico and deletes the source.
    - encode.txt: Hashes .py files for integrity but leaves them as source.
    """
    print("--- Starting Flexible Addon Locking Process (V3) ---")
    try:
        with open(os.path.join(project_root, 'lockplugin.txt'), 'r', encoding='utf-8') as f:
            locked_components = {line.strip() for line in f if line.strip() and not line.startswith('#')}
        print(f"Found {len(locked_components)} components to LOCK (compile and delete source).")
        with open(os.path.join(project_root, 'encode.txt'), 'r', encoding='utf-8') as f:
            encoded_components = {line.strip() for line in f if line.strip() and not line.startswith('#')}
        print(f"Found {len(encoded_components)} components to ENCODE (hash source only).")
    except FileNotFoundError as e:
        print(f"\n[FATAL ERROR] Configuration file missing: {e.filename}")
        print("Please create both 'lockplugin.txt' and 'encode.txt' in the project root.")
        sys.exit(1)
    python_executable = sys.executable
    print(f"Using Python executable from current environment: {python_executable}")
    try:
        subprocess.run([python_executable, '-m', 'nuitka', '--version'], check=True, capture_output=True)
        print("Nuitka installation confirmed in the current environment.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n[FATAL ERROR] Nuitka is not installed or accessible in the current Python environment.")
        print("Please ensure you are running this script within the correct Poetry environment.")
        print("Correct command: 'poetry run python scripts/lock_addons.py'")
        sys.exit(1)
    addon_dirs = ['modules', 'plugins', 'widgets', 'triggers']
    integrity_manifest = {}
    for addon_dir in addon_dirs:
        full_dir_path = os.path.join(project_root, addon_dir)
        if not os.path.isdir(full_dir_path):
            continue
        print(f"\nScanning directory: '{addon_dir}'...")
        for component_id in os.listdir(full_dir_path):
            component_path = os.path.join(full_dir_path, component_id)
            if not os.path.isdir(component_path) or component_id == '__pycache__':
                continue
            should_lock = component_id in locked_components
            should_encode = component_id in encoded_components
            if not should_lock and not should_encode:
                print(f"  - SKIPPING: '{component_id}' is not in lockplugin.txt or encode.txt.")
                continue
            action_type = "LOCKED" if should_lock else "ENCODED"
            print(f"  -> Processing component ({action_type}): {component_id}")
            manifest_path = os.path.join(component_path, 'manifest.json')
            if not os.path.exists(manifest_path):
                print(f"    - WARNING: 'manifest.json' not found. Skipping.")
                continue
            if should_lock:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                entry_point = manifest.get("entry_point")
                if not entry_point:
                    print(f"    - INFO: No 'entry_point' found for locking. Hashing files as-is.")
                else:
                    module_filename, class_name = entry_point.split('.')
                    source_file_path = os.path.join(component_path, f"{module_filename}.py")
                    if os.path.exists(source_file_path):
                        source_relative_path = os.path.relpath(source_file_path, project_root).replace(os.sep, '/')
                        if source_relative_path in ignore_files_relative:
                            print(f"    - SKIPPED COMPILATION: Ignoring '{os.path.basename(source_file_path)}' as per ignore list.")
                        else:
                            print(f"    - Compiling '{os.path.basename(source_file_path)}' with Nuitka...")
                            package_name_to_include = addon_dir
                            command = [
                                python_executable, '-m', 'nuitka', '--module', source_file_path,
                                '--output-dir=' + component_path, '--remove-output', '--plugin-enable=tk-inter',
                                f'--include-package={package_name_to_include}'
                            ]
                            try:
                                result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=project_root)
                                compiled_file = next((f for f in os.listdir(component_path) if f.startswith(module_filename) and (f.endswith('.pyd') or f.endswith('.so'))), None)
                                if compiled_file:
                                    compiled_file_path = os.path.join(component_path, compiled_file)
                                    target_path = os.path.join(component_path, f"{module_filename}.awenkaudico")
                                    if os.path.exists(target_path): os.remove(target_path)
                                    shutil.move(compiled_file_path, target_path)
                                    print(f"    - SUCCESS: Compiled and renamed to '{os.path.basename(target_path)}'")
                                    os.remove(source_file_path)
                                    print(f"    - SECURED: Removed source file '{os.path.basename(source_file_path)}'")
                                else:
                                    print(f"    - ERROR: Nuitka ran, but compiled file could not be found.")
                            except subprocess.CalledProcessError as e:
                                print(f"    - FATAL ERROR: Nuitka compilation failed for {component_id}.")
                                print(f"------ NUITKA STDERR ------\n{e.stderr}\n---------------------------")
                                continue
            print(f"    - Hashing final component files...")
            for root, _, files in os.walk(component_path):
                if "__pycache__" in root:
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path_for_check = os.path.relpath(file_path, project_root).replace(os.sep, '/')
                    if relative_path_for_check in ignore_files_relative:
                        print(f"    - SKIPPED HASHING: Ignoring '{file}' as per ignore list.")
                        continue
                    file_hash = calculate_sha256(file_path)
                    if file_hash:
                        integrity_manifest[relative_path_for_check] = file_hash
    output_path = os.path.join(project_root, "addon_integrity.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(integrity_manifest, f, indent=4, sort_keys=True)
    print(f"\n\n--- Addon Processing Complete ---")
    print(f"Successfully generated 'addon_integrity.json' with {len(integrity_manifest)} entries.")
if __name__ == "__main__":
    main()
