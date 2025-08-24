#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\api_client.py
# JUMLAH BARIS : 534
#######################################################################

import requests
import json
import os
import threading
import time
import random
from flowork_kernel.kernel import Kernel
class ApiClient:
    """
    A client to interact with the local Flowork API server.
    All UI components should use this client instead of calling kernel services directly.
    [REFACTORED V5] Fetches the VariableManager service just-in-time to prevent race conditions.
    [UPGRADED] Added methods for the new Prompt Manager endpoints.
    """
    def __init__(self, base_url="http://localhost:8989/api/v1", kernel=None):
        self.base_url = base_url
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.marketplace_repo_owner = "awenkolayaudico"
        self.marketplace_repo_name = "addon"
        self.marketplace_branch = "main"
        self.kernel = kernel or Kernel.instance
    def _get_auth_headers(self):
        """
        (MODIFIED) Fetches the VariableManager and the API key just-in-time.
        This is the core fix for the "Unauthorized" error.
        """
        headers = {}
        if self.kernel:
            variable_manager = self.kernel.get_service("variable_manager_service")
            if variable_manager:
                api_key = variable_manager.get_variable("FLOWORK_API_KEY")
                if api_key:
                    headers['X-API-Key'] = api_key
        return headers
    def _handle_response(self, response):
        """A helper to handle JSON responses and potential errors."""
        if 200 <= response.status_code < 300:
            if response.status_code == 204 or not response.content:
                return True, {}
            return True, response.json()
        else:
            try:
                error_data = response.json()
                message = error_data.get("error", "Unknown API error")
            except json.JSONDecodeError:
                message = response.text
            return False, message
    def list_datasets(self):
        """Fetches a list of all available training datasets."""
        try:
            response = requests.get(f"{self.base_url}/datasets", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_dataset_data(self, dataset_name: str):
        """Fetches the content of a specific dataset."""
        try:
            response = requests.get(f"{self.base_url}/datasets/{dataset_name}/data", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def create_dataset(self, name: str):
        """Requests the server to create a new, empty dataset."""
        try:
            payload = {"name": name}
            response = requests.post(f"{self.base_url}/datasets", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def add_data_to_dataset(self, dataset_name: str, data_list: list):
        """Sends a list of prompt/response pairs to be added to a dataset."""
        try:
            payload = {"data": data_list}
            response = requests.post(f"{self.base_url}/datasets/{dataset_name}/data", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def start_training_job(self, base_model_id, dataset_name, new_model_name, training_args):
        """Sends a request to start a new fine-tuning job."""
        try:
            payload = {
                "base_model_id": base_model_id,
                "dataset_name": dataset_name,
                "new_model_name": new_model_name,
                "training_args": training_args
            }
            response = requests.post(f"{self.base_url}/training/start", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_training_job_status(self, job_id: str):
        """Fetches the status of an ongoing fine-tuning job."""
        try:
            response = requests.get(f"{self.base_url}/training/status/{job_id}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def start_model_conversion(self, source_model_folder: str, output_gguf_name: str, quantize_method: str):
        """Sends a request to start a new model conversion job."""
        try:
            payload = {
                "source_model_folder": source_model_folder,
                "output_gguf_name": output_gguf_name,
                "quantize_method": quantize_method
            }
            response = requests.post(f"{self.base_url}/models/convert", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def start_model_requantize(self, source_gguf_path: str, output_gguf_name: str, quantize_method: str):
        """Sends a request to start a new model re-quantization job."""
        try:
            payload = {
                "source_gguf_path": source_gguf_path,
                "output_gguf_name": output_gguf_name,
                "quantize_method": quantize_method
            }
            response = requests.post(f"{self.base_url}/models/requantize", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_conversion_status(self, job_id: str):
        """Fetches the status of an ongoing model conversion job."""
        try:
            response = requests.get(f"{self.base_url}/models/convert/status/{job_id}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_agents(self):
        """Fetches a list of all configured AI agents."""
        try:
            response = requests.get(f"{self.base_url}/agents", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def save_agent(self, agent_data: dict):
        """Saves a new or existing agent."""
        try:
            response = requests.post(f"{self.base_url}/agents", json=agent_data, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_agent(self, agent_id: str):
        """Deletes an agent."""
        try:
            response = requests.delete(f"{self.base_url}/agents/{agent_id}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def run_agent(self, agent_id: str, objective: str):
        """Sends a request to start an agent run with a specific objective."""
        try:
            payload = {"objective": objective}
            response = requests.post(f"{self.base_url}/agents/{agent_id}/run", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_agent_run_status(self, run_id: str):
        """Fetches the status of an ongoing agent run."""
        try:
            response = requests.get(f"{self.base_url}/agents/run/{run_id}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def stop_agent_run(self, run_id: str):
        """Sends a request to stop a running agent."""
        try:
            response = requests.post(f"{self.base_url}/agents/run/{run_id}/stop", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_marketplace_ads(self):
        cache_key = "marketplace_ads"
        with self.cache_lock:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < 86400:
                    return True, cached_data
        url = f"https://raw.githubusercontent.com/{self.marketplace_repo_owner}/{self.marketplace_repo_name}/{self.marketplace_branch}/ads.json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            all_ads = response.json()
            selected_ads = random.sample(all_ads, min(6, len(all_ads)))
            with self.cache_lock:
                self.cache[cache_key] = (selected_ads, time.time())
            return True, selected_ads
        except requests.exceptions.RequestException as e:
            return False, f"Network error fetching ads: {e}"
        except (json.JSONDecodeError, ValueError):
            return False, "Failed to parse ads.json."
    def get_marketplace_index(self, component_type: str):
        cache_key = f"marketplace_index_{component_type}"
        with self.cache_lock:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < 86400:
                    return True, cached_data
        folder_map = {
            "modules": "modul",
            "plugins": "plugin",
            "widgets": "widget",
            "presets": "preset",
            "triggers": "triggers",
            "ai_providers": "ai_providers",
            "ai_models": "ai_models"
        }
        folder_name = folder_map.get(component_type)
        if not folder_name:
            return False, f"Unknown component type for marketplace: {component_type}"
        url = f"https://raw.githubusercontent.com/{self.marketplace_repo_owner}/{self.marketplace_repo_name}/{self.marketplace_branch}/{folder_name}/index.json"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 404:
                return True, []
            response.raise_for_status()
            data = response.json()
            with self.cache_lock:
                self.cache[cache_key] = (data, time.time())
            return True, data
        except requests.exceptions.RequestException as e:
            return False, f"Network error fetching marketplace index: {e}"
        except json.JSONDecodeError:
            return False, f"Failed to parse marketplace index.json for {component_type}."
    def trigger_hot_reload(self):
        try:
            payload = {"action": "hot_reload"}
            response = requests.post(f"{self.base_url}/system/actions/hot_reload", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_presets(self):
        cache_key = "presets_list"
        with self.cache_lock:
            if cache_key in self.cache:
                return True, self.cache[cache_key]
        try:
            response = requests.get(f"{self.base_url}/presets", headers=self._get_auth_headers())
            success, data = self._handle_response(response)
            if success:
                preset_names = [item['id'] for item in data] if isinstance(data, list) else []
                with self.cache_lock:
                    self.cache[cache_key] = preset_names
                return success, preset_names
            return success, data
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_preset_data(self, preset_name):
        try:
            response = requests.get(f"{self.base_url}/presets/{preset_name}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def save_preset(self, preset_name, workflow_data):
        with self.cache_lock:
            self.cache.pop("presets_list", None)
        try:
            payload = {"name": preset_name, "workflow_data": workflow_data}
            response = requests.post(f"{self.base_url}/presets", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_preset(self, preset_name):
        with self.cache_lock:
            self.cache.pop("presets_list", None)
        try:
            response = requests.delete(f"{self.base_url}/presets/{preset_name}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_preset_versions(self, preset_name: str):
        try:
            response = requests.get(f"{self.base_url}/presets/{preset_name}/versions", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def load_preset_version(self, preset_name: str, version_filename: str):
        try:
            response = requests.get(f"{self.base_url}/presets/{preset_name}/versions/{version_filename}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_preset_version(self, preset_name: str, version_filename: str):
        try:
            response = requests.delete(f"{self.base_url}/presets/{preset_name}/versions/{version_filename}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_variables(self):
        try:
            response = requests.get(f"{self.base_url}/variables", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def update_variable(self, name, value, is_secret, is_enabled=True, mode=None):
        try:
            payload = {"value": value, "is_secret": is_secret, "is_enabled": is_enabled}
            if mode:
                payload["mode"] = mode
            response = requests.put(f"{self.base_url}/variables/{name}", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def update_variable_state(self, name: str, is_enabled: bool):
        try:
            payload = {"enabled": is_enabled}
            response = requests.patch(f"{self.base_url}/variables/{name}/state", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_variable(self, name):
        try:
            response = requests.delete(f"{self.base_url}/variables/{name}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_components(self, component_type: str, component_id: str = None):
        if not component_id:
            cache_key = f"components_{component_type}"
            with self.cache_lock:
                if cache_key in self.cache:
                    return True, self.cache[cache_key]
        try:
            url = f"{self.base_url}/{component_type}"
            if component_id:
                url += f"/{component_id}"
            response = requests.get(url, headers=self._get_auth_headers())
            success, data = self._handle_response(response)
            if success and not component_id:
                with self.cache_lock:
                    cache_key = f"components_{component_type}"
                    self.cache[cache_key] = data
            return success, data
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def install_component(self, component_type: str, zip_filepath: str):
        with self.cache_lock:
            self.cache.pop(f"components_{component_type}", None)
        try:
            with open(zip_filepath, 'rb') as f:
                headers = self._get_auth_headers()
                files = {'file': (os.path.basename(zip_filepath), f, 'application/zip')}
                response = requests.post(f"{self.base_url}/{component_type}/install", files=files, headers=headers)
            return self._handle_response(response)
        except FileNotFoundError:
            return False, f"Local file not found: {zip_filepath}"
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_component(self, component_type: str, component_id: str):
        with self.cache_lock:
            self.cache.pop(f"components_{component_type}", None)
        try:
            response = requests.delete(f"{self.base_url}/{component_type}/{component_id}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def update_component_state(self, component_type: str, component_id: str, is_paused: bool):
        with self.cache_lock:
            self.cache.pop(f"components_{component_type}", None)
        try:
            payload = {"paused": is_paused}
            response = requests.patch(f"{self.base_url}/{component_type}/{component_id}", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_dashboard_layout(self, tab_id: str):
        try:
            response = requests.get(f"{self.base_url}/uistate/dashboards/{tab_id}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def save_dashboard_layout(self, tab_id: str, layout_data: dict):
        try:
            response = requests.post(f"{self.base_url}/uistate/dashboards/{tab_id}", json=layout_data, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_trigger_definitions(self):
        cache_key = "trigger_definitions"
        with self.cache_lock:
            if cache_key in self.cache:
                return True, self.cache[cache_key]
        try:
            response = requests.get(f"{self.base_url}/triggers/definitions", headers=self._get_auth_headers())
            success, data = self._handle_response(response)
            if success:
                with self.cache_lock:
                    self.cache[cache_key] = data
            return success, data
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_trigger_rules(self):
        try:
            response = requests.get(f"{self.base_url}/triggers/rules", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def create_trigger_rule(self, rule_data: dict):
        try:
            response = requests.post(f"{self.base_url}/triggers/rules", json=rule_data, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def update_trigger_rule(self, rule_id: str, rule_data: dict):
        try:
            response = requests.put(f"{self.base_url}/triggers/rules/{rule_id}", json=rule_data, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_trigger_rule(self, rule_id: str):
        try:
            response = requests.delete(f"{self.base_url}/triggers/rules/{rule_id}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def reload_triggers(self):
        try:
            response = requests.post(f"{self.base_url}/triggers/actions/reload", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_all_settings(self):
        try:
            response = requests.get(f"{self.base_url}/settings", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def save_settings(self, settings_data: dict):
        try:
            response = requests.patch(f"{self.base_url}/settings", json=settings_data, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_tab_session(self):
        try:
            response = requests.get(f"{self.base_url}/uistate/session/tabs", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def save_tab_session(self, tabs_data: list):
        try:
            response = requests.post(f"{self.base_url}/uistate/session/tabs", json=tabs_data, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def open_managed_tab(self, tab_key: str):
        try:
            payload = {"tab_key": tab_key}
            response = requests.post(f"{self.base_url}/ui/actions/open_tab", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def upload_component(self, comp_type: str, component_id: str, description: str, tier: str):
        try:
            payload = {
                "comp_type": comp_type,
                "component_id": component_id,
                "description": description,
                "tier": tier
            }
            response = requests.post(f"{self.base_url}/addons/upload", json=payload, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def upload_model(self, model_path: str, description: str, tier: str):
        try:
            form_data = {
                "description": description,
                "tier": tier,
                "model_id": os.path.basename(model_path).replace('.gguf', '')
            }
            with open(model_path, 'rb') as f:
                files = {'file': (os.path.basename(model_path), f, 'application/octet-stream')}
                response = requests.post(
                    f"{self.base_url}/models/upload",
                    data=form_data,
                    files=files,
                    headers=self._get_auth_headers()
                )
            return self._handle_response(response)
        except FileNotFoundError:
            return False, f"Local model file not found: {model_path}"
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_prompts(self):
        """Fetches the list of all prompt templates."""
        try:
            response = requests.get(f"{self.base_url}/prompts", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_prompt(self, prompt_id: str):
        """Fetches the full details of a single prompt template."""
        try:
            response = requests.get(f"{self.base_url}/prompts/{prompt_id}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def create_prompt(self, prompt_data: dict):
        """Creates a new prompt template."""
        try:
            response = requests.post(f"{self.base_url}/prompts", json=prompt_data, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def update_prompt(self, prompt_id: str, prompt_data: dict):
        """Updates an existing prompt template."""
        try:
            response = requests.put(f"{self.base_url}/prompts/{prompt_id}", json=prompt_data, headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_prompt(self, prompt_id: str):
        """Deletes a prompt template."""
        try:
            response = requests.delete(f"{self.base_url}/prompts/{prompt_id}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_dataset(self, name: str):
        """Requests the server to delete a dataset."""
        try:
            response = requests.delete(f"{self.base_url}/datasets/{name}", headers=self._get_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
