import time
import os
from datetime import datetime
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️ Module watchdog non installé. Observer désactivé.")

class ProjectObserver(FileSystemEventHandler):
    """Gestionnaire d'événements pour surveiller les fichiers"""
    
    def __init__(self):
        super().__init__()
        self.last_events = {}  # Pour éviter les doublons d'événements
        
    def _should_ignore_event(self, event):
        """Filtre les événements à ignorer"""
        if event.is_directory:
            return True
            
        # Ignorer les fichiers temporaires et système
        ignored_extensions = ['.tmp', '.swp', '.log', '~', '.DS_Store']
        ignored_names = ['Thumbs.db', '.git', '__pycache__']
        
        file_path = event.src_path
        
        # Vérifier les extensions
        for ext in ignored_extensions:
            if file_path.endswith(ext):
                return True
                
        # Vérifier les noms de fichiers
        for name in ignored_names:
            if name in file_path:
                return True
                
        return False
        
    def _deduplicate_event(self, event):
        """Évite les événements en double"""
        key = f"{event.event_type}:{event.src_path}"
        current_time = time.time()
        
        if key in self.last_events:
            if current_time - self.last_events[key] < 1:  # Moins d'1 seconde
                return True
                
        self.last_events[key] = current_time
        return False

    def on_modified(self, event):
        """Fichier modifié"""
        if self._should_ignore_event(event) or self._deduplicate_event(event):
            return
            
        file_name = os.path.basename(event.src_path)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[🔄 {timestamp}] Modifié : {file_name}")
        
        # Log dans le fichier
        self._log_event("MODIFIÉ", event.src_path)

    def on_created(self, event):
        """Nouveau fichier créé"""
        if self._should_ignore_event(event) or self._deduplicate_event(event):
            return
            
        file_name = os.path.basename(event.src_path)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[📁 {timestamp}] Nouveau : {file_name}")
        
        # Log dans le fichier
        self._log_event("CRÉÉ", event.src_path)

    def on_deleted(self, event):
        """Fichier supprimé"""
        if self._should_ignore_event(event) or self._deduplicate_event(event):
            return
            
        file_name = os.path.basename(event.src_path)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[🗑️ {timestamp}] Supprimé : {file_name}")
        
        # Log dans le fichier
        self._log_event("SUPPRIMÉ", event.src_path)

    def on_moved(self, event):
        """Fichier déplacé/renommé"""
        if self._should_ignore_event(event):
            return
            
        old_name = os.path.basename(event.src_path)
        new_name = os.path.basename(event.dest_path)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[📦 {timestamp}] Déplacé : {old_name} → {new_name}")
        
        # Log dans le fichier
        self._log_event("DÉPLACÉ", f"{event.src_path} → {event.dest_path}")
        
    def _log_event(self, event_type, file_path):
        """Enregistre l'événement dans un fichier log"""
        try:
            with open("data/file_observer.log", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {event_type}: {file_path}\n")
        except Exception as e:
            print(f"❌ Erreur lors de l'écriture du log : {e}")

def start_observer(path="data/user_projects"):
    """Démarre l'observateur de fichiers"""
    if not WATCHDOG_AVAILABLE:
        print("❌ Impossible de démarrer l'observer : module watchdog manquant")
        print("💡 Installez-le avec : pip install watchdog")
        return
        
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 Dossier créé : {path}")
        
    event_handler = ProjectObserver()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    
    print(f"📡 Surveillance de '{path}' activée...")
    print("🔍 Jarvis observe maintenant vos fichiers de projet")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n📡 Arrêt de l'observateur...")
        observer.stop()
    except Exception as e:
        print(f"❌ Erreur de l'observateur : {e}")
        observer.stop()
        
    observer.join()
    print("📡 Observateur arrêté")

# Fonction de fallback si watchdog n'est pas disponible
def simple_observer(path="data/user_projects"):
    """Observer simple sans watchdog (fallback)"""
    print(f"📡 Observer simple activé pour '{path}'")
    print("⚠️ Fonctionnalités limitées - installez watchdog pour plus d'options")
    
    if not os.path.exists(path):
        os.makedirs(path)
        
    last_files = set()
    
    try:
        while True:
            current_files = set()
            for root, dirs, files in os.walk(path):
                for file in files:
                    current_files.add(os.path.join(root, file))
            
            # Nouveaux fichiers
            new_files = current_files - last_files
            for file in new_files:
                print(f"[📁 {datetime.now().strftime('%H:%M:%S')}] Nouveau : {os.path.basename(file)}")
            
            # Fichiers supprimés
            deleted_files = last_files - current_files
            for file in deleted_files:
                print(f"[🗑️ {datetime.now().strftime('%H:%M:%S')}] Supprimé : {os.path.basename(file)}")
            
            last_files = current_files
            time.sleep(5)  # Vérification toutes les 5 secondes
            
    except KeyboardInterrupt:
        print("\n📡 Observer simple arrêté")