"""
Module Assistant Jarvis
Un assistant IA local avec fonctions vocales et surveillance de fichiers
"""

__version__ = "1.0.0"
__author__ = "Assistant Jarvis Team"
__description__ = "Assistant IA local gratuit avec fonctions vocales"

# Imports principaux du module
try:
    from . import assistant
    from . import logger  
    from . import observer
    from . import voice_assistant
    
    print(f"🤖 Module Jarvis v{__version__} chargé avec succès")
    
except ImportError as e:
    print(f"⚠️ Erreur d'importation du module Jarvis: {e}")
    print("💡 Vérifiez que tous les fichiers sont présents dans le dossier modules/")

# Configuration globale
JARVIS_CONFIG = {
    "version": __version__,
    "voice_enabled": True,
    "file_observer_enabled": True,
    "log_level": "INFO",
    "default_mode": "voice"  # "voice" ou "text"
}

def get_version():
    """Retourne la version de Jarvis"""
    return __version__

def get_config():
    """Retourne la configuration globale"""
    return JARVIS_CONFIG.copy()

def set_config(key, value):
    """Modifie un paramètre de configuration"""
    if key in JARVIS_CONFIG:
        JARVIS_CONFIG[key] = value
        logger.log_system_event("CONFIG", f"Paramètre {key} modifié: {value}")
        return True
    return False