from datetime import datetime

def notify_user(module, explanation, error):
    timestamp = datetime.now().isoformat()
    message = f"[{timestamp}] ⚠️ {module} a échoué : {explanation}\n{error}\n"
    print(message)
    
    with open("william_diagnostics/logs/log.txt", "a", encoding="utf-8") as f:
        f.write(message)
    
    # vocal feedback possible ici :
    from text_to_speech import speak
    speak(f"Problème détecté dans le module {module}. {explanation}")
