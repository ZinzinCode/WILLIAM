from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
tts.tts_to_file(
    text="Bonjour, ceci est une voix synthétique basée sur un échantillon masculin français.",
    file_path="output.wav",
    speaker_wav="male_sample.wav",
    language="fr"
)