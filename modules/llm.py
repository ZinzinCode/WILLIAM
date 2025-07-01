import json
import datetime
import random
import re
from modules.memory import all_facts, add_fact

def get_habits_from_memory():
    """Retourne un dict {intent: count} calculé depuis la mémoire (pour démo, à remplacer par vrai calcul)"""
    # Ici tu pourrais extraire les habitudes depuis un fichier, une base ou un module dédié
    # Pour la démo, on simule :
    habits = {}  # {"greeting": 5, "time_date": 3, ...}
    try:
        with open("data/cognitive_memory.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            habits = data.get("habits", {})
    except Exception:
        pass
    return habits

def get_facts_for_prompt(max_facts=5):
    """Récupère les faits enregistrés pour enrichir le prompt LLM"""
    facts = all_facts()
    if not facts:
        return ""
    # On limite le nombre de faits pour ne pas surcharger le prompt
    selected = list(facts.items())[-max_facts:]
    return "\n".join(f"- {k}: {v}" for k, v in selected)

def query_llm(prompt, max_tokens=150):
    """
    Simule un appel à un LLM. À remplacer par l'appel réel à votre LLM (Ollama, API, etc.)
    Injecte automatiquement les faits mémorisés et habitudes dans le prompt.
    """
    # -- Exemples de commandes "intelligentes" mémoire --
    prompt_lower = prompt.lower()
    if prompt_lower.startswith("souviens-toi que"):
        fait = prompt[15:].strip().rstrip(".")
        add_fact(fait, fait)
        return "Je m'en souviendrai."
    if prompt_lower.startswith("qu'as-tu appris"):
        mem = all_facts()
        if mem:
            return "Voici ce que j'ai retenu :\n" + "\n".join(f"- {v}" for v in mem.values())
        else:
            return "Je n'ai encore rien appris de particulier."
    
    # -- Injection mémoire cognitive (faits & habitudes) dans le prompt --
    facts_str = get_facts_for_prompt()
    habits = get_habits_from_memory()
    habits_str = ""
    if habits:
        # On prend l'habitude la plus fréquente
        sorted_habits = sorted(habits.items(), key=lambda x: x[1], reverse=True)
        intent, count = sorted_habits[0]
        if count >= 3:
            habits_str = (f"\nL'utilisateur pose souvent des questions de type '{intent}' "
                          f"(fréquence : {count}). Adapte ta réponse en conséquence.")
    
    if facts_str or habits_str:
        prompt = (f"Connaissances à retenir pour la conversation :\n{facts_str}{habits_str}\n\n{prompt}")

    # -- Simulation LLM classique --
    # (À remplacer par votre vrai modèle)
    return f"[LLM] Réponse générée pour : {prompt[:max_tokens]}"

class LanguageModel:
    def __init__(self):
        """Initialise le modèle de langage"""
        self.name = "William"
        self.context_history = []
        self.max_history = 10
        self.personality = {
            "friendly": True,
            "helpful": True,
            "curious": True,
            "polite": True
        }
        
        # Réponses pré-définies pour certaines questions communes
        self.predefined_responses = {
            "qui es-tu": "Je suis William, votre assistant personnel. Je suis là pour vous aider avec vos questions et tâches quotidiennes.",
            "comment allez-vous": "Je vais très bien, merci ! Comment puis-je vous aider aujourd'hui ?",
            "bonjour": "Bonjour ! Je suis ravi de vous parler. Comment puis-je vous assister ?",
            "bonsoir": "Bonsoir ! J'espère que vous passez une excellente soirée. Que puis-je faire pour vous ?",
            "merci": "Je vous en prie ! C'est un plaisir de vous aider. Y a-t-il autre chose que je puisse faire ?",
            "au revoir": "Au revoir ! Ce fut un plaisir de vous aider. À bientôt !",
            "quelle heure": f"Il est actuellement {datetime.datetime.now().strftime('%H:%M')}.",
            "quel jour": f"Nous sommes {datetime.datetime.now().strftime('%A %d %B %Y')}."
        }
        
        print("🧠 Modèle de langage initialisé")
    
    def add_to_context(self, user_input, response):
        """Ajoute un échange à l'historique de contexte"""
        self.context_history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "user": user_input,
            "assistant": response
        })
        
        # Limite la taille de l'historique
        if len(self.context_history) > self.max_history:
            self.context_history.pop(0)
    
    def get_context_summary(self):
        """Retourne un résumé du contexte récent"""
        if not self.context_history:
            return "Pas d'historique de conversation."
        
        recent = self.context_history[-3:]  # 3 derniers échanges
        summary = "Contexte récent:\n"
        for i, exchange in enumerate(recent, 1):
            summary += f"{i}. Vous: {exchange['user'][:50]}...\n"
            summary += f"   Moi: {exchange['assistant'][:50]}...\n"
        return summary
    
    def detect_intent(self, text):
        """Détecte l'intention de l'utilisateur"""
        text_lower = text.lower().strip()
        
        # Salutations
        if any(word in text_lower for word in ["bonjour", "salut", "hello", "bonsoir"]):
            return "greeting"
        
        # Questions sur l'heure/date
        if any(word in text_lower for word in ["heure", "temps", "jour", "date"]):
            return "time_date"
        
        # Informations personnelles
        if any(word in text_lower for word in ["qui es-tu", "qui êtes-vous", "ton nom", "votre nom"]):
            return "identity"
        
        # Aide/support
        if any(word in text_lower for word in ["aide", "aidez-moi", "help", "comment", "pouvez-vous"]):
            return "help"
        
        # Calcul/mathématiques
        if any(word in text_lower for word in ["calcul", "combien", "+", "-", "*", "/", "="]):
            return "calculation"
        
        # Au revoir
        if any(word in text_lower for word in ["au revoir", "bye", "à bientôt", "goodbye"]):
            return "farewell"
        
        return "general"
    
    def handle_calculation(self, text):
        """Traite les calculs simples"""
        try:
            # Extraction des nombres et opérations
            numbers = re.findall(r'\d+(?:\.\d+)?', text)
            
            if "+" in text and len(numbers) >= 2:
                result = float(numbers[0]) + float(numbers[1])
                return f"Le résultat de {numbers[0]} + {numbers[1]} est {result}"
            elif "-" in text and len(numbers) >= 2:
                result = float(numbers[0]) - float(numbers[1])
                return f"Le résultat de {numbers[0]} - {numbers[1]} est {result}"
            elif "*" in text and len(numbers) >= 2:
                result = float(numbers[0]) * float(numbers[1])
                return f"Le résultat de {numbers[0]} × {numbers[1]} est {result}"
            elif "/" in text and len(numbers) >= 2:
                if float(numbers[1]) != 0:
                    result = float(numbers[0]) / float(numbers[1])
                    return f"Le résultat de {numbers[0]} ÷ {numbers[1]} est {result}"
                else:
                    return "Désolé, la division par zéro n'est pas possible."
        except:
            pass
        
        return "Je ne peux pas effectuer ce calcul. Pouvez-vous reformuler ?"
    
    def generate_response(self, user_input):
        """Génère une réponse basée sur l'entrée utilisateur, en tenant compte des faits et habitudes"""
        if not user_input or not user_input.strip():
            return "Je n'ai pas bien compris. Pouvez-vous répéter ?"
        
        user_input = user_input.strip()
        user_lower = user_input.lower()

        # Vérification des réponses pré-définies
        for key, response in self.predefined_responses.items():
            if key in user_lower:
                self.add_to_context(user_input, response)
                return response
        
        # Détection d'intention et réponse appropriée
        intent = self.detect_intent(user_input)
        
        if intent == "greeting":
            responses = [
                "Bonjour ! Comment allez-vous aujourd'hui ?",
                "Salut ! Que puis-je faire pour vous ?",
                "Bonjour ! Je suis là pour vous aider.",
                "Hello ! Ravi de vous parler !"
            ]
            response = random.choice(responses)
        
        elif intent == "time_date":
            now = datetime.datetime.now()
            if "heure" in user_lower:
                response = f"Il est {now.strftime('%H:%M')}."
            else:
                response = f"Nous sommes le {now.strftime('%A %d %B %Y')}."
        
        elif intent == "identity":
            response = "Je suis William, votre assistant personnel intelligent. Je suis là pour vous aider avec diverses tâches et répondre à vos questions."
        
        elif intent == "calculation":
            response = self.handle_calculation(user_input)
        
        elif intent == "help":
            response = """Je peux vous aider avec plusieurs choses :
• Répondre à vos questions générales
• Effectuer des calculs simples
• Vous donner l'heure et la date
• Avoir une conversation amicale
• Vous assister dans vos tâches quotidiennes

Que souhaitez-vous faire ?"""
        
        elif intent == "farewell":
            responses = [
                "Au revoir ! Ce fut un plaisir de vous aider.",
                "À bientôt ! Passez une excellente journée.",
                "Au revoir ! N'hésitez pas à revenir quand vous voulez.",
                "À plus tard ! Prenez soin de vous."
            ]
            response = random.choice(responses)
        
        else:
            # Réponse générale intelligente, avec prise en compte des faits/habitudes
            facts_str = get_facts_for_prompt()
            habits = get_habits_from_memory()
            habits_info = ""
            if habits:
                sorted_habits = sorted(habits.items(), key=lambda x: x[1], reverse=True)
                intent_h, count = sorted_habits[0]
                if count >= 3:
                    habits_info = f"(Tu poses souvent des questions de type '{intent_h}') "
            responses = [
                f"{habits_info}C'est intéressant ce que vous dites sur '{user_input}'. Pouvez-vous m'en dire plus ?",
                f"{habits_info}Je comprends que vous parliez de '{user_input}'. Comment puis-je vous aider avec cela ?",
                f"{habits_info}Merci de partager cela. En quoi puis-je vous assister concernant '{user_input}' ?",
                f"{habits_info}C'est une question intéressante. Pouvez-vous me donner plus de contexte ?",
                f"{habits_info}Je vois. Comment puis-je vous aider davantage avec cette question ?"
            ]
            # Ajoute au contexte pour l'apprentissage
            response = random.choice(responses)
        
        self.add_to_context(user_input, response)
        return response
    
    def get_stats(self):
        """Retourne des statistiques sur les conversations"""
        return {
            "total_exchanges": len(self.context_history),
            "session_start": self.context_history[0]["timestamp"] if self.context_history else None,
            "last_exchange": self.context_history[-1]["timestamp"] if self.context_history else None
        }

if __name__ == "__main__":
    # Test du module
    llm = LanguageModel()
    
    test_inputs = [
        "Bonjour",
        "Qui es-tu ?",
        "Quelle heure est-il ?",
        "Combien font 15 + 27 ?",
        "Au revoir"
    ]
    
    for test_input in test_inputs:
        response = llm.generate_response(test_input)
        print(f"👤 {test_input}")
        print(f"🤖 {response}\n")