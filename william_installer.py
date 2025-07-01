#!/usr/bin/env python3
"""
Installateur amélioré pour WillIAM
Installation automatique avec gestion avancée des dépendances
"""

import subprocess
import sys
import os
import platform
import urllib.request
import json
from pathlib import Path

class WillIAMInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.python_version = sys.version_info
        self.errors = []
        self.warnings = []
        
    def print_header(self):
        """Affiche l'en-tête d'installation"""
        print("=" * 70)
        print("🤖 INSTALLATEUR WILLIAM - Assistant Vocal Intelligent")
        print("=" * 70)
        print(f"🐍 Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print(f"💻 Système: {platform.system()} {platform.release()}")
        print("=" * 70)
    
    def check_python_version(self):
        """Vérifie la version de Python"""
        print("🔍 Vérification de Python...")
        
        if self.python_version < (3, 8):
            self.errors.append("Python 3.8+ requis")
            return False
        
        print("✅ Version Python compatible")
        return True
    
    def run_command(self, command, description, required=True):
        """Exécute une commande avec gestion d'erreur"""
        print(f"🔧 {description}...")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True,
                capture_output=True, 
                text=True,
                timeout=300
            )
            print(f"✅ {description} - Succès")
            return True
            
        except subprocess.TimeoutExpired:
            error_msg = f"{description} - Timeout"
            print(f"❌ {error_msg}")
            if required:
                self.errors.append(error_msg)
            else:
                self.warnings.append(error_msg)
            return False
            
        except subprocess.CalledProcessError as e:
            error_msg = f"{description} - Erreur: {e}"
            print(f"❌ {error_msg}")
            if e.stderr:
                print(f"   Détails: {e.stderr.strip()}")
            
            if required:
                self.errors.append(error_msg)
            else:
                self.warnings.append(error_msg)
            return False
    
    def install_basic_packages(self):
        """Installe les packages Python de base"""
        print("\n📦 Installation des packages de base...")
        
        basic_packages = [
            "requests",
            "beautifulsoup4",
            "speechrecognition",
            "watchdog",
            "pillow",
            "scikit-learn"
        ]
        
        for package in basic_packages:
            success = self.run_command(
                f"{sys.executable} -m pip install {package}",
                f"Installation de {package}"
            )
            if not success:
                return False
        
        return True
    
    def install_tts_packages(self):
        """Installe les packages TTS"""
        print("\n🗣️ Installation des packages TTS...")
        
        # Edge TTS (requis)
        if not self.run_command(
            f"{sys.executable} -m pip install edge-tts",
            "Installation Edge TTS"
        ):
            return False
        
        # PyTTSx3 (requis)
        if not self.run_command(
            f"{sys.executable} -m pip install pyttsx3",
            "Installation pyttsx3"
        ):
            return False
        
        # PyAudio (requis mais peut échouer)
        self.install_pyaudio()
        
        # Coqui TTS (optionnel)
        print("\n🎯 Installation Coqui TTS (optionnel, peut prendre du temps)...")
        coqui_success = self.run_command(
            f"{sys.executable} -m pip install TTS",
            "Installation Coqui TTS",
            required=False
        )
        
        if coqui_success:
            print("✅ Coqui TTS installé - Synthèse vocale de haute qualité disponible")
        else:
            self.warnings.append("Coqui TTS non installé - Synthèse vocale limitée")
        
        # Pygame pour la lecture audio
        self.run_command(
            f"{sys.executable} -m pip install pygame",
            "Installation Pygame",
            required=False
        )
        
        return True
    
    def install_pyaudio(self):
        """Installation spécialisée de PyAudio"""
        print("🔊 Installation PyAudio...")
        
        if self.system == "windows":
            return self._install_pyaudio_windows()
        elif self.system == "darwin":
            return self._install_pyaudio_macos()
        else:
            return self._install_pyaudio_linux()
    
    def _install_pyaudio_windows(self):
        """Installation PyAudio sur Windows"""
        success = self.run_command(
            f"{sys.executable} -m pip install pyaudio",
            "Installation PyAudio (Windows)",
            required=False
        )
        
        if not success:
            print("💡 Solutions alternatives pour Windows:")
            print("   1. Téléchargez le .whl depuis: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
            print("   2. Ou essayez: pip install pipwin && pipwin install pyaudio")
            self.warnings.append("PyAudio installation échouée - fonctions vocales limitées")
        
        return success
    
    def _install_pyaudio_macos(self):
        """Installation PyAudio sur macOS"""
        # Essayer d'installer portaudio avec Homebrew
        self.run_command(
            "brew install portaudio",
            "Installation PortAudio (macOS)",
            required=False
        )
        
        success = self.run_command(
            f"{sys.executable} -m pip install pyaudio",
            "Installation PyAudio (macOS)",
            required=False
        )
        
        if not success:
            print("💡 Solutions pour macOS:")
            print("   1. Installez Homebrew: https://brew.sh")
            print("   2. Puis: brew install portaudio")
            print("   3. Enfin: pip install pyaudio")
            self.warnings.append("PyAudio installation échouée")
        
        return success
    
    def _install_pyaudio_linux(self):
        """Installation PyAudio sur Linux"""
        # Essayer d'installer les dépendances système
        distro_commands = [
            "sudo apt-get update && sudo apt-get install -y python3-pyaudio portaudio19-dev",
            "sudo yum install -y python3-pyaudio portaudio-devel",
            "sudo pacman -S python-pyaudio portaudio"
        ]
        
        for cmd in distro_commands:
            if self.run_command(cmd, "Installation dépendances système", required=False):
                break
        
        success = self.run_command(
            f"{sys.executable} -m pip install pyaudio",
            "Installation PyAudio (Linux)",
            required=False
        )
        
        if not success:
            print("💡 Solutions pour Linux:")
            print("   Ubuntu/Debian: sudo apt-get install python3-pyaudio portaudio19-dev")
            print("   CentOS/RHEL: sudo yum install python3-pyaudio portaudio-devel")
            print("   Arch: sudo pacman -S python-pyaudio portaudio")
            self.warnings.append("PyAudio installation échouée")
        
        return success
    
    def install_ollama(self):
        """Installation d'Ollama"""
        print("\n🧠 Installation d'Ollama (optionnel)...")
        
        if self.system == "windows":
            print("💡 Pour Windows, téléchargez Ollama depuis: https://ollama.ai/download")
            self.warnings.append("Installation manuelle d'Ollama requise sur Windows")
            return False
        
        # Linux/macOS
        success = self.run_command(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "Installation Ollama",
            required=False
        )
        
        if success:
            print("🤖 Téléchargement du modèle IA (peut prendre du temps)...")
            model_success = self.run_command(
                "ollama pull llama3.2:3b",
                "Téléchargement modèle Llama 3.2",
                required=False
            )
            
            if model_success:
                print("✅ IA avancée prête")
            else:
                self.warnings.append("Modèle IA non téléchargé - fonctionnalités limitées")
        else:
            self.warnings.append("Ollama non installé - IA basique uniquement")
        
        return success
    
    def create_directories(self):
        """Crée la structure de dossiers"""
        print("\n📁 Création de la structure...")
        
        directories = [
            "modules",
            "data",
            "data/logs",
            "data/user_projects",
            "data/voice_samples"
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                print(f"📂 {directory}")
            except Exception as e:
                self.errors.append(f"Impossible de créer {directory}: {e}")
                return False
        
        return True
    
    def create_init_files(self):
        """Crée les fichiers __init__.py"""
        print("📄 Création des fichiers modules...")
        
        init_files = ["modules/__init__.py"]
        
        for init_file in init_files:
            try:
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write('"""WillIAM Assistant Modules"""\n')
                print(f"✅ {init_file}")
            except Exception as e:
                self.errors.append(f"Impossible de créer {init_file}: {e}")
                return False
        
        return True
    
    def download_voice_sample(self):
        """Télécharge un échantillon vocal par défaut"""
        print("\n🎤 Configuration échantillon vocal...")
        
        sample_path = Path("data/voice_samples/male_sample.wav")
        
        if sample_path.exists():
            print("✅ Échantillon vocal déjà présent")
            return True
        
        print("💡 Pour utiliser XTTS, placez un échantillon vocal (male_sample.wav)")
        print(f"   dans le dossier: {sample_path.parent}")
        print("   Durée recommandée: 10-30 secondes de parole claire")
        
        # Créer un fichier readme
        readme_path = sample_path.parent / "README.txt"
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("""ÉCHANTILLONS VOCAUX POUR XTTS

Pour utiliser le clonage vocal avec XTTS:

1. Enregistrez un échantillon de voix masculine française
2. Nommez le fichier: male_sample.wav
3. Placez-le dans ce dossier
4. Durée: 10-30 secondes de parole claire
5. Format: WAV, 16-bit, 22050Hz recommandé

L'échantillon sera utilisé pour générer une voix similaire.
""")
            print(f"📋 Instructions créées: {readme_path}")
        except Exception as e:
            self.warnings.append(f"Impossible de créer les instructions: {e}")
        
        return True
    
    def create_config_file(self):
        """Crée le fichier de configuration"""
        print("\n⚙️ Création du fichier de configuration...")
        
        config = {
            "assistant": {
                "name": "WillIAM",
                "language": "fr",
                "voice_engine": "edge_tts",
                "wake_word": "hey william"
            },
            "tts": {
                "edge_voice": "fr-FR-HenriNeural",
                "coqui_enabled": False,
                "xtts_enabled": False,
                "volume": 0.8,
                "speed": 1.0
            },
            "stt": {
                "engine": "google",
                "timeout": 5,
                "phrase_timeout": 3
            },
            "ai": {
                "ollama_enabled": False,
                "model": "llama3.2:3b",
                "temperature": 0.7,
                "max_tokens": 500
            },
            "modules": {
                "weather_enabled": True,
                "news_enabled": True,
                "music_enabled": True,
                "automation_enabled": True
            }
        }
        
        config_path = Path("config.json")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuration créée: {config_path}")
        except Exception as e:
            self.errors.append(f"Impossible de créer la configuration: {e}")
            return False
        
        return True
    
    def create_main_script(self):
        """Crée le script principal de démarrage"""
        print("🚀 Création du script principal...")
        
        main_script = '''#!/usr/bin/env python3
"""
WillIAM - Assistant Vocal Intelligent
Script principal de démarrage
"""

import json
import sys
from pathlib import Path

def load_config():
    """Charge la configuration"""
    config_path = Path("config.json")
    if not config_path.exists():
        print("❌ Fichier config.json introuvable!")
        print("💡 Exécutez d'abord l'installateur: python install.py")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Fonction principale"""
    print("=" * 50)
    print("🤖 WillIAM - Assistant Vocal Intelligent")
    print("=" * 50)
    
    try:
        config = load_config()
        print(f"✅ Configuration chargée")
        print(f"🎯 Assistant: {config['assistant']['name']}")
        print(f"🗣️ Moteur TTS: {config['tts']['voice_engine']}")
        print("=" * 50)
        
        # TODO: Implémenter la logique principale de l'assistant
        print("🚧 Assistant en cours de développement...")
        print("💡 Les modules seront intégrés prochainement")
        
    except Exception as e:
        print(f"❌ Erreur de démarrage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        main_path = Path("main.py")
        try:
            with open(main_path, 'w', encoding='utf-8') as f:
                f.write(main_script)
            print(f"✅ Script principal créé: {main_path}")
        except Exception as e:
            self.errors.append(f"Impossible de créer le script principal: {e}")
            return False
        
        return True
    
    def create_requirements_file(self):
        """Crée le fichier requirements.txt"""
        print("📋 Création du fichier requirements.txt...")
        
        requirements = """# WillIAM Assistant Dependencies

# Core packages
requests>=2.28.0
beautifulsoup4>=4.11.0
speechrecognition>=3.10.0
watchdog>=2.2.0
pillow>=9.4.0
scikit-learn>=1.2.0

# TTS/STT packages
edge-tts>=6.1.0
pyttsx3>=2.90
pyaudio>=0.2.11

# Optional packages
TTS>=0.13.0
pygame>=2.1.0

# AI/ML packages (optional)
# torch>=1.13.0
# transformers>=4.21.0
"""
        
        req_path = Path("requirements.txt")
        try:
            with open(req_path, 'w', encoding='utf-8') as f:
                f.write(requirements)
            print(f"✅ Requirements créé: {req_path}")
        except Exception as e:
            self.warnings.append(f"Impossible de créer requirements.txt: {e}")
        
        return True
    
    def print_summary(self):
        """Affiche le résumé d'installation"""
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ D'INSTALLATION")
        print("=" * 70)
        
        if not self.errors:
            print("✅ Installation réussie!")
        else:
            print("❌ Installation avec erreurs:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("\n⚠️  Avertissements:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print("\n🚀 PROCHAINES ÉTAPES:")
        print("1. python main.py - Démarrer l'assistant")
        print("2. Placez vos échantillons vocaux dans data/voice_samples/")
        print("3. Modifiez config.json selon vos préférences")
        
        if "Ollama non installé" in str(self.warnings):
            print("4. Installez Ollama pour l'IA avancée: https://ollama.ai")
        
        print("\n📚 Documentation:")
        print("   • README.md - Guide d'utilisation")
        print("   • config.json - Configuration de l'assistant")
        print("   • data/voice_samples/README.txt - Instructions vocales")
        
        print("=" * 70)
    
    def run_installation(self):
        """Lance l'installation complète"""
        self.print_header()
        
        # Vérifications préliminaires
        if not self.check_python_version():
            print("❌ Installation impossible - Version Python incompatible")
            return False
        
        # Étapes d'installation
        steps = [
            (self.create_directories, "Création des dossiers"),
            (self.create_init_files, "Initialisation des modules"),
            (self.install_basic_packages, "Installation packages de base"),
            (self.install_tts_packages, "Installation packages TTS/STT"),
            (self.install_ollama, "Installation Ollama (optionnel)"),
            (self.download_voice_sample, "Configuration échantillons vocaux"),
            (self.create_config_file, "Création de la configuration"),
            (self.create_main_script, "Création du script principal"),
            (self.create_requirements_file, "Création requirements.txt")
        ]
        
        for step_func, step_name in steps:
            try:
                success = step_func()
                if not success and step_name in ["Installation packages de base"]:
                    print(f"❌ Étape critique échouée: {step_name}")
                    break
            except Exception as e:
                error_msg = f"Erreur dans {step_name}: {e}"
                print(f"❌ {error_msg}")
                self.errors.append(error_msg)
        
        # Résumé final
        self.print_summary()
        
        return len(self.errors) == 0


def main():
    """Point d'entrée principal"""
    installer = WillIAMInstaller()
    
    try:
        success = installer.run_installation()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation interrompue par l'utilisateur")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()