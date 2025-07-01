import time
import random
import os
import requests
import speech_recognition as sr
import tempfile

# --- COQUI XTTS ---
from TTS.api import TTS
from playsound import playsound

# Spécifiez ici le chemin de votre échantillon .wav pour la voix personnalisée
SPEAKER_WAV = "male_sample.wav"  # Changez par votre propre fichier si besoin

# Précharge le modèle XTTS
tts_engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

def safe_remove(filename):
    for _ in range(10):
        try:
            if os.path.exists(filename):
                os.remove(filename)
            break
        except PermissionError:
            time.sleep(0.2)

def speak(text):
    print(f"WillIAm 🗣️ : {text}")
    print("Synthèse en cours...")
    # Utilisation d'un fichier temporaire pour éviter les soucis de permission
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        temp_path = tmp.name
    try:
        tts_engine.tts_to_file(
            text=text,
            file_path=temp_path,
            speaker_wav=SPEAKER_WAV,
            language="fr"
        )
    except Exception as e:
        print(f"Erreur XTTS : {e}")
        tts_engine.tts_to_file(
            text=text,
            file_path=temp_path,
            language="fr"
        )
    # Attendre que le fichier soit bien écrit
    for _ in range(20):  # max 2 secondes
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1024:
            break
        time.sleep(0.1)
    print("Lecture du fichier audio...")
    try:
        playsound(temp_path)
    except Exception as e:
        print(f"Erreur playsound : {e}")
    print("Lecture terminée.")
    safe_remove(temp_path)

def listen(timeout=8):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.pause_threshold = 0.8
        recognizer.energy_threshold = 300
        try:
            print("🎙️ Parle, j'écoute...")
            audio = recognizer.listen(source, timeout=timeout)
            query = recognizer.recognize_google(audio, language="fr-FR")
            print(f"🧠 Tu as dit : {query}")
            return query
        except sr.WaitTimeoutError:
            print("⌛ Aucun son détecté.")
            speak("Je n'ai rien entendu, peux-tu répéter ?")
            return ""
        except sr.UnknownValueError:
            print("🤔 Je n'ai pas compris.")
            speak("Je n'ai pas compris, peux-tu répéter ?")
            return ""
        except sr.RequestError:
            print("❌ Problème de reconnaissance.")
            speak("Il y a un problème de connexion avec la reconnaissance vocale.")
            return ""

def wait_for_wake_word(wake_words=None):
    if wake_words is None:
        wake_words = ["william", "bonjour william", "salut william"]
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.pause_threshold = 0.8
        recognizer.energy_threshold = 300
        while True:
            print(f"🎧 En attente du mot d'activation : {', '.join(wake_words)} ...")
            try:
                audio = recognizer.listen(source, timeout=8)
                query = recognizer.recognize_google(audio, language="fr-FR")
                print(f"🧠 (détection) : {query}")
                for word in wake_words:
                    if word.lower() in query.lower():
                        speak("Oui, je t'écoute !")
                        return
            except Exception:
                continue

def listen_until_sleep_word(sleep_words=None):
    if sleep_words is None:
        sleep_words = ["merci william", "au revoir", "stop", "bonne nuit", "dors william"]
    while True:
        phrase = listen()
        print("Phrase reconnue pour traitement :", repr(phrase))
        if not phrase:
            speak("Je n'ai pas compris, peux-tu répéter ?")
            continue
        if any(word in phrase.lower() for word in sleep_words):
            speak("Très bien, je retourne en veille.")
            break
        yield phrase

def assistant_response(prompt, history=None, model="llama3"):
    """
    Génère une réponse depuis Ollama (LLM local) avec gestion de l'historique.
    """
    messages = history[:] if history else []
    messages.append({"role": "user", "content": prompt})
    try:
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages},
            timeout=90
        )
        response = r.json()
        if "message" in response and "content" in response["message"]:
            return response["message"]["content"].strip()
        return "[Aucune réponse générée par l'IA]"
    except Exception as e:
        print("Erreur Ollama:", e)
        return "Je rencontre un problème pour réfléchir, désolé."

if __name__ == "__main__":
    speak("Bonjour, je suis WillIAm avec une voix masculine personnalisée et une intelligence augmentée grâce à l'IA Llama3 sur Ollama !")
    history = []
    while True:
        wait_for_wake_word()
        for phrase in listen_until_sleep_word():
            print("Phrase reçue :", phrase)
            rep = assistant_response(phrase, history)
            history.append({"role": "user", "content": phrase})
            history.append({"role": "assistant", "content": rep})
            speak(rep)