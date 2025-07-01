import json
import os
import pickle
from datetime import datetime

MEMORY_FILE = "long_term_memory.json"
SNAPSHOT_FILE = "memory_snapshot.pkl"

# --- Mémoire évolutive William ---

def _init_memory():
    """Initialise le fichier mémoire s'il n'existe pas."""
    if not os.path.exists(MEMORY_FILE):
        data = {
            "facts": {},
            "conversations": [],
            "user_preferences": {},
            "stats": {
                "total_interactions": 0,
                "last_interaction": None,
            }
        }
        save_memory(data)

def load_memory():
    _init_memory()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

# --- Faits (connaissances, souvenirs) ---

def add_fact(key, value):
    memory = load_memory()
    memory["facts"][key] = value
    save_memory(memory)

def get_fact(key):
    memory = load_memory()
    return memory["facts"].get(key, None)

def all_facts():
    memory = load_memory()
    return memory["facts"]

# --- Conversations (historique) ---

def add_conversation(user_input, william_response):
    memory = load_memory()
    conversation = {
        "timestamp": datetime.now().isoformat(),
        "user": user_input,
        "william": william_response
    }
    memory["conversations"].append(conversation)
    # Limite la taille de l'historique pour éviter l'inflation
    memory["conversations"] = memory["conversations"][-500:]
    # Statistiques
    memory["stats"]["total_interactions"] += 1
    memory["stats"]["last_interaction"] = conversation["timestamp"]
    save_memory(memory)

def get_conversations(n=10):
    memory = load_memory()
    return memory["conversations"][-n:]

def clear_conversations():
    memory = load_memory()
    memory["conversations"] = []
    save_memory(memory)

# --- Préférences utilisateur ---

def set_user_preference(key, value):
    memory = load_memory()
    memory["user_preferences"][key] = {
        "value": value,
        "updated": datetime.now().isoformat()
    }
    save_memory(memory)

def get_user_preference(key, default=None):
    memory = load_memory()
    pref = memory["user_preferences"].get(key)
    return pref["value"] if pref else default

def all_user_preferences():
    memory = load_memory()
    return memory["user_preferences"]

# --- Statistiques ---

def get_stats():
    memory = load_memory()
    return memory.get("stats", {})

# --- Snapshot complet (pickle) ---

def save_snapshot(obj, path=SNAPSHOT_FILE):
    with open(path, "wb") as f:
        pickle.dump(obj, f)

def load_snapshot(path=SNAPSHOT_FILE):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

# --- Utilitaires ---

def export_memory(export_path="william_export_memory.json"):
    memory = load_memory()
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)
    return export_path

if __name__ == "__main__":
    # Test rapide
    add_fact("exemple", "Ceci est une démo.")
    print("Faits :", all_facts())
    add_conversation("Qui es-tu ?", "Je suis William.")
    print("Dernières conversations :", get_conversations(2))
    set_user_preference("langue", "français")
    print("Préférences utilisateur :", all_user_preferences())
    print("Stats :", get_stats())