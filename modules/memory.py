import pickle
def save_snapshot(self, path="memory_snapshot.pkl"):
    with open(path, "wb") as f:
        pickle.dump(self, f)