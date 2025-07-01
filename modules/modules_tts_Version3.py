def speak(text):
    try:
        from TTS.api import TTS
        import pygame
        import os
        import tempfile

        SAMPLE = "data/voice_samples/male_sample.wav"
        if os.path.exists(SAMPLE):
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            wav_kwargs = dict(speaker_wav=SAMPLE, language="fr")
        else:
            tts = TTS("tts_models/fr/mai/tacotron2-DDC")
            wav_kwargs = {}

        # Découpe intelligente pour accélérer XTTS (sur GPU c'est rapide)
        sentences = [s.strip() for s in text.replace("!","!.").replace("?","?.").split(".") if s.strip()]
        temp_files = []
        for sentence in sentences:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
            tts.tts_to_file(text=sentence, file_path=temp_path, **wav_kwargs)
            temp_files.append(temp_path)

        pygame.mixer.init()
        for temp_path in temp_files:
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            os.remove(temp_path)
        pygame.mixer.quit()
    except Exception as e:
        print(f"⚠️ Erreur XTTS : {e}")
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as err:
            print("Impossible de lire la réponse :", err)