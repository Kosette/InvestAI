import json


def load_watchlist(filepath):
    with open(filepath, "r") as f:
        watchlist = json.load(f)
    return watchlist


def add_to_watchlist(filepath, item):
    watchlist = load_watchlist(filepath)
    watchlist[item["name"]] = item["code"]
    with open(filepath, "w") as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=4)
