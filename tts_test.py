from TTS.api import TTS
from TTS.utils.manage import ModelManager

manager = ModelManager()
models = manager.list_models()

print("Modèles français disponibles :")
for m in models:
    if "/fr/" in m or "fr_" in m or m.startswith("tts_models/fr"):
        print(m)

# Choisis un modèle français masculin
model_name = "tts_models/fr/mai/tacotron2-DDC"  # Voix masculine

tts = TTS(model_name)

# Affiche les speakers si le modèle en propose plusieurs
if tts.speakers:
    print("Voix disponibles :", tts.speakers)
    speaker = tts.speakers[0]  # ajuste si besoin
else:
    speaker = None

text = "Bonjour, ceci est une voix masculine française générée localement avec Coqui TTS."

tts.tts_to_file(
    text=text,
    speaker=speaker,
    file_path="output.wav"
)

print("Synthèse terminée ! Fichier : output.wav")