import threading
import concurrent.futures
import os

# Pour l'OCR (exemple avec pytesseract + PIL)
def ocr_image(image_path):
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="fra")
        return text
    except Exception as e:
        return f"Erreur OCR: {e}"

# Pour l'audio (transcription avec Whisper)
def transcribe_audio(audio_path, language="fr"):
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language=language)
        return result.get("text", "")
    except Exception as e:
        return f"Erreur transcription audio: {e}"

# Pour la vidéo (extraction audio puis transcription)
def analyze_video(video_path, language="fr"):
    try:
        import moviepy.editor as mp
        audio_path = f"{video_path}.audio_temp.wav"
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        text = transcribe_audio(audio_path, language=language)
        os.remove(audio_path)
        return text
    except Exception as e:
        return f"Erreur analyse vidéo: {e}"

# Pour résumé PDF
def summarize_pdf(pdf_path):
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        return summarize_text(text)
    except Exception as e:
        return f"Erreur résumé PDF: {e}"

# Pour résumé DOCX
def summarize_docx(docx_path):
    try:
        import docx
        doc = docx.Document(docx_path)
        text = "\n".join([p.text for p in doc.paragraphs])
        return summarize_text(text)
    except Exception as e:
        return f"Erreur résumé DOCX: {e}"

# Résumé texte générique IA (à adapter pour ton LLM)
def summarize_text(text):
    try:
        # Ex : ollama, openai, transformers...
        from ollama_api import ollama_chat
        summary = ollama_chat(f"Résume ce texte en français en 10 lignes maximum :\n{text}", [], model="llama3:latest")
        return summary
    except Exception as e:
        return f"Erreur résumé IA: {e}"

# --- Système asynchrone (threading) ---
def async_task(fn, args=(), kwargs=None, gui_callback=None):
    if kwargs is None:
        kwargs = {}
    def task():
        result = fn(*args, **kwargs)
        if gui_callback:
            gui_callback(result)
    threading.Thread(target=task, daemon=True).start()

# --- Exemple d'utilisation dans la GUI ---
# from analyze import async_task, ocr_image, transcribe_audio, analyze_video, summarize_pdf, summarize_docx
# async_task(ocr_image, args=("image.png",), gui_callback=gui.append_text)
# async_task(transcribe_audio, args=("audio.wav",), gui_callback=gui.append_text)
# async_task(analyze_video, args=("video.mp4",), gui_callback=gui.append_text)
# async_task(summarize_pdf, args=("file.pdf",), gui_callback=gui.append_text)
# async_task(summarize_docx, args=("file.docx",), gui_callback=gui.append_text)