# config.py - Centralized Configuration Management
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Centralized configuration management for Jarvis Assistant"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Default configuration
        default_config = {
            "version": "1.1.0",
            "assistant": {
                "name": "WillIAm",
                "wake_words": ["william", "bonjour william", "salut william"],
                "sleep_words": ["merci william", "au revoir", "stop", "bonne nuit", "dors william"],
                "default_language": "fr-FR",
                "response_delay": {"min": 1.5, "max": 3.0}
            },
            "tts": {
                "preferred_engine": "deepgram",  # deepgram, gtts, xtts
                "deepgram": {
                    "api_key": os.getenv("DEEPGRAM_API_KEY", ""),
                    "voice": "fr-FR-ANTOINE"
                },
                "xtts": {
                    "speaker_wav": "male_sample.wav",
                    "model": "tts_models/multilingual/multi-dataset/xtts_v2"
                }
            },
            "stt": {
                "timeout": 8,
                "pause_threshold": 0.8,
                "energy_threshold": 300,
                "language": "fr-FR"
            },
            "llm": {
                "provider": "ollama",  # ollama, openai, anthropic
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "model": "llama3",
                    "timeout": 90,
                    "temperature": 0.7
                },
                "max_history_length": 10
            },
            "file_observer": {
                "enabled": True,
                "watch_path": "data/user_projects",
                "ignored_extensions": [".tmp", ".swp", ".log", "~", ".DS_Store"],
                "ignored_names": ["Thumbs.db", ".git", "__pycache__"],
                "dedupe_interval": 1.0
            },
            "knowledge": {
                "web_search_results": 3,
                "ocr_language": "fra",
                "max_document_lines": 10,
                "max_image_text_chars": 500
            },
            "ml": {
                "model_retrain_interval": 24,  # hours
                "min_examples_for_prediction": 5
            },
            "logging": {
                "level": "INFO",
                "max_log_size_mb": 10,
                "backup_count": 3,
                "detailed_conversation_logs": True
            },
            "security": {
                "api_key_encryption": False,
                "log_sensitive_data": False,
                "allowed_domains": ["google.com"]
            }
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        config_to_save = config or self.config
        os.makedirs(self.config_file.parent, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_to_save, f, indent=2, ensure_ascii=False)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'tts.deepgram.voice')"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config()
    
    def reload(self):
        """Reload configuration from file"""
        self.config = self._load_config()

# Singleton instance
config = Config()

# Convenience functions
def get_config(key_path: str, default: Any = None) -> Any:
    return config.get(key_path, default)

def set_config(key_path: str, value: Any):
    config.set(key_path, value)

def reload_config():
    config.reload()
