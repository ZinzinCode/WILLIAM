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