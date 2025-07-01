import threading
from tts_config import speak  # Adapte selon ton organisation de fichiers

def analyse_rapide(text):
    """
    Analyse instantanée sans regex ni boucle lourde.
    Adapte ici ta logique d'extraction/traitement clé.
    """
    infos = text.lower().split()  # Découpage simple et rapide
    print(f"🧠 Analyse : {infos}")
    # Décommente pour activer le TTS non bloquant :
    # threading.Thread(target=speak, args=(" ".join(infos),), daemon=True).start()
    # Place ici d'autres traitements légers si besoin

def main():
    print("🤖 William est prêt ! Tapez 'quit' pour quitter.")
    while True:
        try:
            user_input = input("🎙️ Vous avez dit : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFermeture de l'assistant.")
            break
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("À bientôt !")
            break
        # Traitement immédiat en thread pour ne jamais bloquer la saisie
        threading.Thread(target=analyse_rapide, args=(user_input,), daemon=True).start()
        # L'utilisateur peut saisir la commande suivante sans attendre la fin du traitement

if __name__ == "__main__":
    main()