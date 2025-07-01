"""
Assistant WillIAM amélioré avec intégration Ollama
Gestion intelligente des réponses et du contexte
"""

import requests
import json
import logging
from datetime import datetime
import re

class WillIAMAssistant:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model = "llama3.2:3b"  # Modèle rapide et efficace
        self.context_window = 10  # Nombre de messages à garder en contexte
        self.system_prompt = self._build_system_prompt()
        
        # Vérifier la disponibilité d'Ollama
        self.ollama_available = self._check_ollama()
        
        if not self.ollama_available:
            logging.warning("Ollama non disponible, mode dégradé activé")
    
    def _build_system_prompt(self):
        """Construit le prompt système pour WillIAM"""
        return """Tu es WillIAM, un assistant vocal français intelligent et serviable.

PERSONNALITÉ:
- Tu es poli, courtois et professionnel
- Tu réponds en français naturel
- Tu es direct et concis dans tes réponses
- Tu peux faire preuve d'humour léger quand approprié
- Tu es patient et pédagogique

CAPACITÉS:
- Répondre aux questions générales
- Aider avec des tâches informatiques
- Donner l'heure et la date
- Expliquer des concepts
- Assister dans la programmation
- Gérer des rappels et tâches

CONTRAINTES:
- Garde tes réponses vocales courtes (1-3 phrases max)
- Pour les explications longues, propose de continuer si nécessaire
- Évite les listes à puces dans les réponses vocales
- Privilégie un langage naturel et conversationnel

CONTEXTE ACTUEL:
- Date: {date}
- Heure: {heure}
- Tu fonctionnes en mode vocal principalement
"""
    
    def _check_ollama(self):
        """Vérifie si Ollama est disponible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def _format_system_prompt(self):
        """Formate le prompt système avec les infos actuelles"""
        now = datetime.now()
        return self.system_prompt.format(
            date=now.strftime("%d/%m/%Y"),
            heure=now.strftime("%H:%M")
        )
    
    def _truncate_history(self, history):
        """Tronque l'historique pour maintenir la fenêtre de contexte"""
        if len(history) > self.context_window * 2:  # * 2 car user + assistant
            return history[-(self.context_window * 2):]
        return history
    
    def _ollama_generate(self, messages):
        """Génère une réponse via Ollama"""
        try:
            # Préparer les messages avec le système
            full_messages = [
                {"role": "system", "content": self._format_system_prompt()}
            ] + messages
            
            payload = {
                "model": self.model,
                "messages": full_messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_ctx": 4096
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["message"]["content"].strip()
            else:
                logging.error(f"Erreur Ollama: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Erreur génération Ollama: {e}")
            return None
    
    def _fallback_response(self, user_input):
        """Réponses de base quand Ollama n'est pas disponible"""
        user_lower = user_input.lower().strip()
        
        # Réponses de base
        responses = {
            # Salutations
            r"(bonjour|salut|hey|coucou)": [
                "Bonjour ! Comment puis-je vous aider ?",
                "Salut ! Que puis-je faire pour vous ?",
                "Bonjour ! Je suis à votre service."
            ],
            
            # Heure et date
            r"(quelle heure|heure|time)": self._get_time_response,
            r"(quelle date|date|aujourd'hui)": self._get_date_response,
            
            # État
            r"(comment ça va|comment allez-vous|ça va)": [
                "Ça va très bien, merci ! Et vous ?",
                "Tout va bien de mon côté ! Comment puis-je vous aider ?",
                "Je fonctionne parfaitement, merci de demander !"
            ],
            
            # Capacités
            r"(que peux-tu faire|aide|help|capacités)": [
                "Je peux répondre à vos questions, donner l'heure, expliquer des concepts, et bien plus encore ! Que souhaitez-vous savoir ?"
            ],
            
            # Au revoir
            r"(au revoir|bye|à bientôt|stop)": [
                "Au revoir ! À bientôt !",
                "À la prochaine ! Bonne journée !",
                "Au revoir ! N'hésitez pas à revenir !"
            ],
            
            # Remerciements
            r"(merci|thanks)": [
                "De rien ! Je suis là pour ça !",
                "Avec plaisir ! Autre chose ?",
                "C'est normal ! Puis-je vous aider davantage ?"
            ]
        }
        
        # Recherche de correspondance
        for pattern, response in responses.items():
            if re.search(pattern, user_lower):
                if callable(response):
                    return response()
                elif isinstance(response, list):
                    import random
                    return random.choice(response)
                else:
                    return response
        
        # Réponse par défaut
        return "Je ne suis pas sûr de comprendre. Pouvez-vous reformuler votre question ?"
    
    def _get_time_response(self):
        """Retourne l'heure actuelle"""
        now = datetime.now()
        return f"Il est {now.strftime('%H heures %M')}."
    
    def _get_date_response(self):
        """Retourne la date actuelle"""
        now = datetime.now()
        days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        months = ["janvier", "février", "mars", "avril", "mai", "juin",
                 "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        
        day_name = days[now.weekday()]
        month_name = months[now.month - 1]
        
        return f"Nous sommes {day_name} {now.day} {month_name} {now.year}."
    
    def get_response(self, user_input, history=None):
        """Génère une réponse à l'input utilisateur"""
        if not user_input.strip():
            return "Je vous écoute."
        
        # Préparer l'historique
        if history is None:
            history = []
        
        # Tronquer l'historique si nécessaire
        history = self._truncate_history(history)
        
        # Convertir l'historique au format Ollama
        messages = []
        for entry in history[-self.context_window:]:  # Garder seulement les derniers messages
            messages.append({
                "role": entry.get("role", "user"),
                "content": entry.get("content", "")
            })
        
        # Ajouter le message actuel
        messages.append({
            "role": "user", 
            "content": user_input
        })
        
        # Essayer Ollama d'abord
        if self.ollama_available:
            response = self._ollama_generate(messages)
            if response:
                return response
            else:
                # Ollama a échoué, repasser en mode dégradé
                self.ollama_available = False
                logging.warning("Ollama indisponible, basculement en mode dégradé")
        
        # Mode dégradé
        return self._fallback_response(user_input)
    
    def get_status(self):
        """Retourne le statut de l'assistant"""
        return {
            "name": "WillIAM",
            "version": "1.0",
            "ollama_available": self.ollama_available,
            "model": self.model if self.ollama_available else "Fallback",
            "mode": "IA avancée" if self.ollama_available else "Mode dégradé"
        }

# Instance globale
william = WillIAMAssistant()

# Fonctions compatibles avec l'ancien code
def assistant_response(user_input, history=None):
    """Interface compatible pour générer une réponse"""
    return william.get_response(user_input, history)

def get_assistant_status():
    """Informations sur l'état de l'assistant"""
    return william.get_status()

def chat_loop():
    """Boucle de chat textuel pour tests"""
    print("=== Mode Chat WillIAM ===")
    print("Tapez 'quit' pour quitter\n")
    
    history = []
    
    while True:
        try:
            user_input = input("Vous: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'stop']:
                print("WillIAM: Au revoir !")
                break
            
            if not user_input:
                continue
            
            # Générer la réponse
            response = william.get_response(user_input, history)
            print(f"WillIAM: {response}\n")
            
            # Mettre à jour l'historique
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\nWillIAM: Au revoir !")
            break
        except Exception as e:
            print(f"Erreur: {e}")
