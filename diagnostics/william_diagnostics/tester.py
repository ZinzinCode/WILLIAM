import os

def whisper_test():
    """Test du module de transcription"""
    try:
        from modules.stt import transcribe_audio
        if not os.path.exists("test.wav"):
            raise FileNotFoundError("Fichier test.wav manquant")
        result = transcribe_audio("test.wav")
        assert result is not None
        return True
    except ImportError:
        return True  # Module STT optionnel/mock
    except Exception as e:
        raise e

def tts_test():
    """Test du module text-to-speech"""
    try:
        from modules.tts import speak
        speak("Test", test_mode=True)  # Mode test silencieux
        return True
    except ImportError:
        return True  # Module TTS optionnel
    except Exception as e:
        raise e

def llm_test():
    """Test du module LLM"""
    try:
        from modules.llm import query_llm
        response = query_llm("Test", max_tokens=10)
        assert len(str(response)) > 0
        return True
    except ImportError:
        return True  # Module LLM optionnel
    except Exception as e:
        raise e

def wcm_test():
    """Test du gestionnaire de contexte"""
    try:
        from modules.wcm import WilliamContextManager
        wcm = WilliamContextManager()
        wcm.update_history("test", "test response")
        return True
    except Exception as e:
        raise AssertionError(f"Gestionnaire de contexte défaillant: {e}")

def file_system_test():
    """Test de l'accès au système de fichiers"""
    test_dirs = ["data", "data/context", "william_diagnostics/logs"]
    for directory in test_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    # Test d'écriture
    test_file = "data/test_write.tmp"
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return True
    except Exception:
        raise PermissionError("Impossible d'écrire dans le dossier data")

modules = {
    "whisper": whisper_test,
    "tts": tts_test, 
    "llm": llm_test,
    "wcm": wcm_test,
    "filesystem": file_system_test,
}