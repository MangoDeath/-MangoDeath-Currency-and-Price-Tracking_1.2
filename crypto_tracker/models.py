"""
models.py
---------
Defines the Asset and Portfolio classes used throughout the app.
Includes a simple decorator for action logging (advanced Python feature).
"""

import json
import os
from datetime import datetime

DATA_FILE = "data/portfolio.json"
LOG_FILE = "data/log.txt"


# ── Advanced Python feature: decorator ────────────────────────────────────────
def log_action(func):
    """Decorator that logs every save/load action to a text file."""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        os.makedirs("data", exist_ok=True)
        with open(LOG_FILE, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {func.__name__} called\n")
        return result
    return wrapper


# ── Class 1: Asset ─────────────────────────────────────────────────────────────
class Asset:
    """Represents a single cryptocurrency asset in the portfolio."""

    def __init__(self, name: str, symbol: str, quantity: float, price: float = 0.0):
        self.name = name.strip()
        self.symbol = symbol.strip().upper()
        self.quantity = float(quantity)
        self.price = float(price)
        self.added_date = datetime.now().strftime("%Y-%m-%d")

    def total_value(self) -> float:
        """Return total value: quantity × price."""
        return self.quantity * self.price

    def to_dict(self) -> dict:
        """Serialize asset to a dictionary (for JSON saving)."""
        return {
            "name": self.name,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": self.price,
            "added_date": self.added_date,
        }

    @staticmethod
    def from_dict(data: dict) -> "Asset":
        """Create an Asset from a saved dictionary."""
        asset = Asset(data["name"], data["symbol"], data["quantity"], data["price"])
        asset.added_date = data.get("added_date", "N/A")
        return asset

    def __repr__(self) -> str:
        return f"Asset({self.symbol}, qty={self.quantity}, price={self.price})"


# ── Class 2: Portfolio ─────────────────────────────────────────────────────────
class Portfolio:
    """
    Manages a collection of Asset objects for one user.
    Uses a list for ordered storage and a set for fast duplicate checking.
    """

    def __init__(self, username: str):
        self.username = username
        self.assets: list[Asset] = []
        self._symbols: set[str] = set()   # set — fast O(1) duplicate check

    # ── CRUD operations ────────────────────────────────────────────────────────
    def add_asset(self, asset: Asset) -> tuple[bool, str]:
        if asset.symbol in self._symbols:
            return False, f"{asset.symbol} already exists in your portfolio."
        self.assets.append(asset)
        self._symbols.add(asset.symbol)
        return True, f"{asset.symbol} added successfully."

    def remove_asset(self, symbol: str) -> tuple[bool, str]:
        symbol = symbol.upper()
        for asset in self.assets:
            if asset.symbol == symbol:
                self.assets.remove(asset)
                self._symbols.discard(symbol)
                return True, f"{symbol} removed from portfolio."
        return False, f"{symbol} not found in portfolio."

    def update_price(self, symbol: str, new_price: float) -> tuple[bool, str]:
        symbol = symbol.upper()
        for asset in self.assets:
            if asset.symbol == symbol:
                asset.price = float(new_price)
                return True, f"{symbol} price updated to ${new_price:,.2f}"
        return False, f"{symbol} not found."

    def search(self, query: str) -> list[Asset]:
        """Return assets matching query by name or symbol (case-insensitive)."""
        q = query.lower()
        return [a for a in self.assets if q in a.name.lower() or q in a.symbol.lower()]

    def total_value(self) -> float:
        return sum(a.total_value() for a in self.assets)

    # ── summary stats (uses tuple as immutable snapshot) ──────────────────────
    def summary(self) -> tuple:
        """Return (count, total_value, symbols_set) as an immutable tuple."""
        return (len(self.assets), self.total_value(), frozenset(self._symbols))

    # ── Persistence ────────────────────────────────────────────────────────────
    @log_action
    def save(self):
        """Save this user's portfolio to JSON."""
        os.makedirs("data", exist_ok=True)
        all_data = self._load_all_raw()
        all_data[self.username] = [a.to_dict() for a in self.assets]
        with open(DATA_FILE, "w") as f:
            json.dump(all_data, f, indent=4)

    @log_action
    def load(self):
        """Load this user's portfolio from JSON."""
        all_data = self._load_all_raw()
        user_data = all_data.get(self.username, [])
        self.assets = [Asset.from_dict(d) for d in user_data]
        self._symbols = {a.symbol for a in self.assets}

    def _load_all_raw(self) -> dict:
        """Read the entire portfolio JSON file (all users)."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
