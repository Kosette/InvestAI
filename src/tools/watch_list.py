import json

def load_watchlist(filepath):
    with open(filepath, "r") as f:
        watchlist = json.load(f)
    return watchlist