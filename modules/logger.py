import os
from datetime import datetime

LOG_PATH = "data/william_log.txt"
SYSTEM_LOG_PATH = "data/william_system.log"
OBSERVER_LOG_PATH = "data/file_observer.log"

def log(user_message, william_response):
    """Enregistre une conversation dans le fichier de log principal."""
    os.makedirs("data", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] USER: {user_message}\n")
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WILLIAM: {william_response}\n")

def log_system_event(event_type, message):
    """Enregistre un événement système."""
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] SYSTEM - {event_type}: {message}\n"
    with open(SYSTEM_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)

def last_n_conversations(n=10):
    """Retourne les n dernières paires de conversation utilisateur/William."""
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    conv = []
    buf = []
    for line in reversed(lines):
        buf.insert(0, line)
        if "WILLIAM:" in line and len(buf) == 2:
            conv.insert(0, "".join(buf))
            buf = []
        if len(conv) >= n:
            break
    return conv

def get_log_stats():
    """Retourne des statistiques sur les logs"""
    stats = {
        "conversations": 0,
        "system_events": 0,
        "file_events": 0,
        "last_activity": "Aucune"
    }
    # Compter les conversations
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            stats["conversations"] = content.count("USER:")
    # Compter les événements système
    if os.path.exists(SYSTEM_LOG_PATH):
        with open(SYSTEM_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            stats["system_events"] = len(lines)
            if lines:
                last_line = lines[-1]
                stats["last_activity"] = last_line.split("]")[0][1:]
    # Compter les événements de fichiers
    if os.path.exists(OBSERVER_LOG_PATH):
        with open(OBSERVER_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            stats["file_events"] = len(lines)
    return stats

def clear_logs():
    """Efface tous les logs (à utiliser avec précaution)"""
    log_files = [LOG_PATH, SYSTEM_LOG_PATH, OBSERVER_LOG_PATH]
    for log_file in log_files:
        if os.path.exists(log_file):
            os.remove(log_file)
            print(f"🗑️ {log_file} supprimé")
    print("✅ Tous les logs ont été effacés")
    log_system_event("MAINTENANCE", "Tous les logs ont été effacés")

def init_logging():
    """Initialise le système de logging"""
    os.makedirs("data", exist_ok=True)
    session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_system_event("DÉMARRAGE", f"Session WillIAm démarrée - {session_start}")
    print("📝 Système de logging initialisé")

# Initialiser le logging au chargement du module
init_logging()