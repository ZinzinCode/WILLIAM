import os
import shutil
import datetime
import difflib

REPAIR_LOGS = "repair_logs"

def list_py_files():
    """Liste tous les fichiers .py à la racine et sous-dossiers."""
    py_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files

def audit_code():
    """Retourne une liste de suggestions d'amélioration/d'anomalies."""
    suggestions = []
    # Exemple 1: vérifier présence d'un fichier critique
    if not os.path.exists("data/voice_samples/male_sample.wav"):
        suggestions.append({
            "title": "Fichier voix manquant",
            "desc": "Le fichier male_sample.wav est absent. Ajoutez un test d'existence dans tts.py.",
            "filename": "tts.py",
            "patch": "if not os.path.exists(sample_path):\n    raise FileNotFoundError(sample_path)"
        })
    # Exemple 2: imports doublons
    for file in list_py_files():
        with open(file, encoding="utf-8") as f:
            lines = f.readlines()
        if lines.count("import os\n") > 1:
            suggestions.append({
                "title": "Import redondant",
                "desc": f"Plusieurs imports 'os' dans {file}.",
                "filename": file,
                "patch": "# Supprimez les doublons d'import os"
            })
    # TODO: Ajouter vérification dépendances, code mort, logs, etc.
    return suggestions

def backup_file(filepath):
    os.makedirs(REPAIR_LOGS, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(REPAIR_LOGS, f"{os.path.basename(filepath)}_{ts}.bak")
    shutil.copy(filepath, backup_path)
    return backup_path

def apply_patch(filename, new_content):
    backup = backup_file(filename)
    with open(filename, "r", encoding="utf-8") as f:
        old_content = f.read()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_content)
    log_repair(filename, old_content, new_content)
    return backup

def show_diff(old, new):
    diff = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile='avant',
        tofile='après'
    )
    return ''.join(diff)

def log_repair(filename, old_content, new_content):
    os.makedirs(REPAIR_LOGS, exist_ok=True)
    log_path = os.path.join(REPAIR_LOGS, "repair_log.txt")
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.datetime.now()}] PATCH sur {filename}\n")
        log.write(show_diff(old_content, new_content))
        log.write("\n")

def undo_last_repair():
    backups = sorted([f for f in os.listdir(REPAIR_LOGS) if f.endswith(".bak")])
    if not backups:
        return "Aucune sauvegarde à restaurer."
    last = backups[-1]
    orig_name = last.split("_")[0] + ".py"
    shutil.copy(os.path.join(REPAIR_LOGS, last), orig_name)
    return f"Restauration de {orig_name} depuis {last}"