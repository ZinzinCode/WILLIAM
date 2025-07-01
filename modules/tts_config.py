"""
TTSManager optimisé pour WillIAM
- Synthèse vocale intelligente avec sélection dynamique du moteur, fallback robuste, et lecture naturelle.
- Nettoyage de la ponctuation pour éviter les pauses excessives sur XTTS/Coqui.
- Initialisation rapide, chargement unique des modèles, gestion efficace des ressources.
"""

import os
import logging
import tempfile
from pathlib import Path
import re
import threading

def normalize_tts_text(text):
    """Lisse la ponctuation pour éviter les longues pauses sur certains moteurs TTS."""
    text = re.sub(r"[.!?;:]", ",", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

class TTSManager:
    def __init__(self):
        self.tts_engine = None
        self.engine_type = None
        self.voice_samples_dir = Path("data/voice_samples")
        self.voice_samples_dir.mkdir(parents=True, exist_ok=True)

        # Configuration des voix par priorité
        self.tts_config = {
            "xtts": {
                "model": "tts_models/multilingual/multi-dataset/xtts_v2",
                "sample_file": "male_sample.wav",
                "language": "fr"
            },
            "coqui": {
                "models": [
                    "tts_models/fr/mai/tacotron2-DDC",  # Masculine
                    "tts_models/fr/css10/vits",
                ]
            },
            "edge": {
                "voice": "fr-FR-HenriNeural",
                "rate": "+0%",
                "pitch": "+0Hz"
            }
        }
        self._init_lock = threading.Lock()
        self._init_thread = threading.Thread(target=self._initialize_tts, daemon=True)
        self._init_thread.start()
        self._init_thread.join(15)  # Laisse jusqu'à 15s pour initialiser (chargement lourd sur CPU)

    def _initialize_tts(self):
        with self._init_lock:
            if self._try_xtts():
                return
            if self._try_coqui():
                return
            if self._try_edge():
                return
            self._init_pyttsx3()

    def _try_xtts(self):
        try:
            from TTS.api import TTS
            sample_path = self.voice_samples_dir / self.tts_config["xtts"]["sample_file"]
            if not sample_path.exists():
                logging.warning(f"Échantillon vocal non trouvé: {sample_path}")
                return False
            self.tts_engine = TTS(self.tts_config["xtts"]["model"])
            self.engine_type = "xtts"
            logging.info("✅ XTTS initialisé")
            return True
        except Exception as e:
            logging.warning(f"XTTS non disponible: {e}")
            return False

    def _try_coqui(self):
        try:
            from TTS.api import TTS
            for model in self.tts_config["coqui"]["models"]:
                try:
                    self.tts_engine = TTS(model)
                    self.engine_type = "coqui"
                    logging.info(f"✅ Coqui TTS initialisé: {model}")
                    return True
                except Exception as e:
                    logging.debug(f"Modèle {model} non disponible: {e}")
            return False
        except ImportError:
            logging.warning("Coqui TTS non installé")
            return False

    def _try_edge(self):
        try:
            import edge_tts
            self.engine_type = "edge"
            logging.info("✅ Edge TTS initialisé")
            return True
        except ImportError:
            logging.warning("Edge TTS non installé")
            return False

    def _init_pyttsx3(self):
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.engine_type = "pyttsx3"
            # Sélectionne une voix française si dispo
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'fr' in voice.name.lower() or 'french' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.8)
            logging.info("✅ pyttsx3 initialisé (fallback)")
        except Exception as e:
            logging.error(f"Impossible d'initialiser pyttsx3: {e}")
            self.engine_type = None

    def speak(self, text, save_to_file=None):
        """Synthétise le texte avec le meilleur moteur disponible (lecture complète en un bloc, ponctuation lissée)."""
        if not text or not text.strip():
            return
        # Pour éviter un blocage si l'init a échoué
        if self._init_thread.is_alive():
            self._init_thread.join(5)
        try:
            if self.engine_type == "xtts":
                self._speak_xtts(text, save_to_file)
            elif self.engine_type == "coqui":
                self._speak_coqui(text, save_to_file)
            elif self.engine_type == "edge":
                self._speak_edge(text, save_to_file)
            elif self.engine_type == "pyttsx3":
                self._speak_pyttsx3(text)
            else:
                logging.error("Aucun moteur TTS disponible")
                print(f"🤖 WillIAM: {text}")
        except Exception as e:
            logging.error(f"Erreur synthèse vocale: {e}")
            print(f"🤖 WillIAM: {text}")

    def _speak_xtts(self, text, save_to_file=None):
        text = normalize_tts_text(text)
        config = self.tts_config["xtts"]
        sample_path = self.voice_samples_dir / config["sample_file"]
        output_file = save_to_file or tempfile.mktemp(suffix=".wav")
        self.tts_engine.tts_to_file(
            text=text,
            file_path=output_file,
            speaker_wav=str(sample_path),
            language=config["language"]
        )
        self._play_audio_file(output_file)
        if not save_to_file:
            os.remove(output_file)

    def _speak_coqui(self, text, save_to_file=None):
        text = normalize_tts_text(text)
        output_file = save_to_file or tempfile.mktemp(suffix=".wav")
        self.tts_engine.tts_to_file(
            text=text,
            file_path=output_file
        )
        self._play_audio_file(output_file)
        if not save_to_file:
            os.remove(output_file)

    def _speak_edge(self, text, save_to_file=None):
        text = normalize_tts_text(text)
        import asyncio
        import edge_tts
        async def _edge_tts():
            config = self.tts_config["edge"]
            output_file = save_to_file or tempfile.mktemp(suffix=".wav")
            communicate = edge_tts.Communicate(
                text=text,
                voice=config["voice"],
                rate=config["rate"],
                pitch=config["pitch"]
            )
            await communicate.save(output_file)
            return output_file
        output_file = asyncio.run(_edge_tts())
        self._play_audio_file(output_file)
        if not save_to_file:
            os.remove(output_file)

    def _speak_pyttsx3(self, text):
        text = normalize_tts_text(text)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def _play_audio_file(self, file_path):
        """Lecture audio robuste, multiplateforme, sans écho ni coupure."""
        try:
            import pygame
            pygame.mixer.init()
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(60)
                pygame.mixer.music.unload()
            finally:
                pygame.mixer.quit()
        except ImportError:
            logging.warning("pygame non disponible pour la lecture audio")
            # Fallback système
            if os.name == 'nt':
                os.system(f'start /wait "" "{file_path}"')
            elif os.name == 'posix':
                os.system(f'afplay "{file_path}" 2>/dev/null || aplay "{file_path}" 2>/dev/null')

    def get_engine_info(self):
        return {
            "engine": self.engine_type,
            "available": self.engine_type is not None,
            "quality": {
                "xtts": "Excellente (clonage vocal)",
                "coqui": "Très bonne (local)",
                "edge": "Bonne (cloud)",
                "pyttsx3": "Basique (système)"
            }.get(self.engine_type, "Inconnue")
        }

# Instance globale
tts_manager = TTSManager()

# API compatible
def speak(text, save_to_file=None):
    """Interface compatible pour la synthèse vocale."""
    # Thread pour ne jamais bloquer la boucle principale
    threading.Thread(target=tts_manager.speak, args=(text, save_to_file), daemon=True).start()

def get_tts_info():
    """Infos sur le moteur TTS courant."""
    return tts_manager.get_engine_info()