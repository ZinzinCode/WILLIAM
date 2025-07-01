import subprocess
import os

def try_fix(module, error):
    """Tentatives de réparation automatique"""
    try:
        # Fichier de test manquant (ex : test.wav)
        if isinstance(error, FileNotFoundError):
            if "test.wav" in str(error):
                with open("test.wav", "wb") as f:
                    # Créer un fichier WAV minimal valide
                    f.write(b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
                return True

        # Module Python manquant → pip install
        elif "ModuleNotFoundError" in str(error) or isinstance(error, ModuleNotFoundError):
            if "'" in str(error):
                mod = str(error).split("'")[1]
                print(f"Tentative d'installation du module: {mod}")
                result = subprocess.run([os.sys.executable, "-m", "pip", "install", mod], capture_output=True)
                return result.returncode == 0

        # Permissions/dossier manquant
        elif isinstance(error, PermissionError):
            if "data" in str(error):
                os.makedirs("data", exist_ok=True)
                os.makedirs("data/context", exist_ok=True)
                return True

    except Exception as fix_error:
        print(f"Erreur lors de la réparation: {fix_error}")

    return False