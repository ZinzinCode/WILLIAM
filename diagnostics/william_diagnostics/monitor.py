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