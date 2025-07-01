# 🤖 Assistant IA Local "Jarvis"

Un assistant vocal intelligent et gratuit qui fonctionne entièrement en local sur votre machine.

## 🎯 Fonctionnalités

- **🗣️ Assistant vocal** : Parlez avec Jarvis et recevez des réponses vocales
- **💬 Mode texte** : Interaction par chat textuel
- **📁 Surveillance de fichiers** : Jarvis observe vos projets et vous alerte des changements
- **📝 Historique** : Toutes les conversations sont enregistrées localement
- **🔒 100% Local** : Aucune donnée envoyée vers des serveurs externes (sauf reconnaissance vocale Google)

## 📋 Prérequis

- **Python 3.7+** (recommandé: Python 3.8+)
- **Microphone** (pour les fonctions vocales)
- **Haut-parleurs** (pour les réponses vocales)
- **Connexion Internet** (pour la reconnaissance vocale)

## 🚀 Installation Rapide

### Option 1: Installation Automatique (Recommandée)

```bash
# 1. Téléchargez tous les fichiers dans un dossier
# 2. Ouvrez un terminal dans ce dossier
# 3. Lancez l'installation automatique

python setup.py
```

### Option 2: Installation Manuelle

```bash
# Installer les dépendances
pip install SpeechRecognition pyttsx3 pyaudio watchdog

# Créer la structure de dossiers
mkdir -p modules data data/user_projects
```

## 🏗️ Structure du Projet

```
jarvis_assistant/
├── main.py              # 🚀 Fichier principal
├── setup.py             # ⚙️ Installation automatique
├── modules/
│   ├── __init__.py      # 📦 Module Python
│   ├── assistant.py     # 🧠 Logique de l'assistant
│   ├── observer.py      # 👁️ Surveillance fichiers
│   ├── logger.py        # 📝 Journalisation
│   └── voice_assistant.py # 🎙️ Fonctions vocales
└── data/
    ├── user_projects/   # 📁 Vos projets (surveillés)
    ├── jarvis_log.txt   # 💬 Historique conversations
    ├── jarvis_system.log # ⚙️ Événements système
    └── file_observer.log # 👁️ Changements fichiers
```

## 🎮 Utilisation

### Démarrage

```bash
# Mode vocal (par défaut)
python main.py

# Mode texte uniquement
# Modifiez main.py: run_jarvis(mode="text")
```

### Commandes Utiles

**En mode vocal :**
- Dites "Bonjour Jarvis" pour commencer
- "Quelle heure est-il ?" 
- "Aide-moi"
- "Au revoir" pour quitter

**En mode texte :**
- `aide` - Affiche l'aide
- `heure` - Heure actuelle
- `date` - Date actuelle  
- `projet` - Infos sur la surveillance
- `stop` - Quitter

## 🛠️ Dépannage

### Problèmes Audio (PyAudio)

**Windows :**
```bash
# Si pip install échoue:
pip install pipwin
pipwin install pyaudio

# Ou téléchargez le .whl depuis:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

**macOS :**
```bash
# Installer Homebrew puis:
brew install portaudio
pip install pyaudio
```

**Linux (Ubuntu/Debian) :**
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio
```

### Problèmes de Microphone

1. **Vérifiez les permissions** : Autorisez l'accès micro
2. **Testez le micro** : Utilisez l'enregistreur système
3. **Listez les micros disponibles** : Ajoutez ce code de test

```python
import speech_recognition as sr
print("Micros disponibles:")
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {name}")
```

### Mode Dégradé

Si les fonctions vocales ne marchent pas, Jarvis fonctionnera en mode texte uniquement.

## 🎛️ Configuration Avancée

### Personnaliser la Voix

Modifiez dans `modules/voice_assistant.py` :

```python
# Vitesse de parole (mots/minute)
engine.setProperty('rate', 120)  # Plus lent
engine.setProperty('rate', 200)  # Plus rapide

# Volume (0.0 à 1.0)
engine.setProperty('volume', 0.8)  # Plus faible
```

### Changer les Dossiers Surveillés

Modifiez dans `main.py` :

```python
# Changer le dossier surveillé
obs_thread = threading.Thread(target=observer.start_observer, 
                             args=("votre/dossier/projet",))
```

### Ajouter des Réponses

Dans `modules/assistant.py`, fonction `simple_response()` :

```python
elif "votre commande" in message:
    return "Votre réponse personnalisée"
```

## 📊 Logs et Historique

- **Conversations** : `data/jarvis_log.txt`
- **Système** : `data/jarvis_system.log`  
- **Fichiers** : `data/file_observer.log`

## 🔐 Confidentialité

- **100% Local** : Vos données restent sur votre machine
- **Exception** : Reconnaissance vocale utilise l'API Google (phrases audio envoyées temporairement)
- **Aucun tracking** : Aucune donnée personnelle collectée

## 🚧 Limitations Actuelles

- Reconnaissance vocale nécessite Internet
- Réponses basiques (pas d'IA avancée intégrée)
- Interface en ligne de commande uniquement

## 🔮 Améliorations Futures

- [ ] Interface graphique (GUI)
- [ ] IA locale (Ollama/LLaMA)
- [ ] Commandes système avancées
- [ ] Intégration calendrier/emails
- [ ] Plugins personnalisés
- [ ] Reconnaissance vocale offline

## 🐛 Signaler un Bug

Si vous rencontrez un problème :

1. Vérifiez les logs dans `data/`
2. Testez en mode texte : `run_jarvis(mode="text")`
3. Vérifiez l'installation : `python setup.py`

## 📄 Licence

Ce projet est libre d'utilisation pour un usage personnel et éducatif.

## 🤝 Contribution

Ce projet est ouvert aux améliorations ! N'hésitez pas à :
- Proposer des nouvelles fonctionnalités
- Corriger des bugs
- Améliorer la documentation

---

**🎉 Amusez-vous bien avec votre assistant Jarvis !**