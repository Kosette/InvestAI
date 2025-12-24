import json

def load_index_pool(filepath):
    with open(filepath, "r") as f:
        index_pool = json.load(f)
    return index_pool