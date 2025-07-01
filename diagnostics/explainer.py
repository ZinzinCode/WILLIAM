error_dict = {
    "ConnectionError": "Vérifie ta connexion Internet.",
    "FileNotFoundError": "Un fichier nécessaire est introuvable.",
    "ModuleNotFoundError": "Un module Python est manquant.",
    "AssertionError": "Le module fonctionne mal ou renvoie un mauvais résultat.",
}

def explain_error(e):
    name = type(e).__name__
    return error_dict.get(name, f"Erreur inconnue : {e}")
