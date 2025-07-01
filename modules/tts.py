import threading
import torch
import os
import tempfile
import time
import logging
import platform
import wave
from pathlib import Path

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Robust WAV check ---
def is_valid_wav(filepath):
    try:
        with wave.open(filepath, "rb") as f:
            params = f.getparams()
            if params.nframes < int(params.framerate * 0.1):
                return False
            f.readframes(1)
        return True
    except Exception as e:
        logger.warning(f"Vérif WAV échouée sur {filepath}: {e}")
        return False

# --- Fallback bip audio (sécurité ultime) ---
def fallback_audio(output_path, duration=0.5, freq=440):
    try:
        import numpy as np
        import scipy.io.wavfile
        samplerate = 22050
        t = np.linspace(0, duration, int(duration * samplerate), False)
        beep = (0.5 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
        scipy.io.wavfile.write(output_path, samplerate, beep)
        logger.warning(f"Fallback bip généré: {output_path}")
    except Exception as e:
        logger.error(f"Impossible de générer le fallback audio: {e}")
    return output_path

# --- 1. Configuration XTTS ---
class TTSConfig:
    def __init__(self):
        self.cuda_available = self._check_cuda()
        self.device = "cuda" if self.cuda_available else "cpu"
        self.temp_dir = Path(tempfile.gettempdir()) / "william_tts"
        self.temp_dir.mkdir(exist_ok=True)
        self.speaker_wav_path = str(Path("data/voice_samples/male_sample.wav"))
    def _check_cuda(self):
        try:
            return torch.cuda.is_available() and torch.cuda.device_count() > 0
        except Exception as e:
            logger.warning(f"CUDA check failed: {e}")
            return False

config = TTSConfig()

# --- 2. Gestionnaire XTTS robuste ---
class XTTSManager:
    def __init__(self):
        self.model = None
        self.is_loading = False
        self.load_failed = False
        self.lock = threading.Lock()

    def get_model(self, force_reload=False):
        if self.model is not None and not force_reload:
            return self.model
        if self.load_failed and not force_reload:
            return None
        with self.lock:
            if self.model is not None and not force_reload:
                return self.model
            if self.is_loading:
                while self.is_loading:
                    time.sleep(0.1)
                return self.model
            return self._load_model(force_reload=force_reload)

    def _load_model(self, force_reload=False):
        self.is_loading = True
        try:
            logger.info("Chargement du modèle XTTS...")
            from TTS.api import TTS
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            self.model = TTS(model_name, gpu=config.cuda_available)
            # Test rapide du modèle avec speaker_wav obligatoire
            test_speaker = config.speaker_wav_path if os.path.exists(config.speaker_wav_path) else None
            test_text = "Test"
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
                self.model.tts_to_file(
                    text=test_text,
                    file_path=f.name,
                    language="fr",
                    speaker_wav=test_speaker
                )
            logger.info(f"✅ XTTS chargé avec succès sur {config.device}")
            self.load_failed = False
            return self.model
        except ImportError as e:
            logger.error(f"❌ TTS library non installée: {e}")
            logger.info("💡 Installez avec: pip install TTS")
            self.load_failed = True
            self.model = None
            return None
        except Exception as e:
            logger.error(f"❌ Erreur chargement XTTS: {e}")
            self.load_failed = True
            self.model = None
            return None
        finally:
            self.is_loading = False

    def reload(self):
        logger.info("Reload manuel du modèle XTTS")
        return self.get_model(force_reload=True)

    def preload_async(self):
        threading.Thread(target=self.get_model, daemon=True).start()

xtts_manager = XTTSManager()

# --- 3. Gestionnaire audio robuste ---
class AudioManager:
    def __init__(self):
        self.pygame_initialized = False
        self.lock = threading.Lock()

    def _init_pygame(self):
        if not self.pygame_initialized:
            try:
                import pygame
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
                self.pygame_initialized = True
                logger.info("✅ Pygame audio initialisé")
            except Exception as e:
                logger.error(f"❌ Erreur initialisation pygame: {e}")
                raise

    def play_audio_file(self, file_path):
        with self.lock:
            try:
                import pygame
                self._init_pygame()
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(50)
            except Exception as e:
                logger.error(f"❌ Erreur lecture audio: {e}")
                # Fallback minimal
                if platform.system() == "Windows":
                    os.system(f'start /wait "" "{file_path}"')
                elif platform.system() == "Darwin":
                    os.system(f'afplay "{file_path}"')
                else:
                    os.system(f'aplay "{file_path}"')
            finally:
                try:
                    import pygame
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                except Exception:
                    pass

audio_manager = AudioManager()

# --- 4. Synthèse vocale robuste ---
def speak(text, language="fr", speaker_wav=None, speed=1.0, async_mode=True):
    if not text or not text.strip():
        return
    target = _speak_robust
    args = (text.strip(), language, speaker_wav, speed)
    if async_mode:
        threading.Thread(target=target, args=args, daemon=True).start()
    else:
        return target(*args)

def speak_sync(text, language="fr", speaker_wav=None, speed=1.0):
    """Version synchrone, retourne True si succès, False sinon."""
    return _speak_robust(text, language, speaker_wav, speed)

def _speak_robust(text, language, speaker_wav, speed):
    # XTTS en priorité
    temp_file = config.temp_dir / f"tts_{int(time.time() * 1000)}.wav"
    ok = _try_xtts_synthesis(text, language, speaker_wav, speed, temp_file)
    if ok:
        return True
    # Fallback pyttsx3 si XTTS échoue
    logger.info("Fallback vers pyttsx3...")
    ok2 = _speak_pyttsx3_fallback(text, speed, temp_file)
    if ok2:
        return True
    # Fallback bip universel
    logger.warning("Fallback ultime: bip audio")
    fallback_audio(str(temp_file))
    audio_manager.play_audio_file(str(temp_file))
    return False

def _try_xtts_synthesis(text, language, speaker_wav, speed, temp_file):
    try:
        model = xtts_manager.get_model()
        if model is None:
            return False
        speaker_reference = speaker_wav or config.speaker_wav_path
        if not (speaker_reference and os.path.exists(speaker_reference)):
            logger.error(f"Aucun speaker_wav valide pour XTTS : {speaker_reference}")
            return False
        model.tts_to_file(
            text=text,
            file_path=str(temp_file),
            speaker_wav=speaker_reference,
            language=language,
            split_sentences=True,
        )
        if not temp_file.exists() or temp_file.stat().st_size == 0 or not is_valid_wav(str(temp_file)):
            logger.error("Fichier audio XTTS vide, corrompu ou non créé")
            return False
        audio_manager.play_audio_file(str(temp_file))
        temp_file.unlink(missing_ok=True)
        logger.info("✅ Synthèse XTTS réussie")
        return True
    except Exception as e:
        logger.error(f"❌ Synthèse XTTS: {e}")
        try:
            # Force reload auto du modèle XTTS sur erreur, puis retente (une seule fois)
            xtts_manager.reload()
        except Exception as reload_e:
            logger.error(f"❌ Reload XTTS échoué: {reload_e}")
        return False

def _speak_pyttsx3_fallback(text, speed, temp_file):
    try:
        if platform.system() == "Windows":
            import pythoncom
            pythoncom.CoInitialize()
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        french_voice = None
        for voice in voices:
            voice_name = voice.name.lower()
            voice_id = voice.id.lower()
            if any(keyword in voice_name for keyword in ['hortense', 'marie', 'claire']):
                french_voice = voice.id
                break
            elif any(keyword in voice_id for keyword in ['fr', 'french', 'france']):
                french_voice = voice.id
                break
        if french_voice:
            engine.setProperty('voice', french_voice)
            logger.info(f"✅ Voix française sélectionnée: {french_voice}")
        else:
            logger.warning("⚠️ Aucune voix française trouvée, utilisation de la voix par défaut")
        engine.setProperty('rate', int(180 * speed))
        engine.setProperty('volume', 0.9)
        # Tente d'enregistrer dans temp_file et lire
        engine.save_to_file(text, str(temp_file))
        engine.runAndWait()
        if not temp_file.exists() or temp_file.stat().st_size == 0 or not is_valid_wav(str(temp_file)):
            logger.error("Fichier audio pyttsx3 vide ou corrompu")
            return False
        audio_manager.play_audio_file(str(temp_file))
        temp_file.unlink(missing_ok=True)
        logger.info("✅ Synthèse pyttsx3 réussie")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur pyttsx3: {e}")
        print(f"🔊 [TTS]: {text}")
        return False

# --- 5. Utilitaires ---
def set_speaker_reference(wav_file_path):
    if os.path.exists(wav_file_path):
        config.speaker_wav_path = wav_file_path
        logger.info(f"✅ Référence vocale définie: {wav_file_path}")
    else:
        logger.error(f"❌ Fichier audio introuvable: {wav_file_path}")

def preload_tts():
    logger.info("🚀 Préchargement du système TTS...")
    xtts_manager.preload_async()

def get_available_voices():
    voices_info = {
        "xtts_available": xtts_manager.get_model() is not None,
        "pyttsx3_voices": []
    }
    try:
        import pyttsx3
        engine = pyttsx3.init()
        for voice in engine.getProperty('voices'):
            voices_info["pyttsx3_voices"].append({
                "id": voice.id,
                "name": voice.name,
                "languages": getattr(voice, 'languages', [])
            })
    except Exception as e:
        logger.error(f"Erreur énumération voix pyttsx3: {e}")
    return voices_info

def cleanup_temp_files():
    try:
        for temp_file in config.temp_dir.glob("tts_*.wav"):
            temp_file.unlink()
        logger.info("🧹 Fichiers temporaires nettoyés")
    except Exception as e:
        logger.error(f"Erreur nettoyage: {e}")

# --- 6. Test et diagnostic ---
def test_tts():
    print("🧪 Test du système TTS...")
    print("Test XTTS...")
    model = xtts_manager.get_model()
    if model:
        print("✅ XTTS disponible")
        speak("Bonjour, je teste la synthèse vocale XTTS.", async_mode=False)
    else:
        print("❌ XTTS non disponible")
    time.sleep(2)
    print("Test pyttsx3...")
    _speak_pyttsx3_fallback("Test de la synthèse vocale de secours.", 1.0, config.temp_dir / "pyttsx3_test.wav")
    print(f"Device: {config.device}")
    print(f"CUDA disponible: {config.cuda_available}")
    voices = get_available_voices()
    print(f"Voix pyttsx3 disponibles: {len(voices['pyttsx3_voices'])}")

if __name__ == "__main__":
    test_tts()