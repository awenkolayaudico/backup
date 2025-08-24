#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\generate_permissions.py
# JUMLAH BARIS : 66
#######################################################################

import os
import json
import base64
import sys
import hashlib
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
SIMULATED_DECRYPTION_KEY = b'flowork-capability-key-for-sim-32'
SIMULATED_PUBLIC_KEY = "flowork-simulated-public-key"
def main():
    """
    Generates the secure permissions.bin and permissions.sig files
    from a human-readable python dictionary.
    This script is intended for developer use during the build process.
    """
    print("--- Generating Secure and Sealed Capability Permissions ---")
    permission_rules = {
        "capabilities": {
            "web_scraping_advanced": "basic",
            "time_travel_debugger": "basic",
            "screen_recorder": "basic",
            "unlimited_api": "basic",
            "preset_versioning": "basic",
            "ai_provider_access": "pro",
            "ai_local_models": "pro",
            "ai_copilot": "pro",
            "marketplace_upload": "pro",
            "video_processing": "pro",
            "ai_architect": "architect",
            "core_compiler": "architect",
            "module_generator": "architect",
            "advanced_security": "enterprise",
            "team_collaboration": "enterprise"
        }
    }
    print(f"Loaded {len(permission_rules['capabilities'])} permission rules to process.")
    rules_json = json.dumps(permission_rules, indent=4)
    encrypted_data = bytes([b ^ SIMULATED_DECRYPTION_KEY[i % len(SIMULATED_DECRYPTION_KEY)] for i, b in enumerate(rules_json.encode('utf-8'))])
    print("Step 1/3: Rules have been encrypted.")
    hasher = hashlib.sha256()
    hasher.update(encrypted_data)
    hasher.update(SIMULATED_PUBLIC_KEY.encode('utf-8'))
    signature = base64.b64encode(hasher.digest()).decode('utf-8')
    print("Step 2/3: Encrypted data has been signed.")
    data_path = os.path.join(project_root, 'data')
    os.makedirs(data_path, exist_ok=True)
    output_bin_path = os.path.join(data_path, 'permissions.bin')
    output_sig_path = os.path.join(data_path, 'permissions.sig')
    with open(output_bin_path, 'wb') as f:
        f.write(encrypted_data)
    with open(output_sig_path, 'w', encoding='utf-8') as f:
        f.write(signature)
    print(f"Step 3/3: Secure files have been generated.")
    print(f"  -> Encrypted rules: {output_bin_path}")
    print(f"  -> Signature file: {output_sig_path}")
    print("\n--- Generation Complete ---")
    print("These files are now ready to be shipped with the application.")
if __name__ == "__main__":
    main()
