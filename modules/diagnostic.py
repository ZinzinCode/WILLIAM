# diagnostic.py
import importlib
import sys

def check_module(module_name):
    """Vérifie si un module est disponible"""
    try:
        importlib.import_module(module_name)
        return {"status": "OK", "message": "Disponible"}
    except ImportError as e:
        return {"status": "ERROR", "message": f"Non disponible: {str(e)}"}
    except Exception as e:
        return {"status": "WARNING", "message": f"Erreur: {str(e)}"}

def run_diagnostic():
    """Lance le diagnostic complet du système"""
    print("🔍 Diagnostic de l'environnement...")
    
    # Modules à vérifier
    modules_to_check = {
        "speech_recognition": "Reconnaissance vocale",
        "pyttsx3": "Synthèse vocale", 
        "torch": "PyTorch",
        "transformers": "Transformers",
        "pyaudio": "Audio",
        "openai": "OpenAI",
        "requests": "Requêtes HTTP",
        "json": "JSON",
        "datetime": "Date/Heure",
        "threading": "Threading",
        "queue": "Queue",
        "time": "Time"
    }
    
    # Modules optionnels
    optional_modules = {
        "whisper": "Whisper STT",
        "llama_cpp": "Llama CPP",
        "wcm": "WCM"
    }
    
    results = {}
    errors = {}
    
    # Vérification des modules essentiels
    for module, description in modules_to_check.items():
        result = check_module(module)
        results[module] = result
        
        if result["status"] == "OK":
            print(f"✅ {module:<20} {result['message']}")
        else:
            print(f"❌ {module:<20} {result['message']}")
            errors[module] = result
    
    # Vérification des modules optionnels
    for module, description in optional_modules.items():
        result = check_module(module)
        results[module] = result
        
        if result["status"] == "OK":
            print(f"✅ {module:<20} {result['message']}")
        else:
            print(f"⚠️ {module:<20} {result['message']}")
    
    # Résumé
    if not errors:
        print("✅ Tous les modules nécessaires sont présents !")
    else:
        print(f"❌ {len(errors)} module(s) critique(s) manquant(s)")
    
    return results

if __name__ == "__main__":
    run_diagnostic()
