import speech_recognition as sr

def listen(timeout=8, use_whisper=True, language="fr-FR", gui_callback=None):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Parlez, j'écoute...")
        recognizer.pause_threshold = 0.8
        recognizer.energy_threshold = 300
        try:
            audio = recognizer.listen(source, timeout=timeout)
        except sr.WaitTimeoutError:
            print("⌛ Aucun son détecté.")
            if gui_callback:
                gui_callback("<i>Aucun son détecté.</i>", "#ff5555")
            return ""
        
        # Tentative Whisper local
        if use_whisper:
            try:
                text = recognizer.recognize_whisper(
                    audio,
                    language=language.split('-')[0],
                    model="base"
                )
                print(f"🧠 (Whisper) Vous avez dit : {text}")
                if gui_callback:
                    gui_callback(f"<b>Vous (Whisper):</b> {text}", "#36e636")
                return text
            except Exception as e:
                print(f"💥 Whisper local échoué : {e}")
                if gui_callback:
                    gui_callback(f"<i>Whisper local indisponible ({e}), essai Google...</i>", "#ffd700")
        # Fallback Google API
        try:
            text = recognizer.recognize_google(audio, language=language)
            print(f"🧠 (Google) Vous avez dit : {text}")
            if gui_callback:
                gui_callback(f"<b>Vous (Google):</b> {text}", "#36e636")
            return text
        except sr.UnknownValueError:
            print("🤔 Je n'ai pas compris.")
            if gui_callback:
                gui_callback("<i>Je n'ai pas compris.</i>", "#ff5555")
            return ""
        except sr.RequestError:
            print("❌ Problème de connexion à Google.")
            if gui_callback:
                gui_callback("<i>Connexion Google impossible.</i>", "#ff5555")
            return ""