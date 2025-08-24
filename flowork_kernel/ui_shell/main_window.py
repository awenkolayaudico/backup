#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\main_window.py
# JUMLAH BARIS : 329
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk, Menu, messagebox, Toplevel, Label, Button
from tkinter import filedialog
import uuid
import logging
import datetime
import shutil
import os
import json
import threading
import time
from flowork_kernel.ui_shell.custom_widgets.draggable_notebook import DraggableNotebook
from flowork_kernel.ui_shell.workflow_editor_tab import WorkflowEditorTab
from .ui_components.menubar_manager import MenubarManager
from .popups.PopupManager import PopupManager
from .lifecycle.AppLifecycleHandler import AppLifecycleHandler
import webbrowser
from flowork_kernel.exceptions import PermissionDeniedError
class MainWindow(ttk.Window):
    def __init__(self, kernel_instance):
        super().__init__(themename="darkly")
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.title(self.loc.get('app_title'))
        self.geometry("1280x800")
        self.workflow_editor_tab = None
        self.main_menus ={}
        self.menubar_manager = MenubarManager (self, self.kernel)
        self.popup_manager = PopupManager(self, self.kernel)
        self.lifecycle_handler = AppLifecycleHandler(self, self.kernel)
        try:
            self.recorder_service = self.kernel.get_service("screen_recorder_service")
        except PermissionDeniedError:
            self.kernel.write_to_log("Screen Recorder feature disabled due to insufficient license tier.", "WARN") # English Log
            self.recorder_service = None # Set to None if permission is denied
        self.is_ui_recording = False
        self.record_start_time = None
        self.record_timer_job = None
        self.create_widgets()
        self._create_status_bar()
        self._subscribe_to_events()
        self.tab_manager = self.kernel.get_service("tab_manager_service")
        if self.tab_manager:
            self.tab_manager.set_ui_handles(self, self.notebook)
            self.tab_manager.load_session_state()
        else:
            self.kernel.write_to_log("CRITICAL: TabManagerService not found. UI cannot function.", "CRITICAL") # English Log
            messagebox.showerror(self.loc.get('fatal_error_title', fallback="Fatal Error"), self.loc.get('tab_manager_load_error', fallback="TabManagerService could not be loaded. The application cannot continue."))
            self.destroy()
            return
        self.apply_manual_styles()
        self.protocol("WM_DELETE_WINDOW", self.lifecycle_handler.on_closing_app)
        self.menubar_manager.build_menu()
        self.after(5000, lambda: self.popup_manager.show_notification(
            self.loc.get('notification_ready_title', fallback="Flowork is Ready!"),
            self.loc.get('notification_ready_message', fallback="Welcome to the future of automation."),
            "SUCCESS")
        )
    def handle_license_activation_request(self):
        license_service = self.kernel.get_service("license_manager_service")
        if not license_service:
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), self.loc.get('service_unavailable_error', service_name="License Manager"))
            return
        filepath = filedialog.askopenfilename(
            title=self.loc.get('select_license_file_title', fallback="Select Your license.seal File"),
            filetypes=[(self.loc.get('license_seal_filetype', fallback="License Seal File"), "*.seal")]
        )
        if not filepath:
            self.kernel.write_to_log("License activation cancelled by user.", "WARN") # English Log
            return
        threading.Thread(target=license_service.activate_license_from_file, args=(filepath,), daemon=True).start()
    def handle_license_deactivation_request(self):
        license_service = self.kernel.get_service("license_manager_service")
        if not license_service:
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), self.loc.get('service_unavailable_error', service_name="License Manager"))
            return
        if messagebox.askyesno(
            self.loc.get('settings_license_deactivate_confirm_title', fallback="Confirm Deactivation"),
            self.loc.get('settings_license_deactivate_confirm_message', fallback="Are you sure? This will release the license from this computer."),
            parent=self
        ):
            threading.Thread(target=license_service.deactivate_license_on_server, daemon=True).start()
    def _create_status_bar(self):
        self.status_bar = ttk.Frame(self, height=30, bootstyle="secondary")
        self.status_bar.pack(side="bottom", fill="x", padx=2, pady=(0, 2))
        self.status_bar.pack_propagate(False)
        self.status_label = ttk.Label(self.status_bar, text=self.loc.get('status_bar_ready', fallback="Ready."), anchor="w", bootstyle="inverse-secondary")
        self.status_label.pack(side="left", padx=10)
        if self.recorder_service:
            recorder_frame = ttk.Frame(self.status_bar, bootstyle="secondary")
            recorder_frame.pack(side="right", padx=10)
            self.record_timer_label = ttk.Label(recorder_frame, text="00:00:00", bootstyle="inverse-secondary")
            self.record_timer_label.pack(side="left", padx=(0, 10))
            self.record_button = ttk.Button(recorder_frame, text="🔴", bootstyle="danger", command=self._on_start_record_click)
            self.record_button.pack(side="left")
    def _on_start_record_click(self):
        if self.recorder_service:
            success = self.recorder_service.start_recording()
            if success:
                self.is_ui_recording = True
                self.record_start_time = time.time()
                self._update_button_states()
                self._update_record_timer()
                self.status_label.config(text=self.loc.get('status_bar_recording', fallback="Recording screen and audio..."))
            else:
                messagebox.showerror(self.loc.get('error_title', fallback="Error"), self.loc.get('recorder_start_error', fallback="Could not start recording. Check logs for details."))
    def _on_stop_record_click(self):
        if self.recorder_service:
            self.status_label.config(text=self.loc.get('status_bar_saving', fallback="Saving video, please wait..."))
            self.record_button.config(state="disabled")
            self.update_idletasks()
            final_path = self.recorder_service.stop_recording()
            self.is_ui_recording = False
            if self.record_timer_job:
                self.after_cancel(self.record_timer_job)
                self.record_timer_job = None
            self._update_button_states()
            self.status_label.config(text=self.loc.get('status_bar_ready', fallback="Ready."))
            if final_path:
                messagebox.showinfo(
                    self.loc.get("recorder_save_success_title"),
                    self.loc.get("recorder_save_success_msg") + f"\n\nPath: {final_path}"
                )
            else:
                 messagebox.showerror(self.loc.get('error_title', fallback="Error"), self.loc.get('recorder_save_error', fallback="Failed to save the recording. Check logs for details."))
    def _update_record_timer(self):
        if self.is_ui_recording:
            elapsed_seconds = int(time.time() - self.record_start_time)
            hours, remainder = divmod(elapsed_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.record_timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
            self.record_timer_job = self.after(1000, self._update_record_timer)
    def _update_button_states(self):
        if self.is_ui_recording:
            self.record_button.config(text="⏹️", command=self._on_stop_record_click)
        else:
            self.record_timer_label.config(text="00:00:00")
            self.record_button.config(text="🔴", command=self._on_start_record_click, state="normal")
    def _subscribe_to_events(self):
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.subscribe("AI_ANALYSIS_STARTED", "main_window_status", self._on_ai_analysis_started)
            event_bus.subscribe("AI_ANALYSIS_PROGRESS", "main_window_status", self._on_ai_analysis_progress)
            event_bus.subscribe("AI_ANALYSIS_FINISHED", "main_window_status", self._on_ai_analysis_finished)
    def _on_ai_analysis_started(self, event_data):
        self.status_label.config(text=event_data.get("message", self.loc.get('ai_copilot_working_status', fallback="AI Co-pilot is working...")))
    def _on_ai_analysis_progress(self, event_data):
        self.status_label.config(text=event_data.get("message", self.loc.get('ai_copilot_working_status', fallback="AI Co-pilot is working...")))
    def _on_ai_analysis_finished(self, event_data):
        self.status_label.config(text=self.loc.get('status_bar_ready', fallback="Ready."))
    def add_notification(self, title: str, message: str, level: str = "INFO"):
        self.popup_manager.show_notification(title, message, level)
    def refresh_ui_components(self):
        self.kernel.write_to_log("UI: Rebuilding dynamic menubar...", "DEBUG") # English Log
        if self.menubar_manager:
            self.menubar_manager.build_menu()
        for tab_id in self.notebook.tabs():
            try:
                tab_widget = self.notebook.nametowidget(tab_id)
                if hasattr(tab_widget, 'refresh_content'):
                    tab_widget.refresh_content()
                theme_manager = self.kernel.get_service("theme_manager")
                if hasattr(tab_widget, 'apply_styles') and theme_manager:
                    tab_widget.apply_styles(theme_manager.get_colors())
            except Exception as e:
                self.kernel.write_to_log(f"Failed to refresh components in tab ID {tab_id}: {e}", "ERROR") # English Log
    def apply_theme(self, theme_id):
        self.apply_manual_styles()
        self.refresh_ui_components()
    def apply_manual_styles(self):
        theme_manager = self.kernel.get_service("theme_manager")
        if not theme_manager: return
        flowork_colors = theme_manager.get_colors()
        if not flowork_colors: return
        style = tk_ttk.Style(self);
        self.configure(background=flowork_colors['bg'])
        style.configure('TNotebook', background= flowork_colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', background=flowork_colors['dark'], foreground=flowork_colors['fg'],
        padding =[10,5], font=('Helvetica', 10, 'bold'))
        style.map('TNotebook.Tab',
        background=[('selected' , flowork_colors['primary'])], foreground=[('selected',
        flowork_colors['success'])])
        style.configure("TFrame", background= flowork_colors['bg'], borderwidth=0)
        style.configure('TLabel', background=flowork_colors['bg'], foreground= flowork_colors['fg'])
        style.configure('TLabelframe', background= flowork_colors['bg'], borderwidth =1,
        relief='solid',
        bordercolor= flowork_colors['border'])
        style.configure('TLabelframe.Label', background=flowork_colors['bg'],
        foreground= flowork_colors['fg'], font=("Helvetica", 10, "bold"))
    def create_widgets (self):
        tab_bar_frame =ttk.Frame(self, style='TFrame' )
        tab_bar_frame.pack(fill= 'x', padx=5, pady=(5,0))
        ttk.Button(tab_bar_frame,
                   text=self.loc.get('save_session_button', fallback="Save Session & Layout"),
                   command=self._confirm_and_save_session,
                   style="info.TButton").pack(side="right", anchor='n', pady=2, padx=(2,0))
        ttk.Button(tab_bar_frame,
                   text=self.loc.get('clear_cache_button', fallback="Clear Cache"),
                   command=self._clear_cache_action,
                   style="secondary.TButton").pack(side="right", anchor='n', pady=2, padx=(2,0))
        ttk.Button(tab_bar_frame, text=self.loc.get('clear_layout_button', fallback="Clear Layout"), command=self.clear_active_dashboard, style="danger.TButton").pack(side="right", anchor= 'n',
        pady=2, padx=(2,0))
        add_button = ttk.Button(tab_bar_frame, text="+", width =2, command=lambda:
        self.tab_manager.add_new_workflow_tab(),
        style="success.TButton")
        add_button.pack(side="right", anchor="n", pady=2, padx=(2,0))
        self.notebook = DraggableNotebook(self, loc=self.loc)
        self.notebook.set_close_tab_command(lambda tab_id: self.tab_manager.close_tab(tab_id))
        self.notebook.pack(expand=True, fill= "both", padx =5, pady=(0,5))
    def _confirm_and_save_session(self):
        if messagebox.askyesno(
            self.loc.get('confirm_save_session_title', fallback="Confirm Save"),
            self.loc.get('confirm_save_session_message', fallback="Are you sure you want to save the current workflow, all open tabs, and dashboard layout?")
        ):
            self.save_layout_and_session()
    def _clear_cache_action(self):
        """
        Calls the proper cache clearing function from the active tab's action handler.
        """
        self.kernel.write_to_log("DEBUG: Clear Cache action triggered.", "WARN") # English Log
        active_tab_widget = self.notebook.nametowidget(self.notebook.select())
        if isinstance(active_tab_widget, WorkflowEditorTab) and hasattr(active_tab_widget, 'action_handler'):
            active_tab_widget.action_handler.clear_cache()
        else:
            self.kernel.write_to_log("CLEAR CACHE FAILED: Active tab is not a workflow editor or has no action handler.", "ERROR") # English Log
            messagebox.showwarning(self.loc.get('action_failed_title', fallback="Action Failed"), self.loc.get('action_workflow_tab_only', fallback="This action can only be performed on a Dashboard/Workflow tab."))
    def add_dynamic_menu_item(self, parent_menu_label, item_label, item_command):
        if parent_menu_label in self.main_menus:
            menu = self.main_menus [parent_menu_label]
            menu.add_command(label=item_label, command=item_command)
        else:
            self.kernel.write_to_log(f"UI: Failed to add menu item. Main menu '{parent_menu_label}' not found.", "WARN")
    def _trigger_workflow_action(self, action_name):
        active_tab_widget = self.notebook.nametowidget(self.notebook.select())
        if isinstance(active_tab_widget, WorkflowEditorTab) and hasattr(active_tab_widget, 'action_handler') and hasattr(active_tab_widget.action_handler, action_name):
            try:
                method_to_call = getattr(active_tab_widget.action_handler, action_name)
                method_to_call()
            except Exception as e:
                messagebox.showerror(self.loc.get('error_title', fallback="Error"),
                self.loc.get('action_execution_error', fallback=f"Error executing action '{action_name}': {e}", action_name=action_name, error=e))
        else:
            messagebox.showinfo(self.loc.get('info_title', fallback="Info"),
            self.loc.get('action_workflow_tab_only', fallback="This action can only be performed in a Workflow tab."))
    def clear_active_dashboard(self):
        active_tab_widget = self.notebook.nametowidget(self.notebook.select())
        if hasattr(active_tab_widget, 'clear_dashboard_widgets'):
            if messagebox.askyesno(self.loc.get('confirm_clear_layout_title',
            fallback="Confirm"), self.loc.get('confirm_clear_layout_message' , fallback="Are you sure you want to clear all widgets from this dashboard?")):
                active_tab_widget.clear_dashboard_widgets()
        else:
            messagebox.showinfo(self.loc.get('info_title' , fallback="Info"),
            self.loc.get('action_dashboard_tab_only', fallback="This action only applies to Dashboard tabs."))
    def save_layout_and_session(self):
        for tab_id_str in self.notebook.tabs():
            widget= self.notebook.nametowidget (tab_id_str)
            if hasattr(widget, 'save_dashboard_layout'):
                widget.save_dashboard_layout()
        success, response = self.tab_manager.save_session_state()
        if success:
            self.kernel.write_to_log(self.loc.get('layout_and_session_saved', fallback="Layout and Session saved successfully!"), "SUCCESS")
        else:
            error_message = f"Failed to save tab session: {response}"
            self.kernel.write_to_log(error_message, "ERROR") # English Log
            messagebox.showerror(self.loc.get("error_title"), error_message)
    def _open_managed_tab(self, tab_key):
        self.tab_manager.open_managed_tab(tab_key)
    def _show_about_dialog(self):
        base_message = self.loc.get('about_message', fallback="Flowork: The Limitless Visual Automation Platform")
        license_status = f"Tier: {self.kernel.license_tier.upper()}"
        final_message = f"{base_message}\n\nLicense Status: {license_status}"
        messagebox.showinfo(
            self.loc.get('about_title', fallback="About Flowork"),
            final_message
        )
    def prompt_for_license_file(self):
        self.kernel.write_to_log("License activation process started by user.", "INFO") # English Log
        filepath = filedialog.askopenfilename(
            title=self.loc.get('select_license_file_title', fallback="Select Your license.seal File"),
            filetypes=[(self.loc.get('license_seal_filetype', fallback="License Seal File"), "*.seal")]
        )
        if not filepath:
            self.kernel.write_to_log("License activation cancelled by user.", "WARN") # English Log
            return
        try:
            destination_path = os.path.join(self.kernel.data_path, "license.seal")
            shutil.copyfile(filepath, destination_path)
            self.kernel.write_to_log(f"New license.seal file copied to {destination_path}", "SUCCESS") # English Log
            with open(destination_path, 'r', encoding='utf-8') as f:
                license_content = json.load(f)
            license_data = license_content.get('data')
            if not license_data:
                messagebox.showerror(self.loc.get('error_title', fallback="Error"), self.loc.get('license_invalid_format_error', fallback="Invalid license file format: missing 'data' block."))
                return
            threading.Thread(target=self._run_online_activation, args=(license_data,), daemon=True).start()
        except Exception as e:
            self.kernel.write_to_log(f"Failed to copy or read license file: {e}", "ERROR") # English Log
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), self.loc.get('license_process_error', fallback=f"Could not process the license file. Error: {e}", error=e))
    def _run_online_activation(self, license_data):
        self.kernel.write_to_log("Attempting online license activation...", "INFO") # English Log
        success, message = self.kernel.activate_license_online(license_data)
        self.after(0, self._show_activation_result, success, message)
    def _show_activation_result(self, success, message):
        if success:
            messagebox.showinfo(
                self.loc.get('license_activated_title', fallback="License Activated"),
                f"{message}\n\n{self.loc.get('license_restart_required_msg', fallback='Please restart the application for the changes to take effect.')}"
            )
        else:
            messagebox.showerror(self.loc.get('license_activation_failed_title', fallback="Activation Failed"), message)
    def show_permission_denied_popup(self, message: str):
        """
        Displays a standardized "permission denied" popup and offers to open the pricing page.
        """
        if messagebox.askyesno(
            self.loc.get('license_popup_title', fallback="Premium Feature"),
            f"{message}\n\n{self.loc.get('permission_denied_upgrade_prompt', fallback='Would you like to view plans to upgrade?')}",
            parent=self
        ):
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager:
                tab_manager.open_managed_tab("pricing_page")
