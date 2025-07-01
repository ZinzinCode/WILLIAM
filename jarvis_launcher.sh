# jarvis.sh (Linux/macOS)
#!/bin/bash

echo "🤖 Lancement de l'Assistant Jarvis..."

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier que le fichier main.py existe
if [ ! -f "main.py" ]; then
    echo "❌ Fichier main.py introuvable"
    echo "💡 Exécutez ce script depuis le dossier jarvis_assistant/"
    exit 1
fi

# Lancer Jarvis
python3 main.py

echo "👋 Jarvis s'est arrêté"

# ==========================================
# jarvis.bat (Windows)
# ==========================================
# @echo off
# echo 🤖 Lancement de l'Assistant Jarvis...
# 
# REM Vérifier que Python est installé
# python --version >nul 2>&1
# if errorlevel 1 (
#     echo ❌ Python n'est pas installé ou non accessible
#     pause
#     exit /b 1
# )
# 
# REM Vérifier que le fichier main.py existe
# if not exist "main.py" (
#     echo ❌ Fichier main.py introuvable
#     echo 💡 Exécutez ce script depuis le dossier jarvis_assistant/
#     pause
#     exit /b 1
# )
# 
# REM Lancer Jarvis
# python main.py
# 
# echo 👋 Jarvis s'est arrêté
# pause