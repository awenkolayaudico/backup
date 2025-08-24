#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\secure_encode.py
# JUMLAH BARIS : 63
#######################################################################

import os
import sys
import subprocess
import shutil
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
def main():
    """
    Main function to run the secure encoding process.
    """
    print("--- Starting Secure Encode Process (Source files will NOT be deleted) ---")
    config_file = 'secure_encode.txt'
    config_file_path = os.path.join(project_root, config_file)
    if not os.path.exists(config_file_path):
        print(f"\n[FATAL ERROR] Configuration file '{config_file}' not found in the project root.")
        print("Please create it and list the relative paths of the .py files you want to compile.")
        sys.exit(1)
    with open(config_file_path, 'r', encoding='utf-8') as f:
        files_to_encode = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    print(f"Found {len(files_to_encode)} critical files to compile from '{config_file}'.")
    python_executable = sys.executable
    print(f"Using Python executable: {python_executable}")
    try:
        subprocess.run([python_executable, '-m', 'nuitka', '--version'], check=True, capture_output=True, text=True)
        print("Nuitka installation confirmed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n[FATAL ERROR] Nuitka is not installed or not found in the current environment's PATH.")
        print("Please ensure you are running this script within your 'poetry shell' environment.")
        sys.exit(1)
    for relative_path in files_to_encode:
        source_file_path = os.path.join(project_root, relative_path.replace('/', os.sep))
        if not os.path.exists(source_file_path):
            print(f"\n[WARNING] File not found, skipping: {relative_path}")
            continue
        print(f"\n-> Compiling: {relative_path}")
        output_directory = os.path.dirname(source_file_path)
        command = [
            python_executable, '-m', 'nuitka', '--module', source_file_path,
            f'--output-dir={output_directory}', '--remove-output', '--plugin-enable=tk-inter'
        ]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=project_root)
            module_name = os.path.splitext(os.path.basename(source_file_path))[0]
            compiled_file = next((f for f in os.listdir(output_directory) if f.startswith(module_name) and (f.endswith('.pyd') or f.endswith('.so'))), None)
            if compiled_file:
                print(f"  [SUCCESS] Compiled successfully -> {compiled_file}")
                print(f"  [INFO] Original source file '{os.path.basename(source_file_path)}' was intentionally kept.")
            else:
                print(f"  [ERROR] Nuitka ran, but the compiled output file could not be found in '{output_directory}'.")
        except subprocess.CalledProcessError as e:
            print(f"  [FATAL ERROR] Nuitka compilation failed for {relative_path}.")
            print(f"  ------ NUITKA STDERR ------\n{e.stderr}\n  ---------------------------")
            continue # Continue to the next file
    print("\n--- Secure Encode Process Finished ---")
if __name__ == "__main__":
    main()
