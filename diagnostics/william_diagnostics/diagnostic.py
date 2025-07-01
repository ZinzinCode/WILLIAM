from .monitor import monitor
import json

def run_diagnostic():
    """
    Fonction principale de diagnostic à appeler depuis main.py ou la GUI.
    Retourne un rapport complet de l'état des modules.
    """
    print("🔍 Démarrage du diagnostic William...")
    results = monitor.run_single_check()
    total_modules = len(results)
    healthy_modules = sum(1 for r in results.values() if r["status"] == "OK")
    print(f"\n📊 Rapport de diagnostic:")
    print(f"   Modules testés: {total_modules}")
    print(f"   Modules OK: {healthy_modules}")
    print(f"   Modules en erreur: {total_modules - healthy_modules}")
    for module_name, result in results.items():
        if result["status"] == "ERROR":
            print(f"   ❌ {module_name}: {result['explanation']}")
            if result.get("fixed"):
                print(f"      ✅ Réparation tentée avec succès")
        else:
            print(f"   ✅ {module_name}: Fonctionnel")
    # Sauvegarder le rapport
    try:
        with open("william_diagnostics/logs/last_diagnostic.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
    return results

def start_continuous_monitoring():
    """Démarre la surveillance continue"""
    return monitor.start_monitoring()

def stop_continuous_monitoring():
    """Arrête la surveillance continue"""
    return monitor.stop_monitoring()

def get_system_status():
    """Retourne l'état actuel des modules (pour la GUI ou l'API)"""
    return monitor.get_status()