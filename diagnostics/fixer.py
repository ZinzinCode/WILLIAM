import subprocess

def try_fix(module, error):
    if isinstance(error, FileNotFoundError):
        # Créer un fichier vide temporaire (par ex. test.wav)
        with open("test.wav", "wb") as f:
            f.write(b"")
    elif "ModuleNotFoundError" in str(error):
        mod = str(error).split("'")[1]
        subprocess.call(["pip", "install", mod])
