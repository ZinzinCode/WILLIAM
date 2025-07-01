class CognitiveMemory:
    # ... (reste du code inchangé)
    def __init__(self):
        self.memory = self._load_memory()
        self.facts = self.memory.get("facts", {})
        self.errors = self.memory.get("errors", [])
        self.experiences = self.memory.get("experiences", [])
        self.user_feedback = self.memory.get("user_feedback", [])
        self.repetitions = self.memory.get("repetitions", {})
        # ...

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