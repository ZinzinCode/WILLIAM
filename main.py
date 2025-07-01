# main.py

import datetime

print("🤖 Initialisation de William...")
print(f"📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# === Étape 1 : Diagnostic système ===
try:
    from diagnostic import run_diagnostic
    erreurs = run_diagnostic()
    modules_critiques = [m for m, info in erreurs.items() if info["status"] == "ERROR" and m in ["wcm", "tts", "llm"]]

    if modules_critiques:
        print("\n❌ Impossible de démarrer William : modules critiques manquants.")
        exit(1)

except Exception as e:
    print(f"⚠️ Erreur pendant le diagnostic : {e}")
    print("⛔ Démarrage annulé pour éviter des comportements instables.")
    exit(1)

# === Étape 2 : Lancement des modules ===
try:
    from wcm import ContextManager
except ImportError:
    print("❌ Impossible de charger le gestionnaire de contexte: No module named 'wcm'")
    ContextManager = None

try:
    from tts import VoiceEngine
except ImportError:
    print("⚠️ Synthèse vocale non disponible: No module named 'tts'")
    VoiceEngine = None

try:
    from llm import LanguageModel
except ImportError:
    print("⚠️ Modèle de langage non disponible: No module named 'llm'")
    LanguageModel = None

# === Étape 3 : Démarrage de William ===
print("\n🤖 William est prêt ! Tapez 'quit' pour quitter.")

if LanguageModel:
    assistant = LanguageModel()
else:
    assistant = None

while True:
    user_input = input("👤 Vous: ").strip()
    if user_input.lower() in ["quit", "exit"]:
        print("👋 Au revoir !")
        break

    if user_input.lower() == "diagnostic":
        run_diagnostic()
        continue

    if assistant:
        response = assistant.generate_response(user_input)
        print(f"🤖 William: {response}")
        if VoiceEngine:
            VoiceEngine().speak(response)
    else:
        print("⚠️ William n'est pas fonctionnel sans le module de langage.")
