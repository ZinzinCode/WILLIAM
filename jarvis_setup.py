#!/usr/bin/env python3
"""
Script d'installation pour l'Assistant Jarvis
Installe automatiquement toutes les dépendances nécessaires
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Exécute une commande avec gestion d'erreur"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} - Succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur: {e}")
        if e.stdout:
            print(f"   Sortie: {e.stdout}")
        if e.stderr:
            print(f"   Erreur: {e.stderr}")
        return False

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ requis")
        return False
    
    print("✅ Version Python compatible")
    return True

def install_basic_packages():
    """Installe les packages de base"""
    packages = [
        "SpeechRecognition",
        "pyttsx3", 
        "watchdog"
    ]
    
    for package in packages:
        success = run_command(
            f"{sys.executable} -m pip install {package}",
            f"Installation de {package}"
        )
        if not success:
            print(f"⚠️ Échec d'installation de {package}")
            return False
    
    return True

def install_pyaudio():
    """Installe PyAudio avec gestion spéciale selon l'OS"""
    system = platform.system().lower()
    
    print(f"🔊 Installation de PyAudio sur {system}...")
    
    if system == "windows":
        # Windows - essayer d'abord pip, puis suggérer wheel
        success = run_command(
            f"{sys.executable} -m pip install pyaudio",
            "Installation PyAudio (Windows)"
        )
        
        if not success:
            print("⚠️ Échec d'installation standard de PyAudio")
            print("💡 Solutions pour Windows:")
            print("   1. Téléchargez le fichier .whl depuis:")
            print("      https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
            print("   2. Installez avec: pip install nom_du_fichier.whl")
            print("   3. Ou utilisez: pip install pipwin && pipwin install pyaudio")
            return False
            
    elif system == "darwin":  # macOS
        # macOS - installer portaudio d'abord si Homebrew disponible
        print("🍺 Tentative d'installation avec Homebrew...")
        homebrew_success = run_command(
            "brew install portaudio",
            "Installation PortAudio (macOS)"
        )
        
        success = run_command(
            f"{sys.executable} -m pip install pyaudio",
            "Installation PyAudio (macOS)"
        )
        
        if not success:
            print("💡 Solutions pour macOS:")
            print("   1. Installez Homebrew: https://brew.sh")
            print("   2. Puis: brew install portaudio")
            print("   3. Enfin: pip install pyaudio")
            return False
            
    else:  # Linux
        print("🐧 Installation sur Linux...")
        
        # Essayer d'installer les dépendances système
        distro_commands = [
            "sudo apt-get install -y python3-pyaudio portaudio19-dev",  # Ubuntu/Debian
            "sudo yum install -y python3-pyaudio portaudio-devel",       # CentOS/RHEL
            "sudo pacman -S python-pyaudio portaudio"                    # Arch
        ]
        
        system_dep_installed = False
        for cmd in distro_commands:
            if run_command(cmd, "Installation dépendances système"):
                system_dep_installed = True
                break
        
        success = run_command(
            f"{sys.executable} -m pip install pyaudio",
            "Installation PyAudio (Linux)"
        )
        
        if not success:
            print("💡 Solutions pour Linux:")
            print("   Ubuntu/Debian: sudo apt-get install python3-pyaudio portaudio19-dev")
            print("   CentOS/RHEL: sudo yum install python3-pyaudio portaudio-devel")
            print("   Arch: sudo pacman -S python-pyaudio portaudio")
            return False
    
    return True

def create_directories():
    """Crée les dossiers nécessaires"""
    directories = [
        "modules",
        "data", 
        "data/user_projects"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Dossier créé/vérifié: {directory}")
        except Exception as e:
            print(f"❌ Erreur création dossier {directory}: {e}")
            return False
    
    return True

def create_init_files():
    """Crée les fichiers __init__.py pour les modules"""
    init_files = [
        "modules/__init__.py"
    ]
    
    for init_file in init_files:
        try:
            with open(init_file, 'w') as f:
                f.write('"""Module Jarvis Assistant"""\n')
            print(f"📄 Fichier créé: {init_file}")
        except Exception as e:
            print(f"❌ Erreur création {init_file}: {e}")
            return False
    
    return True

def test_installation():
    """Test rapide de l'installation"""
    print("\n🧪 Test de l'installation...")
    
    try:
        # Test imports
        import speech_recognition as sr
        import pyttsx3
        import watchdog
        print("✅ Tous les modules s'importent correctement")
        
        # Test micro
        print("🎙️ Test microphone...")
        recognizer = sr.Recognizer()
        mics = sr.Microphone.list_microphone_names()
        print(f"✅ {len(mics)} microphone(s) détecté(s)")
        
        # Test synthèse vocale
        print("🗣️ Test synthèse vocale...")
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        print("✅ Synthèse vocale initialisée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale d'installation"""
    print("=" * 60)
    print("🤖 INSTALLATION DE L'ASSISTANT JARVIS")
    print("=" * 60)
    
    # Vérifications préliminaires
    if not check_python_version():
        return False
    
    print("\n📦 Création des dossiers...")
    if not create_directories():
        return False
    
    if not create_init_files():
        return False
    
    print("\n📦 Installation des dépendances...")
    if not install_basic_packages():
        return False
    
    print("\n🔊 Installation PyAudio...")
    audio_success = install_pyaudio()
    
    print("\n🧪 Test de l'installation...")
    test_success = test_installation()
    
    print("\n" + "=" * 60)
    if test_success:
        print("🎉 INSTALLATION TERMINÉE AVEC SUCCÈS!")
        print("🚀 Vous pouvez maintenant lancer Jarvis avec: python main.py")
    else:
        print("⚠️ Installation terminée avec des avertissements")
        if not audio_success:
            print("   - Fonctions audio limitées (PyAudio)")
        print("🚀 Vous pouvez essayer de lancer Jarvis avec: python main.py")
    
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Installation interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("💡 Veuillez installer manuellement avec:")
        print("   pip install SpeechRecognition pyttsx3 pyaudio watchdog")