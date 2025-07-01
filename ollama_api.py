import requests
import json

def ollama_chat(prompt, history=None, model="deepseek-coder:latest"):
    messages = history[:] if history else []
    messages.append({"role": "user", "content": prompt})
    try:
        print("DEBUG - Envoi à Ollama:", messages)
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages},
            timeout=120,
            stream=True
        )
        chunks = []
        for line in r.iter_lines():
            if line:
                obj = json.loads(line.decode("utf-8"))
                if "message" in obj and "content" in obj["message"]:
                    chunks.append(obj["message"]["content"])
        answer = "".join(chunks).strip()
        print("DEBUG - Réponse Ollama:", answer)
        if answer:
            return answer
        return "[Aucune réponse générée par l'IA]"
    except Exception as e:
        print("Erreur Ollama:", e)
        return "Je rencontre un problème pour réfléchir, désolé."