import speech_recognition as sr

def listen(timeout=8):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Parlez, j'écoute...")
        recognizer.pause_threshold = 0.8
        recognizer.energy_threshold = 300
        try:
            audio = recognizer.listen(source, timeout=timeout)
            text = recognizer.recognize_google(audio, language="fr-FR")
            print(f"🧠 Vous avez dit : {text}")
            return text
        except sr.WaitTimeoutError:
            print("⌛ Aucun son détecté.")
            return ""
        except sr.UnknownValueError:
            print("🤔 Je n'ai pas compris.")
            return ""
        except sr.RequestError:
            print("❌ Problème de connexion à Google.")
            return ""