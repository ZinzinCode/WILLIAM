import os
import json
from datetime import datetime

LEARNING_FILE = "learning_state.json"

def _init_learning():
    """Initialise le fichier d'apprentissage s'il n'existe pas."""
    if not os.path.exists(LEARNING_FILE):
        state = {
            "instructions": [],
            "usage_log": [],
            "score": 0.0,
            "last_learned": None,
            "patterns": {}
        }
        save_learning(state)

def load_learning():
    _init_learning()
    with open(LEARNING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_learning(state):
    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# --- Mémorisation d'instructions (long terme) ---

def add_instruction(text, source="user"):
    state = load_learning()
    entry = {
        "text": text,
        "source": source,
        "timestamp": datetime.now().isoformat()
    }
    state["instructions"].append(entry)
    state["last_learned"] = entry["timestamp"]
    save_learning(state)

def get_instructions(n=10):
    state = load_learning()
    return state["instructions"][-n:]

def clear_instructions():
    state = load_learning()
    state["instructions"] = []
    save_learning(state)

# --- Tracking usage & amélioration ---

def log_usage(event, details=None):
    state = load_learning()
    entry = {
        "event": event,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    }
    state["usage_log"].append(entry)
    save_learning(state)

def get_usage_log(n=20):
    state = load_learning()
    return state["usage_log"][-n:]

def clear_usage_log():
    state = load_learning()
    state["usage_log"] = []
    save_learning(state)

# --- Mécanisme d'amélioration ("score", patterns) ---

def update_score(delta):
    state = load_learning()
    state["score"] = round(state.get("score", 0.0) + delta, 2)
    save_learning(state)

def get_score():
    state = load_learning()
    return state.get("score", 0.0)

def learn_pattern(pattern, count=1):
    """
    Enregistre la reconnaissance d'un pattern ou d'une habitude utilisateur.
    """
    state = load_learning()
    patterns = state.get("patterns", {})
    patterns[pattern] = patterns.get(pattern, 0) + count
    state["patterns"] = patterns
    save_learning(state)

def get_patterns():
    state = load_learning()
    return state.get("patterns", {})

# --- Utilitaire export/import ---

def export_learning(export_path="william_export_learning.json"):
    state = load_learning()
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    return export_path

if __name__ == "__main__":
    # Démo rapide
    add_instruction("Toujours répondre en français.", source="user")
    log_usage("test", {"note": "premier usage"})
    learn_pattern("salutation")
    update_score(0.5)
    print("Instructions:", get_instructions())
    print("Usage log:", get_usage_log())
    print("Patterns:", get_patterns())
    print("Score:", get_score())