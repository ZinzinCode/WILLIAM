import sys
import threading
import datetime
import os
import json

from gui import WilliamGUI
from stt import listen
from tts import speak, preload_tts, ensure_voice_cache  # Ajout ici
from ollama_api import ollama_chat

# === Ajout pour le Mode REPAIR ===
from PySide6.QtWidgets import QPushButton
from interface.repair_panel import RepairPanel

# --- Mémoire cognitive persistante (optimisée, externalisable) ---
MEMORY_FILE = "data/william_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"facts": {}, "habits": {}, "feedback": [], "repetitions": {}}

def save_memory(mem):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)

memory = load_memory()

def add_fact(key, value):
    memory["facts"][key] = value
    save_memory(memory)

def record_habit(intent):
    memory["habits"][intent] = memory["habits"].get(intent, 0) + 1
    save_memory(memory)

def add_feedback(feedback):
    memory["feedback"].append({"ts": datetime.datetime.now().isoformat(), "feedback": feedback})
    save_memory(memory)

def record_repetition(text):
    key = text.strip().lower()
    memory["repetitions"][key] = memory["repetitions"].get(key, 0) + 1
    save_memory(memory)
    return memory["repetitions"][key]

# --- Détection d'intention/utilité (optimisée) ---
def is_code_question(user_input):
    mots_code = [
        "code", "python", "fonction", "programme", "script",
        "algorithm", "boucle", "variable", "java", "c++", "c#", "js", "javascript",
        "ligne de code", "erreur", "bug", "debug", "compilation", "instruction", "class", "méthode", "def ", "```"
    ]
    return any(m in user_input.lower() for m in mots_code) or "```" in user_input

def detect_intent(text):
    txt = text.lower()
    if any(w in txt for w in ["bonjour", "salut", "hello"]):
        return "salutation"
    if "heure" in txt:
        return "question_heure"
    if "date" in txt or "jour" in txt:
        return "question_date"
    if "merci" in txt:
        return "remerciement"
    if "diagnostic" in txt:
        return "diagnostic"
    if "aide" in txt:
        return "aide"
    if any(w in txt for w in ["au revoir", "bye", "exit", "quit"]):
        return "au_revoir"
    if any(w in txt for w in ["que vois-tu à l’écran", "que vois-tu à l'ecran", "lis ce document", "scan écran", "scan ecran", "lis l'écran", "lis l'ecran"]):
        return "ocr"
    return "autre"

# --- Web search & OCR integration (sécurisé) ---
def web_search(query):
    try:
        from websearch import bing_search
        result = bing_search(query)
        return result if result else "Aucun résultat web pertinent trouvé."
    except Exception as e:
        return f"Recherche web impossible : {e}"

def run_ocr():
    try:
        from ocr import read_screen
        return read_screen()
    except Exception as e:
        return f"Erreur OCR : {e}"

# --- Génération de réponse principale (modulaire, ready LLM) ---
def get_response(user_input, history):
    llama_history = history[:]
    if not any(m.get("role") == "system" for m in llama_history):
        llama_history = [
            {"role": "system", "content": "Tu es un assistant intelligent, expert en informatique, qui réponds toujours en français de façon claire, concise et pédagogique. Si tu dois expliquer du code, fais-le pas à pas, simplement."}
        ] + llama_history

    # Mémoire cognitive dans le contexte
    context_info = ""
    if memory["facts"]:
        facts_str = "\n".join(f"- {k}: {v}" for k, v in list(memory["facts"].items())[-5:])
        context_info += f"Connaissances précédemment retenues :\n{facts_str}\n"
    if memory["habits"]:
        hab, count = max(memory["habits"].items(), key=lambda x: x[1])
        if count >= 3:
            context_info += f"L'utilisateur pose souvent des questions de type '{hab}' ({count} fois récemment). Adapte-toi.\n"

    llama_history = llama_history[-8:]
    history = history[-8:]

    intent = detect_intent(user_input)
    record_habit(intent)
    repetition_count = record_repetition(user_input)

    # OCR priorité si demandé explicitement
    if intent == "ocr":
        ocr_text = run_ocr()
        if ocr_text:
            add_fact(f"OCR du {datetime.datetime.now().isoformat()}", ocr_text)
            return f"Texte OCR extrait :\n{ocr_text[:500]}" + ("..." if len(ocr_text) > 500 else "")

    if is_code_question(user_input):
        code_response = ollama_chat(
            user_input + " (Réponds seulement avec le code ou la correction, sans explication superflue, maximum 10 lignes.)",
            history, model="deepseek-coder:latest"
        )
        prompt_llama = (
            f"{context_info}Voici la réponse d'une IA spécialisée en code :\n{code_response}\n"
            "Explique ou reformule cette réponse en français, de façon claire, pédagogique et concise. Réponds en 2 phrases maximum."
        )
        final_response = ollama_chat(prompt_llama, llama_history, model="llama3:latest")
    else:
        prompt = f"{context_info}{user_input} (Réponds en 2 phrases maximum, en français, direct au but.)"
        final_response = ollama_chat(prompt, llama_history, model="llama3:latest")

    # Recherche web auto si LLM ne sait pas
    if any(x in str(final_response).lower() for x in ["je ne sais pas", "je n'ai pas la réponse"]):
        speak("Je vais chercher sur le web, un instant...")
        web_answer = web_search(user_input)
        final_response = final_response + "\n🔎 D'après le web :\n" + str(web_answer)

    # Feedback/satisfaction utilisateur
    if "merci" in user_input.lower():
        add_feedback("merci")
        nb_merci = sum(1 for f in memory["feedback"] if "merci" in f["feedback"])
        if nb_merci in [3, 5, 10]:
            speak("Merci de votre confiance ! Si vous souhaitez m'aider à m'améliorer, dites-le moi ou donnez-moi un feedback.")
    if repetition_count >= 3:
        speak(f"Vous avez posé plusieurs fois la même question : '{user_input.strip()}'. Voulez-vous de l'aide ou souhaitez-vous lancer un diagnostic ?")

    return final_response[:300]

# ---- MAIN PROGRAMME ----

def main_gui():
    from PySide6.QtWidgets import QApplication

    # Préchargement TTS pour réactivité (XTTS, pyttsx3, etc)
    try:
        preload_tts()
        ensure_voice_cache()  # <--- Ajout ici : génère les samples voix manquants
    except Exception:
        pass

    app = QApplication(sys.argv)
    gui = WilliamGUI()
    gui.show()
    gui.append_text("Bienvenue dans WILLIAM, assistant IA vocal évolutif !", "#b200ff")
    gui.set_diagnostic("⏳")

    history = []

    def on_toggle_listen(active):
        if active:
            gui.append_text("<i>Écoute vocale activée...</i>", "#ffd700")
            def listen_and_respond():
                user_input = listen(gui_callback=gui.show_live_transcription)
                if not user_input:
                    gui.append_text("<i>Aucune entrée vocale détectée.</i>", "#ff5555")
                    return
                gui.append_text(f"<b>Vous :</b> {user_input}", "#36e636")
                response = get_response(user_input, history)
                gui.append_text(f"<b>William :</b> {response}", "#fff")
                speak(response)
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": response})
            threading.Thread(target=listen_and_respond, daemon=True).start()
        else:
            gui.append_text("<i>Écoute désactivée.</i>", "#ffd700")

    gui.toggle_listen.connect(on_toggle_listen)

    # Diagnostic affiché dans la GUI (optionnel, si tu as un module diagnostic)
    try:
        from diagnostic import run_diagnostic
        erreurs = run_diagnostic()
        if not erreurs or all(info["status"] == "OK" for info in erreurs.values()):
            gui.set_diagnostic("✅")
        else:
            gui.set_diagnostic("❌")
    except Exception:
        gui.set_diagnostic("❌")

    # === Ajout du bouton Mode REPAIR ===
    repair_btn = QPushButton("Mode REPAIR")
    gui.layout.addWidget(repair_btn)  # <-- SANS les parenthèses
    def open_repair():
        panel = RepairPanel()
        panel.show()
    repair_btn.clicked.connect(open_repair)

    sys.exit(app.exec())

if __name__ == "__main__":
    # Auto-création dossiers critiques
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    os.makedirs("data/tts_cache", exist_ok=True)
    main_gui()