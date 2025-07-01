import json
import os
import pickle

MEMORY_FILE = "long_term_memory.json"
SNAPSHOT_FILE = "memory_snapshot.pkl"

# --- Mémoire à long terme (JSON) ---

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def add_fact(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

def get_fact(key):
    memory = load_memory()
    return memory.get(key, None)

def all_facts():
    return load_memory()

# --- Snapshot complet (pickle) ---

def save_snapshot(obj, path=SNAPSHOT_FILE):
    with open(path, "wb") as f:
        pickle.dump(obj, f)

def load_snapshot(path=SNAPSHOT_FILE):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None