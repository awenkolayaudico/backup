#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\integrity_checker_service\integrity_checker_service.py
# JUMLAH BARIS : 61
#######################################################################

import os
import json
import hashlib
from ..base_service import BaseService
class IntegrityCheckerService(BaseService):
    """
    Implements the "Benteng Baja" (Steel Fortress) strategy.
    [V3] Now performs a two-layer check. It loads the core manifest and
    also loads the addon manifest if it exists, merging them for a full system verification.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.core_manifest_path = os.path.join(self.kernel.project_root_path, "core_integrity.json")
        self.addon_manifest_path = os.path.join(self.kernel.project_root_path, "addon_integrity.json")
    def _calculate_sha256(self, file_path):
        """Calculates the SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return None
    def verify_core_files(self):
        """
        [MODIFICATION] The main verification method now loads both core and addon manifests.
        It verifies that all files listed in both manifests exist and are unchanged.
        """
        self.kernel.write_to_log("Benteng Baja: Verifying file integrity (Two-Layer Check)...", "INFO")
        full_integrity_manifest = {}
        if not os.path.exists(self.core_manifest_path):
            self.kernel.write_to_log("Benteng Baja: core_integrity.json not found. Skipping check.", "WARN")
            return
        with open(self.core_manifest_path, 'r', encoding='utf-8') as f:
            core_manifest = json.load(f)
            full_integrity_manifest.update(core_manifest)
            self.kernel.write_to_log(f"Benteng Baja: Loaded {len(core_manifest)} core engine file hashes.", "DEBUG")
        if os.path.exists(self.addon_manifest_path):
            try:
                with open(self.addon_manifest_path, 'r', encoding='utf-8') as f:
                    addon_manifest = json.load(f)
                    full_integrity_manifest.update(addon_manifest)
                    self.kernel.write_to_log(f"Benteng Baja: Loaded {len(addon_manifest)} addon file hashes.", "DEBUG")
            except Exception as e:
                self.kernel.write_to_log(f"Benteng Baja: Could not load addon_integrity.json: {e}", "WARN")
        for rel_path, expected_hash in full_integrity_manifest.items():
            full_path = os.path.join(self.kernel.project_root_path, rel_path.replace("/", os.sep))
            current_hash = self._calculate_sha256(full_path)
            if current_hash is None:
                raise RuntimeError(f"Integrity Check Failed: Core file '{rel_path}' is missing from disk but listed in the manifest.")
            if current_hash != expected_hash:
                raise RuntimeError(f"Integrity Check Failed: Core file '{rel_path}' has been modified or is corrupt.")
        self.kernel.write_to_log(f"Benteng Baja: All {len(full_integrity_manifest)} registered files passed integrity check.", "SUCCESS")
