# assistant.py
import sys
import os
from datetime import datetime

# Ajouter le dossier modules au PATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

class WilliamAssistant:
    def __init__(self, config=None):
        self.config = config or {}
        self.voice_enabled = self.config.get("voice_enabled", False)
        self.text_only = self.config.get("text_only", False)
        self.diagnostic_enabled = self.config.get("diagnostic_enabled", True)
        
        # Modules optionnels
        self.wcm = None
        self.tts = None
        self.stt = None
        self.llm = None
        
        # État des modules
        self.module_status = {}
        
        # Initialiser les modules
        self._initialize_modules()
        
    def _initialize_modules(self):
        """Initialise les modules disponibles"""
        
        # Gestionnaire de contexte (essentiel)
        try:
            from wcm import WilliamContextManager
            self.wcm = WilliamContextManager()
            self.module_status["wcm"] = True
            print("✅ Gestionnaire de contexte chargé")
        except Exception as e:
            print(f"❌ Impossible de charger le gestionnaire de contexte: {e}")
            self.module_status["wcm"] = False
        
        # Text-to-Speech (optionnel)
        if not self.text_only:
            try:
                from tts import speak
                self.tts = speak
                self.module_status["tts"] = True
                print("✅ Synthèse vocale disponible")
            except Exception as e:
                print(f"⚠️ Synthèse vocale non disponible: {e}")
                self.module_status["tts"] = False
        
        # Speech-to-Text (optionnel)
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
        
        # LLM (optionnel - peut utiliser une API externe)
        try:
            from llm import query_llm
            self.llm = query_llm
            self.module_status["llm"] = True
            print("✅ Modèle de langage disponible")
        except Exception as e:
            print(f"⚠️ Modèle de langage non disponible: {e}")
            self.module_status["llm"] = False
    
    def _check_module_health(self):
        """Vérifie l'état des modules critiques"""
        if self.diagnostic_enabled:
            try:
                from william_diagnostics.diagnostic import get_system_status
                return get_system_status()
            except ImportError:
                pass
        return self.module_status
    
    def _handle_diagnostic_command(self, user_input):
        """Gère les commandes de diagnostic"""
        if not self.diagnostic_enabled:
            return False
            
        lower_input = user_input.lower()
        
        if "diagnostic" in lower_input or "état système" in lower_input:
            try:
                from william_diagnostics.diagnostic import run_diagnostic
                results = run_diagnostic()
                
                response = "📊 État du système:\n"
                for module, result in results.items():
                    if result["status"] == "OK":
                        response += f"✅ {module}: Fonctionnel\n"
                    else:
                        response += f"❌ {module}: {result['explanation']}\n"
                
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
        
        return False
    
    def _respond(self, message):
        """Envoie une réponse à l'utilisateur"""
        print(f"🤖 William: {message}")
        
        # Synthèse vocale si disponible
        if self.tts and self.module_status.get("tts") and not self.text_only:
            try:
                self.tts(message)
            except Exception as e:
                print(f"⚠️ Erreur TTS: {e}")
    
    def _get_user_input(self):
        """Récupère l'entrée utilisateur (texte ou vocal)"""
        if self.voice_enabled and self.stt and self.module_status.get("stt"):
            try:
                print("🎤 En écoute... (Entrée pour passer en mode texte)")
                # Implémentation simplifiée - en réalité il faudrait gérer l'enregistrement
                user_input = input("👤 Vous: ")
                return user_input
            except Exception as e:
                print(f"⚠️ Erreur reconnaissance vocale: {e}")
                return input("👤 Vous: ")
        else:
            return input("👤 Vous: ")
    
    def _process_input(self, user_input):
        """Traite l'entrée utilisateur"""
        
        # Commandes spéciales
        if user_input.lower() in ["quit", "exit", "au revoir", "bye"]:
            return False
        
        # Commandes de diagnostic
        if self._handle_diagnostic_command(user_input):
            return True
        
        # Mise à jour du contexte
        if self.wcm and self.module_status.get("wcm"):
            try:
                context = self.wcm.get_context_prompt()
            except Exception:
                context = ""
        else:
            context = ""
        
        # Générer une réponse
        response = self._generate_response(user_input, context)
        
        # Mettre à jour l'historique
        if self.wcm and self.module_status.get("wcm"):
            try:
                self.wcm.update_history(user_input, response)
            except Exception as e:
                print(f"⚠️ Erreur mise à jour contexte: {e}")
        
        # Envoyer la réponse
        self._respond(response)
        
        return True
    
    def _generate_response(self, user_input, context=""):
        """Génère une réponse à partir de l'entrée utilisateur"""
        
        # Utiliser le LLM si disponible
        if self.llm and self.module_status.get("llm"):
            try:
                prompt = f"{context}\nUtilisateur: {user_input}\nWilliam:"
                response = self.llm(prompt, max_tokens=150)
                return str(response).strip()
            except Exception as e:
                print(f"⚠️ Erreur LLM: {e}")
        
        # Réponses de base si pas de LLM
        responses = {
            "bonjour": "Bonjour ! Comment puis-je vous aider ?",
            "comment ça va": "Je fonctionne correctement, merci !",
            "aide": "Je suis William, votre assistant. Tapez 'diagnostic' pour vérifier l'état du système.",
            "merci": "De rien ! N'hésitez pas si vous avez d'autres questions.",
        }
        
        # Recherche de mots-clés
        user_lower = user_input.lower()
        for keyword, response in responses.items():
            if keyword in user_lower:
                return response
        
        # Réponse par défaut
        return f"J'ai bien reçu votre message : '{user_input}'. Comment puis-je vous aider ?"
    
    def run(self):
        """Boucle principale de l'assistant"""
        
        print("\n🤖 William est prêt ! Tapez 'quit' pour quitter.")
        
        # Message d'accueil
        welcome_msg = "Bonjour ! Je suis William, votre assistant personnel."
        if self.diagnostic_enabled:
            welcome_msg += " Tapez 'diagnostic' pour vérifier l'état du système."
        
        self._respond(welcome_msg)
        
        # Boucle principale
        try:
            while True:
                try:
                    user_input = self._get_user_input()
                    
                    if not user_input.strip():
                        continue
                    
                    # Traiter l'entrée
                    if not self._process_input(user_input):
                        break
                
                except KeyboardInterrupt:
                    print("\n👋 Au revoir !")
                    break
                except Exception as e:
                    print(f"❌ Erreur: {e}")
                    
                    # Log de l'erreur si diagnostic activé
                    if self.diagnostic_enabled:
                        try:
                            import traceback
                            with open("william_diagnostics/logs/errors.log", "a", encoding="utf-8") as f:
                                f.write(f"\n[{datetime.now().isoformat()}] ERROR:\n")
                                f.write(traceback.format_exc())
                                f.write("\n" + "-"*30 + "\n")
                        except:
                            pass
                    
                    self._respond("Désolé, j'ai rencontré une erreur. Pouvez-vous reformuler ?")
        
        except Exception as e:
            print(f"❌ Erreur critique dans la boucle principale: {e}")
        
        finally:
            # Nettoyage
            if self.diagnostic_enabled:
                try:
                    from william_diagnostics.diagnostic import stop_continuous_monitoring
                    stop_continuous_monitoring()
                except ImportError:
                    pass
            
            print("👋 William s'arrête...")
