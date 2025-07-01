import json
import datetime
import os
import threading
from pathlib import Path

class ContextManager:
    def __init__(self, context_file="william_context.json"):
        """Initialise le gestionnaire de contexte"""
        self.context_file = Path(context_file)
        self.context_data = {
            "user_preferences": {},
            "conversation_history": [],
            "session_info": {},
            "system_state": {},
            "created": datetime.datetime.now().isoformat(),
            "last_updated": datetime.datetime.now().isoformat()
        }
        self.lock = threading.Lock()
        self.load_context()
        print("📋 Gestionnaire de contexte initialisé")
    
    def load_context(self):
        """Charge le contexte depuis le fichier"""
        try:
            if self.context_file.exists():
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.context_data.update(loaded_data)
                print(f"📂 Contexte chargé depuis {self.context_file}")
            else:
                print("📝 Nouveau contexte créé")
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement du contexte: {e}")
    
    def save_context(self):
        """Sauvegarde le contexte dans le fichier"""
        try:
            with self.lock:
                self.context_data["last_updated"] = datetime.datetime.now().isoformat()
                with open(self.context_file, 'w', encoding='utf-8') as f:
                    json.dump(self.context_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde du contexte: {e}")
    
    def add_conversation(self, user_input, assistant_response):
        """Ajoute un échange à l'historique"""
        conversation_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response,
            "session_id": self.get_session_id()
        }
        
        with self.lock:
            self.context_data["conversation_history"].append(conversation_entry)
            
            # Limite l'historique à 100 entrées
            if len(self.context_data["conversation_history"]) > 100:
                self.context_data["conversation_history"] = self.context_data["conversation_history"][-100:]
        
        self.save_context()
    
    def get_recent_conversations(self, count=5):
        """Retourne les conversations récentes"""
        with self.lock:
            return self.context_data["conversation_history"][-count:]
    
    def set_user_preference(self, key, value):
        """Définit une préférence utilisateur"""
        with self.lock:
            self.context_data["user_preferences"][key] = {
                "value": value,
                "updated": datetime.datetime.now().isoformat()
            }
        self.save_context()
    
    def get_user_preference(self, key, default=None):
        """Récupère une préférence utilisateur"""
        with self.lock:
            pref = self.context_data["user_preferences"].get(key)
            return pref["value"] if pref else default
    
    def update_system_state(self, component, state):
        """Met à jour l'état d'un composant système"""
        with self.lock:
            self.context_data["system_state"][component] = {
                "state": state,
                "timestamp": datetime.datetime.now().isoformat()
            }
        self.save_context()
    
    def get_system_state(self, component):
        """Récupère l'état d'un composant système"""
        with self.lock:
            return self.context_data["system_state"].get(component, {}).get("state")
    
    def start_session(self):
        """Démarre une nouvelle session"""
        session_id = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with self.lock:
            self.context_data["session_info"] = {
                "session_id": session_id,
                "start_time": datetime.datetime.now().isoformat(),
                "interactions_count": 0
            }
        self.save_context()
        return session_id
    
    def end_session(self):
        """Termine la session actuelle"""
        with self.lock:
            if "session_info" in self.context_data:
                self.context_data["session_info"]["end_time"] = datetime.datetime.now().isoformat()
        self.save_context()
    
    def increment_interaction(self):
        """Incrémente le compteur d'interactions"""
        with self.lock:
            if "session_info" in self.context_data:
                self.context_data["session_info"]["interactions_count"] = \
                    self.context_data["session_info"].get("interactions_count", 0) + 1
        self.save_context()
    
    def get_session_id(self):
        """Retourne l'ID de session actuel"""
        with self.lock:
            return self.context_data.get("session_info", {}).get("session_id", "unknown")
    
    def get_conversation_stats(self):
        """Retourne des statistiques sur les conversations"""
        with self.lock:
            total_conversations = len(self.context_data["conversation_history"])
            
            if total_conversations == 0:
                return {
                    "total_conversations": 0,
                    "first_conversation": None,
                    "last_conversation": None,
                    "current_session_interactions": 0
                }
            
            first_conv = self.context_data["conversation_history"][0]["timestamp"]
            last_conv = self.context_data["conversation_history"][-1]["timestamp"]
            current_session_interactions = self.context_data.get("session_info", {}).get("interactions_count", 0)
            
            return {
                "total_conversations": total_conversations,
                "first_conversation": first_conv,
                "last_conversation": last_conv,
                "current_session_interactions": current_session_interactions
            }
    
    def search_conversations(self, query, limit=10):
        """Recherche dans l'historique des conversations"""
        query_lower = query.lower()
        results = []
        
        with self.lock:
            for conv in reversed(self.context_data["conversation_history"]):
                if (query_lower in conv["user"].lower() or 
                    query_lower in conv["assistant"].lower()):
                    results.append(conv)
                    if len(results) >= limit:
                        break
        
        return results
    
    def clear_history(self):
        """Efface l'historique des conversations"""
        with self.lock:
            self.context_data["conversation_history"] = []
        self.save_context()
        print("🗑️ Historique des conversations effacé")
    
    def export_context(self, export_file=None):
        """Exporte le contexte vers un fichier"""
        if not export_file:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            export_file = f"william_context_export_{timestamp}.json"
        
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.context_data, f, indent=2, ensure_ascii=False)
            print(f"📤 Contexte exporté vers {export_file}")
            return export_file
        except Exception as e:
            print(f"⚠️ Erreur lors de l'export: {e}")
            return None
    
    def get_context_summary(self):
        """Retourne un résumé du contexte"""
        stats = self.get_conversation_stats()
        
        summary = f"""
📊 Résumé du contexte William:
• Total conversations: {stats['total_conversations']}
• Session actuelle: {self.get_session_id()}
• Interactions session: {stats['current_session_interactions']}
• Préférences utilisateur: {len(self.context_data['user_preferences'])}
• États système: {len(self.context_data['system_state'])}
"""
        
        if stats['first_conversation']:
            summary += f"• Première conversation: {stats['first_conversation'][:19]}\n"
        if stats['last_conversation']:
            summary += f"• Dernière conversation: {stats['last_conversation'][:19]}\n"
        
        return summary.strip()

class WilliamContextManager:
    def __init__(self):
        self.history = []

    def get_context_prompt(self):
        # Construit un contexte à partir de l'historique
        if not self.history:
            return ""
        # Limite à 4 derniers échanges pour la rapidité
        context_lines = []
        for entry in self.history[-4:]:
            context_lines.append(f"Utilisateur: {entry['user']}\nWilliam: {entry['william']}")
        return "\n".join(context_lines)

    def update_history(self, user_input, response):
        self.history.append({"user": user_input, "william": response})

# Instance globale
_context_manager = None

def get_context_manager():
    """Retourne l'instance globale du gestionnaire de contexte"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager

if __name__ == "__main__":
    # Test du module
    cm = ContextManager()
    
    # Test des fonctionnalités
    cm.start_session()
    cm.add_conversation("Bonjour", "Bonjour ! Comment allez-vous ?")
    cm.set_user_preference("langue", "français")
    cm.update_system_state("tts", "actif")
    
    print(cm.get_context_summary())
    
    # Test de recherche
    results = cm.search_conversations("bonjour")
    print(f"Résultats de recherche: {len(results)}")