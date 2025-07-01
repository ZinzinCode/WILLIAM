from sklearn.tree import DecisionTreeClassifier
import pickle
import os

MODEL_PATH = "data/william_model.pkl"
DATA_PATH = "data/william_model_data.pkl"

# Chargement des exemples d'habitudes (dataset)
def load_data():
    if not os.path.exists(DATA_PATH):
        # Dataset initial par défaut
        X = [
            [9, 1], [14, 0], [18, 1], [21, 0]
        ]
        y = [
            'Ouvrir VSCode', 'Lire les mails', 'Lancer Spotify', 'Fermer les applications'
        ]
        return X, y
    else:
        X, y = [], []
        with open(DATA_PATH, "rb") as f:
            while True:
                try:
                    x, label = pickle.load(f)
                    X.append(x)
                    y.append(label)
                except EOFError:
                    break
        return X, y

def train_and_save_model():
    X, y = load_data()
    clf = DecisionTreeClassifier()
    clf.fit(X, y)
    os.makedirs("data", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)

def predict_action(heure, projet_actif):
    if not os.path.exists(MODEL_PATH):
        train_and_save_model()
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    action = model.predict([[heure, int(projet_actif)]])[0]
    return action

def add_habit_example(heure, projet_actif, action):
    os.makedirs("data", exist_ok=True)
    with open(DATA_PATH, "ab") as f:
        pickle.dump(([heure, int(projet_actif)], action), f)
    # Réentraîne le modèle à chaque ajout pour qu'il prenne en compte le nouvel exemple
    train_and_save_model()

# Pour initialiser le modèle au premier lancement
if __name__ == "__main__":
    train_and_save_model()
    print("Modèle entraîné et sauvegardé.")