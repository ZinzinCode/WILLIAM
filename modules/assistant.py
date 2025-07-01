import sys
import os
import threading
import json
from datetime import datetime

# Ajouter le dossier modules au PATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

MEMORY_PATH = "data/cognitive_memory.json"
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

class CognitiveMemory:
    def __init__(self):
        self.memory = self._load_memory()
        self.facts = self.memory.get("facts", {})
        self.errors = self.memory.get("errors", [])
        self.experiences = self.memory.get("experiences", [])
        self.habits = self.memory.get("habits", {})
        self.suggestions = self.memory.get("suggestions", [])
        self.user_feedback = self.memory.get("user_feedback", [])
        self.repetitions = self.memory.get("repetitions", {})
        self.last_update = self.memory.get("last_update", None)

    def _load_memory(self):
        if os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_memory(self):
        self.memory["facts"] = self.facts
        self.memory["errors"] = self.errors
        self.memory["experiences"] = self.experiences
        self.memory["habits"] = self.habits
        self.memory["suggestions"] = self.suggestions
        self.memory["user_feedback"] = self.user_feedback
        self.memory["repetitions"] = self.repetitions
        self.memory["last_update"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

    def add_fact(self, key, value):
        self.facts[key] = value
        self._save_memory()

    def add_error(self, error, context=""):
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "context": context
        })
        self._save_memory()

    def add_experience(self, user_input, response, was_successful=True):
        self.experiences.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "response": response,
            "success": was_successful
        })
        intent = self._extract_intent(user_input)
        if intent:
            self.habits[intent] = self.habits.get(intent, 0) + 1
        self._save_memory()

    def add_suggestion(self, suggestion):
        self.suggestions.append({
            "timestamp": datetime.now().isoformat(),
            "suggestion": suggestion
        })
        self._save_memory()

    def add_user_feedback(self, feedback):
        self.user_feedback.append({
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback
        })
        self._save_memory()

    def record_repetition(self, user_input):
        key = user_input.strip().lower()
        self.repetitions[key] = self.repetitions.get(key, 0) + 1
        self._save_memory()

    def get_most_repeated(self):
        if not self.repetitions:
            return None, 0
        key, count = max(self.repetitions.items(), key=lambda x: x[1])
        return key, count

    def get_fact(self, key):
        return self.facts.get(key)

    def get_recent_errors(self, n=5):
        return self.errors[-n:]

    def get_recent_experiences(self, n=10):
        return self.experiences[-n:]

    def get_habits(self):
        return dict(sorted(self.habits.items(), key=lambda x: x[1], reverse=True))

    def get_suggestions(self, n=5):
        return self.suggestions[-n:]

    def _extract_intent(self, text):
        text = text.lower()
        if any(w in text for w in ["bonjour", "salut", "hello"]):
            return "salutation"
        if "heure" in text:
            return "question_heure"
        if "date" in text or "jour" in text:
            return "question_date"
        if "merci" in text:
            return "remerciement"
        if "diagnostic" in text:
            return "diagnostic"
        if "aide" in text:
            return "aide"
        if "souviens-toi" in text:
            return "ajout_memoire"
        if "corrige-toi" in text or "améliore-toi" in text:
            return "auto_correction"
        if any(w in text for w in ["au revoir", "bye"]):
            return "au_revoir"
        return "autre"

    def review_and_improve(self):
        report = []
        if self.errors:
            last_error = self.errors[-1]
            report.append(f"Dernière erreur : {last_error['error']} (contexte : {last_error['context']})")
            if "llm" in last_error["context"].lower():
                suggestion = "Conseil : vérifier la connexion au modèle LLM ou réduire la taille du contexte."
                self.add_suggestion(suggestion)
                report.append(suggestion)
        if self.habits:
            frequent = sorted(self.habits.items(), key=lambda x: x[1], reverse=True)[:2]
            for intent, count in frequent:
                if count >= 3:
                    suggestion = f"Suggestion : tu poses souvent des questions de type '{intent}', je peux anticiper ou automatiser ces réponses."
                    self.add_suggestion(suggestion)
                    report.append(suggestion)
        if self.suggestions:
            report.append("Suggestions récentes :")
            for s in self.get_suggestions(3):
                report.append(f"- {s['suggestion']}")
        return "\n".join(report) if report else "Aucune suggestion ou correction récente."

class WilliamAssistant:
    def __init__(self, config=None):
        self.config = config or {}
        self.voice_enabled = self.config.get("voice_enabled", False)
        self.text_only = self.config.get("text_only", False)
        self.diagnostic_enabled = self.config.get("diagnostic_enabled", True)
        self.wcm = None
        self.tts = None
        self.stt = None
        self.llm = None
        self.cognitive_memory = CognitiveMemory()
        self.module_status = {}
        self._log_check_counter = 0
        self._initialize_modules()

    def _initialize_modules(self):
        try:
            from wcm import WilliamContextManager
            self.wcm = WilliamContextManager()
            self.module_status["wcm"] = True
            print("✅ Gestionnaire de contexte chargé")
        except Exception as e:
            print(f"❌ Impossible de charger le gestionnaire de contexte: {e}")
            self.module_status["wcm"] = False
        if not self.text_only:
            try:
                from tts import speak
                self.tts = speak
                self.module_status["tts"] = True
                print("✅ Synthèse vocale disponible")
            except Exception as e:
                print(f"⚠️ Synthèse vocale non disponible: {e}")
                self.module_status["tts"] = False
        if self.voice_enabled:
            try:
                from stt import transcribe_audio, record_audio
                self.stt = {"transcribe": transcribe_audio, "record": record_audio}
                self.module_status["stt"] = True
                print("✅ Reconnaissance vocale disponible")
            except Exception as e:
                print(f"⚠️ Reconnaissance vocale non disponible: {e}")
                self.module_status["stt"] = False
                self.voice_enabled = False
        try:
            from llm import query_llm
            self.llm = query_llm
            self.module_status["llm"] = True
            print("✅ Modèle de langage disponible")
        except Exception as e:
            print(f"⚠️ Modèle de langage non disponible: {e}")
            self.module_status["llm"] = False

    def _web_search(self, query):
        try:
            from websearch import bing_search  # À adapter selon ton module
            # Résultat : texte ou dict
            result = bing_search(query)
            return result if result else "Aucun résultat web pertinent trouvé."
        except Exception as e:
            return f"Recherche web impossible : {e}"

    def _run_ocr(self):
        try:
            from ocr import read_screen
            return read_screen()
        except Exception as e:
            print(f"Erreur OCR : {e}")
            return None

    def _check_module_health(self):
        if self.diagnostic_enabled:
            try:
                from william_diagnostics.diagnostic import get_system_status
                return get_system_status()
            except ImportError:
                pass
        return self.module_status

    def _handle_diagnostic_command(self, user_input):
        lower_input = user_input.lower()
        if "diagnostic" in lower_input or "état système" in lower_input:
            try:
                from william_diagnostics.diagnostic import run_diagnostic
                results = run_diagnostic()
                response = "📊 État du système:\n"
                for module, result in results.items():
                    if result.get("status") == "OK":
                        response += f"✅ {module}: Fonctionnel\n"
                    else:
                        explanation = result.get("explanation") or result.get("message", "Erreur inconnue")
                        response += f"❌ {module}: {explanation}\n"
                self._respond(response)
                return True
            except ImportError:
                self._respond("⚠️ Module de diagnostic non disponible")
                return True
        elif "surveillance" in lower_input:
            if "arrêter" in lower_input or "stop" in lower_input:
                try:
                    from william_diagnostics.diagnostic import stop_continuous_monitoring
                    if stop_continuous_monitoring():
                        self._respond("🔄 Surveillance arrêtée")
                    else:
                        self._respond("⚠️ Aucune surveillance active")
                    return True
                except ImportError:
                    pass
            elif "démarrer" in lower_input or "start" in lower_input:
                try:
                    from william_diagnostics.diagnostic import start_continuous_monitoring
                    if start_continuous_monitoring():
                        self._respond("🔄 Surveillance démarrée")
                    else:
                        self._respond("⚠️ Surveillance déjà active")
                    return True
                except ImportError:
                    pass
        elif "améliore-toi" in lower_input or "corrige-toi" in lower_input or "donne-moi tes suggestions" in lower_input:
            result = self.cognitive_memory.review_and_improve()
            self._respond("🧠 Capacité d'amélioration :\n" + result)
            return True
        elif "habitude" in lower_input or "statistique" in lower_input:
            habits = self.cognitive_memory.get_habits()
            if habits:
                msg = "📈 Voici mes habitudes détectées :\n"
                for k, v in habits.items():
                    msg += f"- {k}: {v} fois\n"
                self._respond(msg)
            else:
                self._respond("Je n'ai pas encore détecté d'habitudes marquantes.")
            return True
        elif "erreur" in lower_input and "récente" in lower_input:
            errors = self.cognitive_memory.get_recent_errors()
            if errors:
                msg = "🪲 Dernières erreurs :\n"
                for err in errors:
                    msg += f"- {err['timestamp']}: {err['error']} (contexte : {err['context']})\n"
                self._respond(msg)
            else:
                self._respond("Aucune erreur récente mémorisée.")
            return True
        elif "souviens-toi que" in lower_input:
            fact = user_input[15:].strip()
            if fact:
                self.cognitive_memory.add_fact(fact, fact)
                self._respond("Je m'en souviendrai : " + fact)
            else:
                self._respond("Que dois-je retenir ?")
            return True
        elif "analyse log" in lower_input or "statistique erreur" in lower_input:
            stats = analyze_error_log()
            msg = f"📊 Sur les derniers logs : {stats['count']} erreurs détectées."
            if stats["recent_errors"]:
                msg += "\nExtraits récents :\n" + "\n".join(stats["recent_errors"])
            if stats["suggest_clear"]:
                msg += "\n⚠️ Les logs sont volumineux. Voulez-vous les nettoyer ? Dites 'clear logs' pour confirmer."
            self._respond(msg)
            return True
        elif "clear logs" in lower_input:
            try:
                if os.path.exists(LOG_FILE):
                    os.remove(LOG_FILE)
                    self._respond("🧹 Les logs ont été nettoyés.")
                else:
                    self._respond("Aucun log à nettoyer.")
            except Exception as e:
                self._respond(f"Impossible de nettoyer les logs : {e}")
            return True
        return False

    def _respond(self, message):
        print(f"🤖 William: {message}")
        if self.tts and self.module_status.get("tts") and not self.text_only:
            def speak_thread(msg):
                try:
                    self.tts(msg)
                except Exception as e:
                    print(f"⚠️ Erreur TTS: {e}")
            threading.Thread(target=speak_thread, args=(message,), daemon=True).start()

    def _get_user_input(self):
        if self.voice_enabled and self.stt and self.module_status.get("stt"):
            try:
                print("🎤 En écoute... (Entrée pour passer en mode texte)")
                user_input = input("👤 Vous: ")
                return user_input
            except Exception as e:
                print(f"⚠️ Erreur reconnaissance vocale: {e}")
                return input("👤 Vous: ")
        else:
            return input("👤 Vous: ")

    def _process_input(self, user_input):
        # OCR sur demande explicite
        ocr_triggers = [
            "que vois-tu à l’écran", "que vois-tu à l'ecran", "lis ce document", "scan écran", 
            "scan ecran", "lis l'écran", "lis l'ecran"
        ]
        if any(x in user_input.lower() for x in ocr_triggers):
            self._respond("📸 Analyse de l'écran/document en cours...")
            ocr_text = self._run_ocr()
            if ocr_text:
                fact_key = f"OCR du {datetime.now().isoformat()}"
                self.cognitive_memory.add_fact(fact_key, ocr_text)
                self._respond(f"Texte extrait :\n{ocr_text[:500]}" + ("..." if len(ocr_text) > 500 else ""))
            else:
                self._respond("Aucun texte n'a été détecté à l'écran ou sur le document.")
            return True

        if user_input.lower() in ["quit", "exit", "au revoir", "bye"]:
            return False
        if self._handle_diagnostic_command(user_input):
            return True
        if "merci" in user_input.lower():
            self.cognitive_memory.add_user_feedback("merci")
            merci_count = sum(1 for f in self.cognitive_memory.user_feedback if "merci" in f["feedback"])
            if merci_count in [3, 5, 10]:
                self._respond("😊 Merci de votre confiance ! Si vous souhaitez m'aider à m'améliorer, dites-le moi ou donnez-moi un feedback.")
        self.cognitive_memory.record_repetition(user_input)
        repeated, count = self.cognitive_memory.get_most_repeated()
        if count >= 3 and repeated == user_input.strip().lower():
            self._respond(f"🔄 Vous avez posé plusieurs fois la même question : '{user_input.strip()}'. Voulez-vous de l'aide ou souhaitez-vous lancer un diagnostic ?")
        self._log_check_counter += 1
        if self._log_check_counter % 10 == 0:
            stats = analyze_error_log()
            if stats["suggest_clear"]:
                self._respond("⚠️ Les logs d’erreurs sont volumineux. Dites 'clear logs' pour les nettoyer.")
        if self.wcm and self.module_status.get("wcm"):
            try:
                context = self.wcm.get_context_prompt()
            except Exception:
                context = ""
        else:
            context = ""
        facts = "\n".join(f"- {k}" for k in self.cognitive_memory.facts.keys())
        if facts:
            context = f"Infos importantes à retenir :\n{facts}\n\n{context}"
        def process():
            try:
                if user_input.lower().startswith("souviens-toi que"):
                    fact = user_input[15:].strip()
                    if fact:
                        self.cognitive_memory.add_fact(fact, fact)
                        self._respond("Je m'en souviendrai : " + fact)
                        self.cognitive_memory.add_experience(user_input, "mémoire ajoutée", True)
                    else:
                        self._respond("Que dois-je retenir ?")
                        self.cognitive_memory.add_experience(user_input, "mémoire non ajoutée", False)
                    return
                response = self._generate_response(user_input, context)
                if self.wcm and self.module_status.get("wcm"):
                    try:
                        self.wcm.update_history(user_input, response)
                    except Exception as e:
                        print(f"⚠️ Erreur mise à jour contexte: {e}")
                self.cognitive_memory.add_experience(user_input, response, was_successful=True)
                if any(w in user_input.lower() for w in ["super", "génial", "top", "bravo"]):
                    self.cognitive_memory.add_user_feedback("positif")
                if any(w in user_input.lower() for w in ["nul", "mauvais", "pas utile", "incompréhensible"]):
                    self.cognitive_memory.add_user_feedback("negatif")
                    self._respond("😢 Je suis désolé si je n'ai pas répondu à vos attentes. Voulez-vous m'indiquer ce qui n'allait pas ou essayer une commande d'aide ?")
                stats = analyze_error_log()
                if stats["count"] > 10:
                    self._respond("🚨 J'ai rencontré de nombreuses erreurs récemment. Voulez-vous lancer un diagnostic ou nettoyer les logs ('clear logs') ?")
                self._respond(response)
            except Exception as err:
                print(f"❌ Erreur lors du traitement de l'entrée: {err}")
                self.cognitive_memory.add_experience(user_input, str(err), was_successful=False)
                self.cognitive_memory.add_error(str(err), context=user_input)
                self._respond("Désolé, j'ai rencontré une erreur. Pouvez-vous reformuler ?")
        threading.Thread(target=process, daemon=True).start()
        return True

    def _generate_response(self, user_input, context=""):
        if self.llm and self.module_status.get("llm"):
            try:
                ctx = context if context else ""
                prompt = f"{ctx}\nUtilisateur: {user_input}\nWilliam:"
                response = self.llm(prompt, max_tokens=120)

                # Recherche web automatique si LLM ne sait pas
                if any(x in str(response).lower() for x in ["je ne sais pas", "je n'ai pas la réponse"]):
                    self._respond("Je vais chercher sur le web, un instant...")
                    web_answer = self._web_search(user_input)
                    if web_answer:
                        response = str(response).strip() + "\n🔎 D'après le web :\n" + str(web_answer)

                if "corrige-toi" in user_input.lower() or "améliore-toi" in user_input.lower():
                    suggestion = self.cognitive_memory.review_and_improve()
                    response += "\n[Suggestion cognitive] " + suggestion
                return str(response).strip()
            except Exception as e:
                print(f"⚠️ Erreur LLM: {e}")
        responses = {
            "bonjour": "Bonjour ! Comment puis-je vous aider ?",
            "comment ça va": "Je fonctionne correctement, merci !",
            "aide": "Je suis William, votre assistant. Tapez 'diagnostic' pour vérifier l'état du système.",
            "merci": "De rien ! N'hésitez pas si vous avez d'autres questions.",
        }
        user_lower = user_input.lower()
        for keyword, response in responses.items():
            if keyword in user_lower:
                return response
        return f"J'ai bien reçu votre message : '{user_input}'. Comment puis-je vous aider ?"

    def run(self):
        print("\n🤖 William est prêt ! Tapez 'quit' pour quitter.")
        welcome_msg = "Bonjour ! Je suis William, votre assistant personnel."
        if self.diagnostic_enabled:
            welcome_msg += " Tapez 'diagnostic' pour vérifier l'état du système."
        welcome_msg += " Tapez 'améliore-toi' pour mes suggestions d'amélioration."
        self._respond(welcome_msg)
        try:
            while True:
                try:
                    user_input = self._get_user_input()
                    if not user_input.strip():
                        continue
                    if not self._process_input(user_input):
                        break
                except KeyboardInterrupt:
                    print("\n👋 Au revoir !")
                    break
                except Exception as e:
                    print(f"❌ Erreur: {e}")
                    if self.diagnostic_enabled:
                        try:
                            import traceback
                            os.makedirs("william_diagnostics/logs", exist_ok=True)
                            with open("william_diagnostics/logs/errors.log", "a", encoding="utf-8") as f:
                                f.write(f"\n[{datetime.now().isoformat()}] ERROR:\n")
                                f.write(traceback.format_exc())
                                f.write("\n" + "-"*30 + "\n")
                        except Exception:
                            pass
                    self._respond("Désolé, j'ai rencontré une erreur. Pouvez-vous reformuler ?")
        except Exception as e:
            print(f"❌ Erreur critique dans la boucle principale: {e}")
        finally:
            if self.diagnostic_enabled:
                try:
                    from william_diagnostics.diagnostic import stop_continuous_monitoring
                    stop_continuous_monitoring()
                except ImportError:
                    pass
            print("👋 William s'arrête...")