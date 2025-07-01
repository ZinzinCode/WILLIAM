# Configuration TTS optimisée pour William
TTS_CONFIG = {
    "preferred_engine": "xtts",  # xtts, pyttsx3
    "language": "fr",
    "speed": 1.0,
    "volume": 0.9,
    "voice_cloning": True,
    "cache_enabled": True,
    "async_processing": True,
    "quality": "high",  # high, medium, fast
    
    # Paramètres XTTS
    "xtts": {
        "model": "tts_models/multilingual/multi-dataset/xtts_v2",
        "gpu": True,
        "split_sentences": True,
        "temperature": 0.7,
    },
    
    # Paramètres pyttsx3 (fallback)
    "pyttsx3": {
        "rate": 180,
        "volume": 0.9,
        "voice_preference": ["hortense", "marie", "french", "fr"]
    }
}
