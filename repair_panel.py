from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QListWidget, QHBoxLayout

from repair import audit_code, apply_patch, undo_last_repair

class RepairPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mode REPAIR")
        self.layout = QVBoxLayout(self)
        self.suggestions = audit_code()
        self.list = QListWidget()
        for sug in self.suggestions:
            self.list.addItem(f"{sug['title']} ({sug['filename']})")
        self.layout.addWidget(QLabel("Suggestions de réparation :"))
        self.layout.addWidget(self.list)
        self.desc = QTextEdit("")
        self.layout.addWidget(self.desc)
        btns = QHBoxLayout()
        self.apply_btn = QPushButton("✅ Appliquer")
        self.ignore_btn = QPushButton("❌ Ignorer")
        self.undo_btn = QPushButton("Annuler dernière correction")
        btns.addWidget(self.apply_btn)
        btns.addWidget(self.ignore_btn)
        btns.addWidget(self.undo_btn)
        self.layout.addLayout(btns)
        self.list.currentRowChanged.connect(self.show_suggestion)
        self.apply_btn.clicked.connect(self.apply_selected)
        self.ignore_btn.clicked.connect(self.ignore_selected)
        self.undo_btn.clicked.connect(self.undo_last)
        self.show_suggestion(0)

    def show_suggestion(self, idx):
        if 0 <= idx < len(self.suggestions):
            sug = self.suggestions[idx]
            self.desc.setText(f"{sug['desc']}\n\nPatch proposé :\n{sug['patch']}")

    def apply_selected(self):
        idx = self.list.currentRow()
        if 0 <= idx < len(self.suggestions):
            sug = self.suggestions[idx]
            filename = sug['filename']
            with open(filename, encoding="utf-8") as f:
                old = f.read()
            new = old.replace("\nimport os\nimport os\n", "\nimport os\n")
            apply_patch(filename, new)
            self.desc.append("\n✅ Patch appliqué et sauvegarde créée.")

    def ignore_selected(self):
        self.desc.append("\n❌ Suggestion ignorée.")

    def undo_last(self):
        msg = undo_last_repair()
        self.desc.append(f"\n↩️ {msg}")