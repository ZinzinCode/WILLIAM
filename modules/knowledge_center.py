import requests
from bs4 import BeautifulSoup
import pytesseract
import pyautogui
from PIL import Image
import os

# --- Recherche Web Google (scraping des 3 premiers résultats) ---
def web_search(query, lang="fr"):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://www.google.com/search?q={query}&hl={lang}"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.select('.tF2Cxc')  # Google result blocks
    data = []
    for res in results[:3]:
        title_tag = res.select_one('h3')
        link_tag = res.select_one('a')
        snippet_tag = res.select_one('.VwiC3b')
        title = title_tag.text if title_tag else ""
        link = link_tag['href'] if link_tag else ""
        snippet = snippet_tag.text if snippet_tag else ""
        data.append({"title": title, "link": link, "snippet": snippet})
    return data

# --- OCR Capture d'écran complète ---
def read_screen_text():
    screenshot = pyautogui.screenshot()
    text = pytesseract.image_to_string(screenshot, lang='fra')
    return text

# --- OCR d'une zone spécifique de l'écran ---
def read_screen_area(left, top, width, height):
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    text = pytesseract.image_to_string(screenshot, lang='fra')
    return text

# --- Résumé de document texte brut (simple) ---
def summarize_document(path, max_lines=10):
    if not os.path.exists(path):
        return "Fichier introuvable."
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) <= max_lines:
        return "".join(lines)
    else:
        return "".join(lines[:max_lines]) + "\n[...]"

# --- Résumé document image ou PDF (OCR sur image) ---
def summarize_image_document(image_path, max_chars=500):
    if not os.path.exists(image_path):
        return "Fichier image introuvable."
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang='fra')
    return text[:max_chars] + ("\n[...]" if len(text) > max_chars else "")

# --- Exemple d'analyse d'habitude utilisateur (à compléter avec ML) ---
def analyze_user_habit():
    return "Module d'analyse d'habitude à compléter."

# Exemple d'utilisation (à supprimer en prod) :
if __name__ == "__main__":
    print("Recherche web :")
    for res in web_search("machine learning explication"):
        print(res)
    print("\nTexte à l'écran :", read_screen_text())