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