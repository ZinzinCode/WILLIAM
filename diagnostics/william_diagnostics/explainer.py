# Explique les erreurs Python courantes de manière claire pour l'utilisateur/GUI

error_dict = {
    "ConnectionError": "Vérifie ta connexion Internet.",
    "FileNotFoundError": "Un fichier nécessaire est introuvable.",
    "ModuleNotFoundError": "Un module Python est manquant.",
    "AssertionError": "Le module fonctionne mal ou renvoie un mauvais résultat.",
    "ImportError": "Un module Python ne peut pas être importé.",
    "OSError": "Erreur système ou fichier corrompu.",
    "PermissionError": "Permissions insuffisantes pour accéder au fichier.",
    "TimeoutError": "Délai d'attente dépassé.",
}

def explain_error(e):
    name = type(e).__name__
    return error_dict.get(name, f"Erreur inconnue : {e}")