import threading
import torch
import os
import tempfile

# --- 1. Détection GPU/CUDA ---
def is_cuda_available():
    try:
        return torch.cuda.is_available()
    except Exception:
        return False

# --- 2. Initialisation XTTS globale (une seule fois) ---
_xtts_model = None

def get_xtts_model():
    global _xtts_model
    if _xtts_model is None:
        try:
            from TTS.api import TTS
            _xtts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=is_cuda_available())
        except Exception as e:
            print(f"[XTTS indisponible] {e}")
            _xtts_model = None
    return _xtts_model

# --- 3. Synthèse vocale threadée, fluide, fallback automatique ---
def speak(text):
    threading.Thread(target=_speak_impl, args=(text,), daemon=True).start()

def _speak_impl(text):
    model = get_xtts_model()
    if model:
        try:
            # Utilise un fichier temporaire pour éviter les collisions/conflits
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
            model.tts_to_file(text=text, file_path=temp_path, speaker_wav=None, language="fr")
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(50)
                pygame.mixer.music.unload()
                pygame.mixer.quit()
            finally:
                os.remove(temp_path)
            return
        except Exception as e:
            print(f"[XTTS erreur synthèse] {e}")
    # Fallback si XTTS indisponible ou erreur
    speak_fallback(text)

def speak_fallback(text):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        # Privilégie la voix française si dispo (ou Hortense si Windows)
        voices = engine.getProperty('voices')
        fr_voice = None
        for v in voices:
            if "hortense" in v.name.lower():
                fr_voice = v.id
                break
            if "fr" in v.id.lower() or "french" in v.name.lower():
                fr_voice = v.id
        if fr_voice:
            engine.setProperty('voice', fr_voice)
        engine.setProperty('rate', 180)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[pyttsx3 indisponible] {e}")
        print(f"[TTS Fallback]: {text}")

# --- Pour pré-charger XTTS au lancement ---
def preload_tts():
    threading.Thread(target=get_xtts_model, daemon=True).start()