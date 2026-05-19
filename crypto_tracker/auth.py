"""
auth.py
-------
Handles user registration and login.
Passwords are stored as SHA-256 hashes in data/users.json.
"""

import json
import os
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox

USERS_FILE = "data/users.json"


# ── Helper ─────────────────────────────────────────────────────────────────────
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── Class 3: AuthManager ───────────────────────────────────────────────────────
class AuthManager:
    """Handles registration and login with JSON-backed user storage."""

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.users: dict = self._load_users()

    def _load_users(self) -> dict:
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_users(self):
        with open(USERS_FILE, "w") as f:
            json.dump(self.users, f, indent=4)

    def register(self, username: str, password: str) -> tuple[bool, str]:
        if not username or not password:
            return False, "Username and password cannot be empty."
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(password) < 4:
            return False, "Password must be at least 4 characters."
        if username in self.users:
            return False, "Username already exists."
        self.users[username] = _hash_password(password)
        self._save_users()
        return True, "Account created! You can now log in."

    def login(self, username: str, password: str) -> tuple[bool, str]:
        if not username or not password:
            return False, "Please fill in all fields."
        if username not in self.users:
            return False, "User not found. Please register first."
        if self.users[username] != _hash_password(password):
            return False, "Incorrect password. Please try again."
        return True, "Login successful!"


# ── Login / Register Tkinter Window ───────────────────────────────────────────
class LoginWindow:
    """Simple login and registration screen."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Crypto Tracker — Login")
        self.root.geometry("400x340")
        self.root.resizable(False, False)
        self.auth = AuthManager()
        self._build_ui()

    def _build_ui(self):
        # Outer frame with padding
        frame = ttk.Frame(self.root, padding=30)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="🪙 Crypto Portfolio Tracker",
                  font=("Helvetica", 17, "bold")).pack(pady=(0, 5))
        ttk.Label(frame, text="Sign in or create an account",
                  font=("Helvetica", 9), foreground="gray").pack(pady=(0, 20))

        # Username
        ttk.Label(frame, text="Username:").pack(anchor="w")
        self.username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var, width=32).pack(pady=(2, 10))

        # Password
        ttk.Label(frame, text="Password:").pack(anchor="w")
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(frame, textvariable=self.password_var,
                                        show="*", width=32)
        self.password_entry.pack(pady=(2, 5))

        # Show/hide password toggle
        self.show_pw = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Show password", variable=self.show_pw,
                        command=self._toggle_pw).pack(anchor="w", pady=(0, 15))

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text="Login", command=self._login,
                   width=14).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Register", command=self._register,
                   width=14).pack(side="left", padx=6)

        # Allow Enter key to log in
        self.root.bind("<Return>", lambda _: self._login())

    def _toggle_pw(self):
        self.password_entry.config(show="" if self.show_pw.get() else "*")

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        ok, msg = self.auth.login(username, password)
        if ok:
            self._open_main_app(username)
        else:
            messagebox.showerror("Login Failed", msg, parent=self.root)

    def _register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        ok, msg = self.auth.register(username, password)
        if ok:
            messagebox.showinfo("Success", msg, parent=self.root)
        else:
            messagebox.showerror("Registration Error", msg, parent=self.root)

    def _open_main_app(self, username: str):
        """Close login window and open the main dashboard."""
        from app import MainApp
        self.root.destroy()
        new_root = tk.Tk()
        MainApp(new_root, username)
        new_root.mainloop()
