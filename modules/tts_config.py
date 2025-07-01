"""
Configuration TTS optimisée pour WillIAM
Gestion intelligente de la synthèse vocale avec fallbacks
"""

import os
import logging
from pathlib import Path

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
                    "tts_models/fr/mai/tacotron2-DDC",  # Voix masculine
                    "tts_models/fr/css10/vits",         # Alternative
                ]
            },
            "edge": {
                "voice": "fr-FR-HenriNeural",  # Voix masculine française
                "rate": "+0%",
                "pitch": "+0Hz"
            }
        }
        
        self._initialize_tts()
    
    def _initialize_tts(self):
        """Initialise le meilleur moteur TTS disponible"""
        
        # 1. Essayer XTTS (meilleure qualité avec clonage)
        if self._try_xtts():
            return
            
        # 2. Essayer Coqui TTS local
        if self._try_coqui():
            return
            
        # 3. Fallback vers Edge TTS
        if self._try_edge():
            return
            
        # 4. Dernier recours : pyttsx3
        self._init_pyttsx3()
    
    def _try_xtts(self):
        """Tente d'initialiser XTTS avec échantillon vocal"""
        try:
            from TTS.api import TTS
            
            sample_path = self.voice_samples_dir / self.tts_config["xtts"]["sample_file"]
            
            if not sample_path.exists():
                logging.warning(f"Échantillon vocal non trouvé: {sample_path}")
                return False
            
            self.tts_engine = TTS(self.tts_config["xtts"]["model"])
            self.engine_type = "xtts"
            
            logging.info("✅ XTTS initialisé avec succès")
            return True
            
        except Exception as e:
            logging.warning(f"XTTS non disponible: {e}")
            return False
    
    def _try_coqui(self):
        """Tente d'initialiser Coqui TTS local"""
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
                    continue
                    
            return False
            
        except ImportError:
            logging.warning("Coqui TTS non installé")
            return False
    
    def _try_edge(self):
        """Tente d'initialiser Edge TTS"""
        try:
            import edge_tts
            self.engine_type = "edge"
            
            logging.info("✅ Edge TTS initialisé")
            return True
            
        except ImportError:
            logging.warning("Edge TTS non installé")
            return False
    
    def _init_pyttsx3(self):
        """Initialise pyttsx3 comme fallback"""
        try:
            import pyttsx3
            
            self.tts_engine = pyttsx3.init()
            self.engine_type = "pyttsx3"
            
            # Configuration voix française si disponible
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'fr' in voice.name.lower() or 'french' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            # Configuration de base
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.8)
            
            logging.info("✅ pyttsx3 initialisé (fallback)")
            
        except Exception as e:
            logging.error(f"Impossible d'initialiser la synthèse vocale: {e}")
            self.engine_type = None
    
    def speak(self, text, save_to_file=None):
        """Synthétise le texte avec le meilleur moteur disponible"""
        
        if not text.strip():
            return
            
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
                print(f"🤖 WillIAM: {text}")  # Fallback texte
                
        except Exception as e:
            logging.error(f"Erreur synthèse vocale: {e}")
            print(f"🤖 WillIAM: {text}")  # Fallback texte
    
    def _speak_xtts(self, text, save_to_file=None):
        """Synthèse avec XTTS et clonage vocal"""
        config = self.tts_config["xtts"]
        sample_path = self.voice_samples_dir / config["sample_file"]
        
        output_file = save_to_file or "temp_speech.wav"
        
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
        """Synthèse avec Coqui TTS local"""
        output_file = save_to_file or "temp_speech.wav"
        
        self.tts_engine.tts_to_file(
            text=text,
            file_path=output_file
        )
        
        self._play_audio_file(output_file)
        
        if not save_to_file:
            os.remove(output_file)
    
    def _speak_edge(self, text, save_to_file=None):
        """Synthèse avec Edge TTS"""
        import asyncio
        import edge_tts
        import pygame
        
        async def _edge_tts():
            config = self.tts_config["edge"]
            output_file = save_to_file or "temp_speech.wav"
            
            communicate = edge_tts.Communicate(
                text=text,
                voice=config["voice"],
                rate=config["rate"],
                pitch=config["pitch"]
            )
            
            await communicate.save(output_file)
            return output_file
        
        # Exécution asynchrone
        output_file = asyncio.run(_edge_tts())
        self._play_audio_file(output_file)
        
        if not save_to_file:
            os.remove(output_file)
    
    def _speak_pyttsx3(self, text):
        """Synthèse avec pyttsx3"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def _play_audio_file(self, file_path):
        """Lit un fichier audio avec pygame"""
        try:
            import pygame
            
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Attendre la fin de la lecture
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
        except ImportError:
            logging.warning("pygame non disponible pour la lecture audio")
            # Alternative avec système
            if os.name == 'nt':  # Windows
                os.system(f'start /wait "" "{file_path}"')
            elif os.name == 'posix':  # Linux/macOS
                os.system(f'afplay "{file_path}" 2>/dev/null || aplay "{file_path}" 2>/dev/null')
    
    def get_engine_info(self):
        """Retourne des infos sur le moteur TTS actuel"""
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

# Fonctions compatibles avec l'ancien code
def speak(text, save_to_file=None):
    """Interface compatible pour la synthèse vocale"""
    tts_manager.speak(text, save_to_file)

def get_tts_info():
    """Informations sur le moteur TTS actuel"""
    return tts_manager.get_engine_info()
