# william_diagnostics/diagnostic.py

import importlib
import subprocess
import sys
import os
from datetime import datetime

# Liste des modules requis et instructions de réparation
MODULES_REQUIS = {
    "wcm": "module interne (modules/wcm.py)",
    "tts": "module interne (modules/tts.py)",
    "llm": "module interne (modules/llm.py)",
    "speech_recognition": "pip install SpeechRecognition",
    "pyttsx3": "pip install pyttsx3",
    "torch": "pip install torch",
    "transformers": "pip install transformers",
    "pyaudio": "pip install pyaudio",
    "whisper": "pip install openai-whisper"
}

def verifier_module(nom):
    try:
        importlib.import_module(nom)
        return True
    except ImportError:
        return False


def run_diagnostic():
    print("🔍 Diagnostic de l’environnement...\n")
    erreurs = {}

    for module, commande in MODULES_REQUIS.items():
        est_disponible = verifier_module(module)
        statut = "✅" if est_disponible else "❌"
        print(f"{statut} {module:<20} {'Disponible' if est_disponible else 'Manquant'}")
        erreurs[module] = {
            "status": "OK" if est_disponible else "ERROR",
            "fix": commande
        }

    modules_manquants = [m for m, v in erreurs.items() if v["status"] == "ERROR" and not m.startswith("wcm")]

    if modules_manquants:
        print("\n📌 Modules manquants détectés :")
        for mod in modules_manquants:
            print(f"- {mod} → {MODULES_REQUIS[mod]}")

        print("\n💡 Souhaitez-vous tenter une réparation automatique ? (O/N)")
        reponse = input(">>> ").strip().lower()

        if reponse == "o":
            for mod in modules_manquants:
                try:
                    print(f"🛠️ Installation de {mod}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", mod])
                    print(f"✅ {mod} installé avec succès.")
                except Exception as e:
                    print(f"❌ Erreur lors de l’installation de {mod} : {e}")
        else:
            print("⏭️ Réparation automatique ignorée.")

    else:
        print("\n✅ Tous les modules nécessaires sont présents !")

    return erreurs


def start_continuous_monitoring():
    # Optionnel : surveillance continue en arrière-plan
    print("⏳ Surveillance continue : non implémentée encore.")

def stop_continuous_monitoring():
    print("🛑 Surveillance arrêtée.")
