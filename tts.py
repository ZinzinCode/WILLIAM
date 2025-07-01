# modules/tts.py
"""
Module de synthèse vocale pour WillIAM Assistant
Supporte Edge TTS, pyttsx3, et Coqui TTS avec XTTS
"""

import json
import os
import asyncio
import platform
import subprocess
from pathlib import Path
from datetime import datetime

class VoiceEngine:
    """Gestionnaire principal de synthèse vocale"""
    
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.tts_config = self.config.get("tts", {})
        self.voice_engine = self.config.get("assistant", {}).get("voice_engine", "edge_tts")
        
        # Initialisation des moteurs
        self.edge_tts = None
        self.pyttsx3_engine = None
        self.coqui_tts = None
        
        # Dossier de sortie pour les fichiers audio
        self.output_dir = Path("data/audio_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🗣️ Moteur TTS sélectionné: {self.voice_engine}")
        self._init_engines()
    
    def _load_config(self, config_path):
        """Charge la configuration depuis le fichier JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ config.json introuvable, utilisation configuration par défaut")
            return self._default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Erreur lecture config.json: {e}")
            return self._default_config()
    
    def _default_config(self):
        """Configuration par défaut"""
        return {
            "assistant": {
                "voice_engine": "edge_tts"
            },
            "tts": {
                "edge_voice": "fr-FR-HenriNeural",
                "coqui_enabled": False,
                "xtts_enabled": False,
                "volume": 0.8,
                "speed": 1.0
            }
        }
    
    def _init_engines(self):
        """Initialise les moteurs TTS disponibles"""
        # Initialisation Edge TTS
        try:
            import edge_tts
            self.edge_tts = edge_tts
            print("✅ Edge TTS disponible")
        except ImportError:
            print("⚠️ Edge TTS non disponible")
        
        # Initialisation pyttsx3
        try:
            import pyttsx3
            self.pyttsx3_engine = pyttsx3.init()
            self._configure_pyttsx3()
            print("✅ pyttsx3 disponible")
        except ImportError:
            print("⚠️ pyttsx3 non disponible")
        except Exception as e:
            print(f"⚠️ Erreur initialisation pyttsx3: {e}")
        
        # Initialisation Coqui TTS
        if self.tts_config.get("coqui_enabled", False):
            try:
                from TTS.api import TTS
                self.coqui_tts = TTS
                print("✅ Coqui TTS disponible")
            except ImportError:
                print("⚠️ Coqui TTS non disponible")
    
    def _configure_pyttsx3(self):
        """Configure le moteur pyttsx3"""
        if not self.pyttsx3_engine:
            return
        
        try:
            # Volume
            volume = self.tts_config.get("volume", 0.8)
            self.pyttsx3_engine.setProperty('volume', volume)
            
            # Vitesse
            speed = self.tts_config.get("speed", 1.0)
            rate = self.pyttsx3_engine.getProperty('rate')
            self.pyttsx3_engine.setProperty('rate', int(rate * speed))
            
            # Voix (essayer de trouver une voix française)
            voices = self.pyttsx3_engine.getProperty('voices')
            french_voice = None
            
            for voice in voices:
                if 'fr' in voice.id.lower() or 'french' in voice.name.lower():
                    french_voice = voice
                    break
            
            if french_voice:
                self.pyttsx3_engine.setProperty('voice', french_voice.id)
                print(f"🎯 Voix française sélectionnée: {french_voice.name}")
            else:
                print("⚠️ Aucune voix française trouvée, utilisation voix par défaut")
        
        except Exception as e:
            print(f"⚠️ Erreur configuration pyttsx3: {e}")
    
    def speak(self, text, save_to_file=False):
        """
        Synthétise et lit le texte
        
        Args:
            text (str): Texte à synthétiser
            save_to_file (bool): Sauvegarder en fichier audio
        
        Returns:
            bool: True si succès, False sinon
        """
        if not text or not text.strip():
            print("⚠️ Texte vide, synthèse ignorée")
            return False
        
        print(f"🗣️ Synthèse: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # Sélection du moteur selon la configuration
        if self.voice_engine == "edge_tts" and self.edge_tts:
            return self._speak_edge_tts(text, save_to_file)
        elif self.voice_engine == "coqui" and self.coqui_tts and self.tts_config.get("coqui_enabled"):
            return self._speak_coqui_tts(text, save_to_file)
        elif self.voice_engine == "xtts" and self.coqui_tts and self.tts_config.get("xtts_enabled"):
            return self._speak_xtts(text, save_to_file)
        elif self.pyttsx3_engine:
            return self._speak_pyttsx3(text)
        else:
            print("❌ Aucun moteur TTS disponible")
            return False
    
    def _speak_edge_tts(self, text, save_to_file=False):
        """Synthèse avec Edge TTS"""
        try:
            voice = self.tts_config.get("edge_voice", "fr-FR-HenriNeural")
            
            # Génération du fichier audio
            output_file = self.output_dir / f"edge_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            # Utilisation d'asyncio pour Edge TTS
            async def generate_speech():
                communicate = self.edge_tts.Communicate(text, voice)
                await communicate.save(str(output_file))
            
            # Exécution asynchrone
            if platform.system() == "Windows":
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(generate_speech())
            loop.close()
            
            # Lecture du fichier généré
            self._play_audio_file(output_file)
            
            # Suppression du fichier temporaire si pas de sauvegarde
            if not save_to_file:
                try:
                    os.remove(output_file)
                except:
                    pass
            else:
                print(f"💾 Audio sauvegardé: {output_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur Edge TTS: {e}")
            return self._fallback_speak(text)
    
    def _speak_pyttsx3(self, text):
        """Synthèse avec pyttsx3"""
        try:
            self.pyttsx3_engine.say(text)
            self.pyttsx3_engine.runAndWait()
            return True
        except Exception as e:
            print(f"❌ Erreur pyttsx3: {e}")
            return False
    
    def _speak_coqui_tts(self, text, save_to_file=False):
        """Synthèse avec Coqui TTS (modèle multilingue)"""
        try:
            # Utilisation du modèle français de Coqui
            model_name = "tts_models/fr/mai/tacotron2-DDC"
            
            tts = self.coqui_tts(model_name)
            output_file = self.output_dir / f"coqui_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            # Génération audio
            tts.tts_to_file(text=text, file_path=str(output_file))
            
            # Lecture
            self._play_audio_file(output_file)
            
            # Gestion sauvegarde
            if not save_to_file:
                try:
                    os.remove(output_file)
                except:
                    pass
            else:
                print(f"💾 Audio sauvegardé: {output_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur Coqui TTS: {e}")
            return self._fallback_speak(text)
    
    def _speak_xtts(self, text, save_to_file=False):
        """Synthèse avec XTTS (clonage vocal)"""
        try:
            # Chemin vers l'échantillon vocal
            speaker_wav = Path("data/voice_samples/male_sample.wav")
            
            if not speaker_wav.exists():
                print("⚠️ Échantillon vocal introuvable, utilisation Coqui standard")
                return self._speak_coqui_tts(text, save_to_file)
            
            # Modèle XTTS
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            tts = self.coqui_tts(model_name)
            
            output_file = self.output_dir / f"xtts_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            # Génération avec clonage vocal
            tts.tts_to_file(
                text=text,
                file_path=str(output_file),
                speaker_wav=str(speaker_wav),
                language="fr"
            )
            
            # Lecture
            self._play_audio_file(output_file)
            
            # Gestion sauvegarde
            if not save_to_file:
                try:
                    os.remove(output_file)
                except:
                    pass
            else:
                print(f"💾 Audio sauvegardé: {output_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur XTTS: {e}")
            return self._fallback_speak(text)
    
    def _play_audio_file(self, file_path):
        """Lit un fichier audio selon l'OS"""
        try:
            system = platform.system()
            
            if system == "Windows":
                os.startfile(str(file_path))
            elif system == "Darwin":  # macOS
                subprocess.run(["afplay", str(file_path)], check=True)
            else:  # Linux
                # Essayer plusieurs lecteurs audio
                players = ["aplay", "paplay", "ffplay", "mpg123"]
                for player in players:
                    try:
                        subprocess.run([player, str(file_path)], 
                                     check=True, stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    print("⚠️ Aucun lecteur audio trouvé sur Linux")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lecture audio: {e}")
            return False
    
    def _fallback_speak(self, text):
        """Méthode de secours si le moteur principal échoue"""
        if self.pyttsx3_engine and self.voice_engine != "pyttsx3":
            print("🔄 Basculement vers pyttsx3...")
            return self._speak_pyttsx3(text)
        else:
            print("❌ Tous les moteurs TTS ont échoué")
            print(f"📝 Texte non lu: {text}")
            return False
    
    def set_voice_engine(self, engine):
        """Change le moteur TTS à la volée"""
        valid_engines = ["edge_tts", "pyttsx3", "coqui", "xtts"]
        
        if engine not in valid_engines:
            print(f"❌ Moteur invalide. Choix: {valid_engines}")
            return False
        
        self.voice_engine = engine
        print(f"🔄 Moteur TTS changé: {engine}")
        return True
    
    def test_voice(self, text="Bonjour, ceci est un test de synthèse vocale avec WillIAM."):
        """Test du moteur TTS actuel"""
        print(f"🧪 Test du moteur {self.voice_engine}...")
        success = self.speak(text)
        
        if success:
            print("✅ Test réussi")
        else:
            print("❌ Test échoué")
        
        return success
    
    def list_available_engines(self):
        """Liste les moteurs TTS disponibles"""
        engines = []
        
        if self.edge_tts:
            engines.append("edge_tts")
        if self.pyttsx3_engine:
            engines.append("pyttsx3")
        if self.coqui_tts and self.tts_config.get("coqui_enabled"):
            engines.append("coqui")
        if self.coqui_tts and self.tts_config.get("xtts_enabled"):
            engines.append("xtts")
        
        return engines
    
    def get_status(self):
        """Retourne le statut du moteur TTS"""
        return {
            "current_engine": self.voice_engine,
            "available_engines": self.list_available_engines(),
            "edge_tts_available": self.edge_tts is not None,
            "pyttsx3_available": self.pyttsx3_engine is not None,
            "coqui_available": self.coqui_tts is not None,
            "xtts_enabled": self.tts_config.get("xtts_enabled", False),
            "config": self.tts_config
        }


# Fonction utilitaire pour utilisation rapide
def quick_speak(text, engine="edge_tts"):
    """Fonction rapide pour synthèse vocale"""
    voice = VoiceEngine()
    voice.set_voice_engine(engine)
    return voice.speak(text)


# Test du module si exécuté directement
if __name__ == "__main__":
    print("🧪 Test du module TTS...")
    
    # Création d'une instance
    tts = VoiceEngine()
    
    # Affichage du statut
    status = tts.get_status()
    print(f"📊 Statut TTS:")
    print(f"   Moteur actuel: {status['current_engine']}")
    print(f"   Moteurs disponibles: {status['available_engines']}")
    
    # Test de chaque moteur disponible
    for engine in status['available_engines']:
        print(f"\n🔧 Test du moteur: {engine}")
        tts.set_voice_engine(engine)
        success = tts.test_voice(f"Test du moteur {engine}")
        if not success:
            print(f"❌ Échec du test pour {engine}")
    
    print("\n✅ Tests terminés")
