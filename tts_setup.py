#!/usr/bin/env python3
"""
Script de configuration et diagnostic TTS pour William
Résout les problèmes de lenteur et d'absence de voix Coqui
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            return True
        else:
            print(f"❌ {description} - Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️ Python 3.8+ recommandé pour TTS")
        return False
    return True

def install_dependencies():
    """Installation des dépendances TTS optimisées"""
    
    dependencies = [
        # TTS principal
        ("TTS", "Coqui TTS pour synthèse vocale avancée"),
        
        # Audio
        ("pygame", "Lecture audio optimisée"),
        ("pyttsx3", "Synthèse vocale de fallback"),
        ("soundfile", "Traitement fichiers audio"),
        
        # IA/ML
        ("torch", "PyTorch pour les modèles IA"),
        ("torchaudio", "Audio avec PyTorch"),
        
        # Utilitaires
        ("numpy", "Calculs numériques"),
        ("librosa", "Analyse audio avancée"),
    ]
    
    print("📦 Installation des dépendances TTS...")
    
    for package, description in dependencies:
        print(f"\n📦 Installation de {package} ({description})")
        
        # Commande d'installation adaptée
        if package == "torch":
            # Installation PyTorch avec support CUDA si disponible
            if platform.system() == "Windows":
                cmd = "pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118"
            else:
                cmd = "pip install torch torchaudio"
        else:
            cmd = f"pip install {package}"
        
        run_command(cmd, f"Installation {package}")

def setup_coqui_tts():
    """Configuration spécifique de Coqui TTS"""
    print("\n🎤 Configuration de Coqui TTS...")
    
    # Vérification de l'installation
    try:
        from TTS.api import TTS
        print("✅ Coqui TTS installé")
        
        # Test de chargement du modèle XTTS
        print("🔄 Test du modèle XTTS...")
        try:
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            print("✅ Modèle XTTS chargé avec succès")
            
            # Test de synthèse rapide
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
                tts.tts_to_file("Test", file_path=f.name, language="fr")
                print("✅ Test de synthèse réussi")
                
        except Exception as e:
            print(f"❌ Erreur modèle XTTS: {e}")
            print("💡 Le modèle sera téléchargé au premier usage")
            
    except ImportError:
        print("❌ Coqui TTS non installé")
        print("💡 Lancez: pip install TTS")

def optimize_system():
    """Optimisations système pour TTS"""
    print("\n⚡ Optimisations système...")
    
    # Création du dossier de cache TTS
    cache_dir = Path.home() / ".cache" / "tts"
    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Cache TTS: {cache_dir}")
    
    # Variables d'environnement pour optimiser les performances
    optimizations = {
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:128",
        "TTS_CACHE_PATH": str(cache_dir),
        "PYTHONUNBUFFERED": "1"
    }
    
    for var, value in optimizations.items():
        os.environ[var] = value
        print(f"✅ {var}={value}")

def create_voice_samples():
    """Crée des échantillons de voix pour le clonage"""
    samples_dir = Path("voice_samples")
    samples_dir.mkdir(exist_ok=True)
    
    print(f"\n🎵 Dossier échantillons vocaux: {samples_dir}")
    print("💡 Placez vos fichiers WAV de référence (5-10 secondes) dans ce dossier")
    print("   pour améliorer la qualité de clonage vocal XTTS")

def diagnose_audio_system():
    """Diagnostic du système audio"""
    print("\n🔊 Diagnostic système audio...")
    
    # Test pygame
    try:
        import pygame
        pygame.mixer.init()
        print("✅ Pygame audio fonctionnel")
        pygame.mixer.quit()
    except Exception as e:
        print(f"❌ Pygame audio: {e}")
    
    # Test pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"✅ pyttsx3: {len(voices)} voix disponibles")
        
        # Affichage des voix françaises
        french_voices = []
        for voice in voices:
            if any(keyword in voice.name.lower() for keyword in ['hortense', 'marie', 'fr', 'french']):
                french_voices.append(voice.name)
        
        if french_voices:
            print(f"🇫🇷 Voix françaises: {', '.join(french_voices)}")
        else:
            print("⚠️ Aucune voix française détectée")
            
    except Exception as e:
        print(f"❌ pyttsx3: {e}")

def create_improved_config():
    """Crée un fichier de configuration TTS optimisé"""
    config_content = '''# Configuration TTS optimisée pour William
TTS_CONFIG = {
    "preferred_engine": "xtts",  # xtts, pyttsx3
    "language": "fr",
    "speed": 1.0,
    "volume": 0.9,
    "voice_cloning": True,
    "cache_enabled": True,
    "async_processing": True,
    "quality": "high",  # high, medium, fast
    
    # Paramètres XTTS
    "xtts": {
        "model": "tts_models/multilingual/multi-dataset/xtts_v2",
        "gpu": True,
        "split_sentences": True,
        "temperature": 0.7,
    },
    
    # Paramètres pyttsx3 (fallback)
    "pyttsx3": {
        "rate": 180,
        "volume": 0.9,
        "voice_preference": ["hortense", "marie", "french", "fr"]
    }
}
'''
    
    config_file = Path("tts_config.py")
    config_file.write_text(config_content, encoding="utf-8")
    print(f"✅ Configuration créée: {config_file}")

def main():
    """Script principal de configuration"""
    print("🤖 Configuration TTS pour William")
    print("=" * 50)
    
    # Vérifications système
    if not check_python_version():
        return
    
    # Installation des dépendances
    install_dependencies()
    
    # Configuration spécifique
    setup_coqui_tts()
    optimize_system()
    create_voice_samples()
    
    # Diagnostic
    diagnose_audio_system()
    
    # Configuration
    create_improved_config()
    
    print("\n🎉 Configuration TTS terminée!")
    print("\n📋 Étapes suivantes:")
    print("1. Testez avec: python -c 'from tts_improved import test_tts; test_tts()'")
    print("2. Placez vos échantillons vocaux dans voice_samples/")
    print("3. Utilisez speak() dans votre code principal")
    
    print("\n💡 Conseils pour améliorer les performances:")
    print("- Utilisez un GPU NVIDIA pour XTTS (plus rapide)")
    print("- Enregistrez des échantillons vocaux de 5-10 secondes")
    print("- Activez le cache pour éviter les rechargements")

if __name__ == "__main__":
    main()
