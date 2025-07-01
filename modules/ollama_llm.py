import requests

def assistant_response(prompt, history=None, model="llama3"):
    """
    Génère une réponse depuis Ollama (LLM local).
    - prompt: le texte de l'utilisateur
    - history: une liste [{"role": "user"/"assistant", "content": "..."}] pour le contexte
    - model: le modèle Ollama à utiliser (ex: "llama3", "mistral", "phi3")
    """
    messages = history[:] if history else []
    messages.append({"role": "user", "content": prompt})

    r = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": model, "messages": messages}
    )
    response = r.json()
    if "message" in response and "content" in response["message"]:
        return response["message"]["content"]
    return response.get("response", "[Aucune réponse générée]")