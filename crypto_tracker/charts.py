"""
charts.py
---------
Generates matplotlib charts embedded in Tkinter Toplevel windows.
"""

import tkinter as tk
from tkinter import ttk, messagebox

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False


def _check_matplotlib(parent) -> bool:
    if not MATPLOTLIB_OK:
        messagebox.showerror(
            "Missing Library",
            "matplotlib is not installed.\nRun: pip install matplotlib",
            parent=parent,
        )
        return False
    return True


def show_pie_chart(assets: list, parent: tk.Tk = None):
    """
    Show a pie chart of portfolio distribution by USD value.
    Only includes assets with a value > 0.
    """
    if not _check_matplotlib(parent):
        return

    valued = [(a.symbol, a.total_value()) for a in assets if a.total_value() > 0]
    if not valued:
        messagebox.showinfo("No Data", "No assets with value > 0 to chart.", parent=parent)
        return

    labels, values = zip(*valued)

    win = tk.Toplevel(parent)
    win.title("Portfolio Distribution — Pie Chart")
    win.geometry("600x520")

    fig = Figure(figsize=(6, 5), dpi=100)
    ax = fig.add_subplot(111)
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.82,
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax.set_title("Portfolio Distribution by Value (USD)", fontsize=13, pad=15)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    ttk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 10))


def show_bar_chart(assets: list, parent: tk.Tk = None):
    """
    Show a bar chart of each asset's total USD value.
    """
    if not _check_matplotlib(parent):
        return

    if not assets:
        messagebox.showinfo("No Data", "Portfolio is empty.", parent=parent)
        return

    symbols = [a.symbol for a in assets]
    values  = [a.total_value() for a in assets]
    colors  = plt.cm.tab20.colors[:len(symbols)]   # distinct colors

    win = tk.Toplevel(parent)
    win.title("Asset Values — Bar Chart")
    win.geometry("700x480")

    fig = Figure(figsize=(7, 4.5), dpi=100)
    ax = fig.add_subplot(111)
    bars = ax.bar(symbols, values, color=colors, width=0.5)

    # Label each bar with its value
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.01,
            f"${val:,.2f}",
            ha="center", va="bottom", fontsize=8,
        )

    ax.set_title("Total Asset Values (USD)", fontsize=13)
    ax.set_xlabel("Symbol")
    ax.set_ylabel("Value (USD)")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"${x:,.0f}")
    )
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    ttk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 10))


def show_price_history_chart(symbol: str, history: list[tuple], parent: tk.Tk = None):
    """
    Show a simple line chart of price history for one asset.
    `history` is a list of (date_str, price) tuples.
    """
    if not _check_matplotlib(parent):
        return

    if len(history) < 2:
        messagebox.showinfo("Not Enough Data",
                            f"Need at least 2 price records for {symbol}.",
                            parent=parent)
        return

    dates, prices = zip(*history)

    win = tk.Toplevel(parent)
    win.title(f"{symbol} — Price History")
    win.geometry("650x420")

    fig = Figure(figsize=(6.5, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(dates, prices, marker="o", color="steelblue", linewidth=2)
    ax.set_title(f"{symbol} Price History (USD)", fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"${x:,.2f}")
    )
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    ttk.Button(win, text="Close", command=win.destroy).pack(pady=(0, 10))
