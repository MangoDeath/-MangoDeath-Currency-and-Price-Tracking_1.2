"""
main.py
-------
Entry point for the Crypto Portfolio Tracker.
Run with:  python main.py
"""

import tkinter as tk
from auth import LoginWindow


def main():
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
