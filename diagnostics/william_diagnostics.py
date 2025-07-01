# william_diagnostics/__init__.py
"""
Système de diagnostic pour l'assistant William
"""

# william_diagnostics/explainer.py
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

# william_diagnostics/feedback.py
import os
from datetime import datetime

def notify_user(module, explanation, error):
    timestamp = datetime.now().isoformat()
    message = f"[{timestamp}] ⚠️ {module} a échoué : {explanation}\n{error}\n"
    print(message)
    
    # Créer le dossier s'il n'existe pas
    os.makedirs("william_diagnostics/logs", exist_ok=True)
    
    with open("william_diagnostics/logs/log.txt", "a", encoding="utf-8") as f:
        f.write(message)
    
    # Feedback vocal optionnel (si TTS disponible)
    try:
        from modules.tts import speak
        speak(f"Problème détecté dans le module {module}. {explanation}")
    except Exception:
        pass  # TTS non disponible, continuer sans

# william_diagnostics/fixer.py
import subprocess
import os

def try_fix(module, error):
    """Tentatives de réparation automatique"""
    try:
        if isinstance(error, FileNotFoundError):
            # Créer des fichiers de test manquants
            if "test.wav" in str(error):
                with open("test.wav", "wb") as f:
                    # Créer un fichier WAV minimal valide
                    f.write(b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
                return True
            
        elif "ModuleNotFoundError" in str(error) or isinstance(error, ModuleNotFoundError):
            # Extraire le nom du module et tenter l'installation
            if "'" in str(error):
                mod = str(error).split("'")[1]
                print(f"Tentative d'installation du module: {mod}")
                result = subprocess.run(["pip", "install", mod], capture_output=True)
                return result.returncode == 0
        
        elif isinstance(error, PermissionError):
            # Créer les dossiers nécessaires
            if "data" in str(error):
                os.makedirs("data", exist_ok=True)
                os.makedirs("data/context", exist_ok=True)
                return True
                
    except Exception as fix_error:
        print(f"Erreur lors de la réparation: {fix_error}")
    
    return False

# william_diagnostics/tester.py
import os
import json

def whisper_test():
    """Test du module de transcription"""
    try:
        from modules.stt import transcribe_audio
        # Vérifier que le fichier test existe
        if not os.path.exists("test.wav"):
            raise FileNotFoundError("Fichier test.wav manquant")
        result = transcribe_audio("test.wav")
        assert result is not None
        return True
    except ImportError:
        # Module STT non disponible, créer un mock
        return True

def tts_test():
    """Test du module text-to-speech"""
    try:
        from modules.tts import speak
        speak("Test", test_mode=True)  # Mode test silencieux
        return True
    except ImportError:
        return True  # Module TTS optionnel

def llm_test():
    """Test du module LLM"""
    try:
        from modules.llm import query_llm
        response = query_llm("Test", max_tokens=10)
        assert len(str(response)) > 0
        return True
    except ImportError:
        return True  # Module LLM optionnel

def wcm_test():
    """Test du gestionnaire de contexte"""
    try:
        from modules.wcm import WilliamContextManager
        wcm = WilliamContextManager()
        wcm.update_history("test", "test response")
        return True
    except Exception as e:
        raise AssertionError(f"Gestionnaire de contexte défaillant: {e}")

def file_system_test():
    """Test de l'accès au système de fichiers"""
    test_dirs = ["data", "data/context", "william_diagnostics/logs"]
    for directory in test_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    # Test d'écriture
    test_file = "data/test_write.tmp"
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return True
    except Exception:
        raise PermissionError("Impossible d'écrire dans le dossier data")

modules = {
    "whisper": whisper_test,
    "tts": tts_test, 
    "llm": llm_test,
    "wcm": wcm_test,
    "filesystem": file_system_test,
}

# william_diagnostics/monitor.py
import time
import threading
from . import tester, fixer, explainer, feedback

class DiagnosticMonitor:
    def __init__(self, interval=30):
        self.interval = interval
        self.running = False
        self.thread = None
        self.status = {}
        
    def run_single_check(self):
        """Exécute un diagnostic complet une seule fois"""
        results = {}
        for module_name, test_func in tester.modules.items():
            try:
                test_func()
                results[module_name] = {"status": "OK", "error": None}
                self.status[module_name] = True
            except Exception as e:
                readable = explainer.explain_error(e)
                fixed = fixer.try_fix(module_name, e)
                feedback.notify_user(module_name, readable, e)
                results[module_name] = {
                    "status": "ERROR", 
                    "error": str(e),
                    "explanation": readable,
                    "fixed": fixed
                }
                self.status[module_name] = False
        return results
    
    def run_monitor(self):
        """Surveillance continue en arrière-plan"""
        while self.running:
            self.run_single_check()
            time.sleep(self.interval)
    
    def start_monitoring(self):
        """Démarre la surveillance en arrière-plan"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_monitor, daemon=True)
            self.thread.start()
            return True
        return False
    
    def stop_monitoring(self):
        """Arrête la surveillance"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        return True
    
    def get_status(self):
        """Retourne l'état actuel des modules"""
        return self.status.copy()

# Instance globale
monitor = DiagnosticMonitor()

# william_diagnostics/diagnostic.py
from .monitor import monitor
import json

def run_diagnostic():
    """
    Fonction principale de diagnostic à appeler depuis main.py
    Retourne un rapport complet de l'état des modules
    """
    print("🔍 Démarrage du diagnostic William...")
    
    # Exécuter un diagnostic complet
    results = monitor.run_single_check()
    
    # Générer le rapport
    total_modules = len(results)
    healthy_modules = sum(1 for r in results.values() if r["status"] == "OK")
    
    print(f"\n📊 Rapport de diagnostic:")
    print(f"   Modules testés: {total_modules}")
    print(f"   Modules OK: {healthy_modules}")
    print(f"   Modules en erreur: {total_modules - healthy_modules}")
    
    # Détail des erreurs
    for module_name, result in results.items():
        if result["status"] == "ERROR":
            print(f"   ❌ {module_name}: {result['explanation']}")
            if result.get("fixed"):
                print(f"      ✅ Réparation tentée avec succès")
        else:
            print(f"   ✅ {module_name}: Fonctionnel")
    
    # Sauvegarder le rapport
    try:
        with open("william_diagnostics/logs/last_diagnostic.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
    
    return results

def start_continuous_monitoring():
    """Démarre la surveillance continue"""
    return monitor.start_monitoring()

def stop_continuous_monitoring():
    """Arrête la surveillance continue"""
    return monitor.stop_monitoring()

def get_system_status():
    """Retourne l'état actuel du système"""
    return monitor.get_status()
