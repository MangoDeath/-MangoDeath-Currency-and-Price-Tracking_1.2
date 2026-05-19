
import tkinter as tk
from tkinter import ttk, messagebox

from models import Portfolio, Asset
from api import fetch_prices, get_supported_symbols, COINGECKO_IDS
from charts import show_pie_chart, show_bar_chart



class MainApp:
   

    TABLE_COLS = ("Name", "Symbol", "Quantity", "Price (USD)", "Value (USD)", "Added")
    COL_WIDTHS = (160, 75, 90, 120, 120, 95)

    def __init__(self, root: tk.Tk, username: str):
        self.root = root
        self.username = username
        self.portfolio = Portfolio(username)
        self.portfolio.load()   

        self.root.title(f" Crypto Tracker — {username}")
        self.root.geometry("960x580")
        self.root.minsize(780, 480)

        self._build_ui()
        self._refresh_table()

    #    UI 
    def _build_ui(self):
        self._build_header()
        self._build_search()
        self._build_table()
        self._build_footer()
        self._build_buttons()

    def _build_header(self):
        bar = ttk.Frame(self.root, padding=(12, 8))
        bar.pack(fill="x")
        ttk.Label(bar, text=" Crypto Portfolio Tracker",
                  font=("Helvetica", 16, "bold")).pack(side="left")
        ttk.Label(bar, text=f"  {self.username}",
                  font=("Helvetica", 10), foreground="#555").pack(side="right")

    def _build_search(self):
        row = ttk.Frame(self.root, padding=(12, 2))
        row.pack(fill="x")
        ttk.Label(row, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self._on_search())
        ttk.Entry(row, textvariable=self.search_var, width=32).pack(side="left", padx=6)
        ttk.Button(row, text="Clear", command=self._clear_search).pack(side="left")

    def _build_table(self):
        frame = ttk.Frame(self.root, padding=(12, 6))
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(frame, columns=self.TABLE_COLS, show="headings", height=16)
        for col, width in zip(self.TABLE_COLS, self.COL_WIDTHS):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=width, anchor="center", minwidth=60)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # alternating row colors
        self.tree.tag_configure("odd",  background="#f5f5f5")
        self.tree.tag_configure("even", background="#ffffff")

    def _build_footer(self):
        foot = ttk.Frame(self.root, padding=(12, 4))
        foot.pack(fill="x")
        self.total_label = ttk.Label(foot, text="Total Portfolio Value: $0.00",
                                     font=("Helvetica", 12, "bold"))
        self.total_label.pack(side="left")
        self.status_label = ttk.Label(foot, text="", foreground="#555",
                                      font=("Helvetica", 9))
        self.status_label.pack(side="right")

    def _build_buttons(self):
        bar = ttk.Frame(self.root, padding=(12, 6))
        bar.pack(fill="x")

        actions = [
            (" Add Asset",self._open_add_dialog),
            (" Remove Asset", self._remove_selected),
            (" Update Price",   self._open_update_dialog),
            (" Fetch Live Prices", self._fetch_live_prices),
            (" Pie Chart",lambda: show_pie_chart(self.portfolio.assets, self.root)),
            (" Bar Chart",lambda: show_bar_chart(self.portfolio.assets, self.root)),
            (" Save",self._save),
            (" Load",self._load),
        ]

        for label, cmd in actions:
            ttk.Button(bar, text=label, command=cmd).pack(side="left", padx=3)

                    #table helpers 
    def _refresh_table(self, assets=None):
        self.tree.delete(*self.tree.get_children())
        display = assets if assets is not None else self.portfolio.assets

        for i, asset in enumerate(display):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", tag=tag, values=(
                asset.name,
                asset.symbol,
                f"{asset.quantity:g}",
                f"${asset.price:,.4f}",
                f"${asset.total_value():,.2f}",
                asset.added_date,
            ))

        total = self.portfolio.total_value()
        count, _, _ = self.portfolio.summary()
        self.total_label.config(text=f"Total Portfolio Value: ${total:,.2f}")
        self._set_status(f"{count} asset(s)")

    def _sort_by(self, col: str):
        
        idx = self.TABLE_COLS.index(col)
        reverse = getattr(self, "_last_sort", None) == col
        self._last_sort = None if reverse else col
        self.portfolio.assets.sort(
            key=lambda a: self.tree.set(self.tree.get_children()[
                self.portfolio.assets.index(a)
            ], col) if self.tree.get_children() else "",
            reverse=reverse,
        )
        self._refresh_table()

    def _on_search(self):
        query = self.search_var.get().strip()
        if query:
            self._refresh_table(self.portfolio.search(query))
        else:
            self._refresh_table()

    def _clear_search(self):
        self.search_var.set("")

    def _set_status(self, msg: str):
        self.status_label.config(text=msg)

    def _get_selected_symbol(self) -> str | None:
        """Return the symbol of the currently selected table row, or None."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an asset from the table.")
            return None
        return self.tree.item(sel[0], "values")[1]   # column index 1 = Symbol

    # ── Dialog: Add Asset ──────────────────────────────────────────────────────
    def _open_add_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Add New Asset")
        dlg.geometry("340x350")
        dlg.resizable(False, False)
        dlg.grab_set()

        frame = ttk.Frame(dlg, padding=33)
        frame.pack(fill="both", expand=True)

        supported = ", ".join(get_supported_symbols()[:20])
        ttk.Label(frame, text=f"Supported for live prices: {supported}",
                  font=("Helvetica", 8), foreground="gray",
                  wraplength=290).pack(anchor="w", pady=(0, 12))

        fields = [
            ("Name (e.g. Bitcoin):", "name",     False),
            ("Symbol (e.g. BTC):",   "symbol",   False),
            ("Quantity:",             "quantity", False),
            ("Price (USD):",         "price",    False),
        ]
        entries: dict[str, ttk.Entry] = {}
        for label, key, _ in fields:
            ttk.Label(frame, text=label).pack(anchor="w")
            e = ttk.Entry(frame, width=30)
            e.pack(pady=(2, 8))
            entries[key] = e

        def _submit():
            name   = entries["name"].get().strip()
            symbol = entries["symbol"].get().strip()
            qty_s  = entries["quantity"].get().strip()
            prc_s  = entries["price"].get().strip()

            if not name or not symbol:
                messagebox.showerror("Error", "Name and symbol are required.", parent=dlg)
                return
            if len(symbol) > 10:
                messagebox.showerror("Error", "Symbol seems too long.", parent=dlg)
                return
            try:
                qty = float(qty_s)
                if qty <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Quantity must be a positive number.", parent=dlg)
                return
            try:
                price = float(prc_s) if prc_s else 0.0
                if price < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Price must be 0 or a positive number.", parent=dlg)
                return

            asset = Asset(name, symbol, qty, price)
            ok, msg = self.portfolio.add_asset(asset)
            if ok:
                self._refresh_table()
                dlg.destroy()
                messagebox.showinfo("Added", msg)
            else:
                messagebox.showerror("Duplicate", msg, parent=dlg)

        ttk.Button(frame, text="Add to Portfolio", command=_submit).pack(pady=4)
        dlg.bind("<Return>", lambda _: _submit())

    # remove asset 
    def _remove_selected(self):
        symbol = self._get_selected_symbol()
        if symbol is None:
            return
        if not messagebox.askyesno("Confirm Remove",
                                   f"Remove {symbol} from your portfolio?",
                                   parent=self.root):
            return
        ok, msg = self.portfolio.remove_asset(symbol)
        if ok:
            self._refresh_table()
            messagebox.showinfo("Removed", msg)
        else:
            messagebox.showerror("Error", msg)

    # Update Price 
    def _open_update_dialog(self):
        symbol = self._get_selected_symbol()
        if symbol is None:
            return

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Update Price — {symbol}")
        dlg.geometry("300x170")
        dlg.resizable(False, False)
        dlg.grab_set()

        frame = ttk.Frame(dlg, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"New price for {symbol} (USD):").pack(anchor="w")
        price_entry = ttk.Entry(frame, width=28)
        price_entry.pack(pady=10)

        def _submit():
            prc_s = price_entry.get().strip()
            try:
                price = float(prc_s)
                if price < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid non-negative price.", parent=dlg)
                return
            ok, msg = self.portfolio.update_price(symbol, price)
            if ok:
                self._refresh_table()
                dlg.destroy()
                messagebox.showinfo("Updated", msg)
            else:
                messagebox.showerror("Error", msg, parent=dlg)

        ttk.Button(frame, text="Update", command=_submit).pack()
        dlg.bind("<Return>", lambda _: _submit())

    # fetch prices 
    def _fetch_live_prices(self):
        symbols = [a.symbol for a in self.portfolio.assets]
        if not symbols:
            messagebox.showinfo("Empty Portfolio", "Add some assets first.")
            return

        self._set_status("Fetching live prices…")
        self.root.update_idletasks()

        prices = fetch_prices(symbols)

        if not prices:
            messagebox.showwarning(
                "API Unavailable",
                "Could not fetch prices from CoinGecko.\n"
                "Check your internet connection or try again later.",
            )
            self._set_status("Fetch failed.")
            return

        updated = []
        for symbol, price in prices.items():
            ok, _ = self.portfolio.update_price(symbol, price)
            if ok:
                updated.append(symbol)

        self._refresh_table()
        if updated:
            messagebox.showinfo("Prices Updated",
                                f"Updated: {', '.join(updated)}")
        else:
            known = [s for s in symbols if s in COINGECKO_IDS]
            hint = f"\nKnown symbols in your portfolio: {known}" if known else ""
            messagebox.showinfo("No Match",
                                "None of your symbols matched CoinGecko.\n"
                                "Use standard tickers (BTC, ETH, SOL …)." + hint)

    # Save Load
    def _save(self):
        try:
            self.portfolio.save()
            messagebox.showinfo("Saved", "Portfolio saved to data/portfolio.json ✅")
        except Exception as exc:
            messagebox.showerror("Save Error", f"Could not save:\n{exc}")

    def _load(self):
        try:
            self.portfolio.load()
            self._refresh_table()
            messagebox.showinfo("Loaded", "Portfolio loaded from data/portfolio.json ✅")
        except Exception as exc:
            messagebox.showerror("Load Error", f"Could not load:\n{exc}")
