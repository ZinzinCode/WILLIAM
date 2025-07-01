import datetime
import os
import json
from tts import speak

try:
    from stt import listen
except ImportError:
    listen = None

from ollama_api import ollama_chat

# --- Mémoire cognitive persistante ---
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

# --- Détection d'intention/utilité ---
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

# --- Web search & OCR integration ---
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

# --- Log/statistique proactive ---
LOG_FILE = "william_diagnostics/logs/errors.log"
def analyze_error_log(max_lines=200):
    if not os.path.exists(LOG_FILE):
        return {"count": 0, "recent_errors": [], "suggest_clear": False}
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-max_lines:]
    error_count = sum(1 for l in lines if "ERROR:" in l or "Erreur" in l)
    recent_errors = [l.strip() for l in lines if "ERROR:" in l or "Erreur" in l][-5:]
    suggest_clear = os.path.getsize(LOG_FILE) > 1_000_000
    return {"count": error_count, "recent_errors": recent_errors, "suggest_clear": suggest_clear}

def prompt_diagnostic_if_needed():
    stats = analyze_error_log()
    if stats["count"] > 10:
        speak("🚨 J'ai rencontré de nombreuses erreurs récentes. Voulez-vous lancer un diagnostic ou nettoyer les logs ('clear logs') ?")
    if stats["suggest_clear"]:
        speak("⚠️ Les logs d’erreurs sont volumineux. Dites 'clear logs' pour les nettoyer.")

# --- Génération de réponse principale ---
def get_response(user_input, history):
    # Ajoute un prompt système si première question à Llama 3
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

    # Génération code ou général
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

print("🤖 Initialisation de William...")
print(f"📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
    from diagnostic import run_diagnostic
    erreurs = run_diagnostic()
    modules_critiques = [m for m, info in erreurs.items() if info["status"] == "ERROR" and m in ["wcm", "tts"]]
    if modules_critiques:
        print("\n❌ Impossible de démarrer William : modules critiques manquants.")
        exit(1)
except Exception as e:
    print(f"⚠️ Erreur pendant le diagnostic : {e}")
    print("⛔ Démarrage annulé pour éviter des comportements instables.")
    exit(1)

print("\n🤖 William est prêt ! Tapez 'quit' pour quitter.")

history = []
log_check_counter = 0

while True:
    mode = input("Mode [t]exte ou [v]ocal ? (t/v): ").strip().lower()
    if mode == "v" and listen:
        user_input = listen()
    else:
        user_input = input("👤 Vous: ").strip()
    if not user_input:
        continue

    if user_input.lower() in ["quit", "exit"]:
        print("👋 Au revoir !")
        break

    if user_input.lower() == "diagnostic":
        try:
            run_diagnostic()
        except Exception:
            print("Diagnostic indisponible.")
        continue

    if user_input.lower() == "clear logs":
        try:
            if os.path.exists(LOG_FILE):
                os.remove(LOG_FILE)
                print("🧹 Les logs ont été nettoyés.")
            else:
                print("Aucun log à nettoyer.")
        except Exception as e:
            print(f"Impossible de nettoyer les logs : {e}")
        continue

    response = get_response(user_input, history)
    print(f"🤖 William: {response}")
    speak(response)

    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": response})

    # Vérification proactive des logs/statistiques toutes les 10 interactions
    log_check_counter += 1
    if log_check_counter % 10 == 0:
        prompt_diagnostic_if_needed()