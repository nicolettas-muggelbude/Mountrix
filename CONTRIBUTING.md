# Contributing zu Mountrix

Vielen Dank für dein Interesse, zu Mountrix beizutragen! 🎉

## Code of Conduct

Dieses Projekt folgt einem respektvollen und inklusiven Umgang. Bitte sei freundlich und konstruktiv.

## Wie kann ich beitragen?

### 🐛 Bug Reports

Wenn du einen Fehler gefunden hast:

1. Prüfe, ob der Bug bereits als [Issue](https://github.com/<username>/mountrix/issues) existiert
2. Wenn nicht, erstelle ein neues Issue mit:
   - Klarer Beschreibung des Problems
   - Schritten zur Reproduktion
   - Erwartetes vs. tatsächliches Verhalten
   - System-Informationen (OS, Python-Version, Desktop-Umgebung)
   - Logs (falls verfügbar)

### 💡 Feature Requests

Neue Ideen sind willkommen!

1. Prüfe [bestehende Feature Requests](https://github.com/<username>/mountrix/issues?q=is%3Aissue+label%3Aenhancement)
2. Erstelle ein Issue mit Label `enhancement`
3. Beschreibe:
   - Was soll die Funktion tun?
   - Warum ist sie nützlich?
   - Wie könnte sie implementiert werden?

### 🔧 Pull Requests

1. **Fork** das Repository
2. Erstelle einen **Feature-Branch**: `git checkout -b feature/mein-feature`
3. **Implementiere** deine Änderungen
4. **Teste** deine Änderungen: `pytest tests/`
5. **Code-Style** prüfen: `black src/ && flake8 src/`
6. **Committe**: `git commit -m "feat: Beschreibung"`
7. **Push**: `git push origin feature/mein-feature`
8. Erstelle einen **Pull Request**

## Entwicklungs-Setup

### Voraussetzungen

```bash
# Ubuntu/Debian
sudo apt install python3.10 python3-pip git

# Optional: GUI-Entwicklung
sudo apt install python3-pyqt6 qttools5-dev-tools  # Qt Designer
sudo apt install glade  # GTK Designer
```

### Setup

```bash
# Repository klonen
git clone https://github.com/<username>/mountrix.git
cd mountrix

# Virtual Environment
python3.10 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
pip install -e .  # Editable install

# Entwicklung starten
python src/mountrix/main.py
```

### Tests ausführen

```bash
# Alle Tests
pytest tests/ -v

# Mit Coverage
pytest tests/ --cov=src/mountrix --cov-report=html

# Einzelner Test
pytest tests/test_fstab.py::test_parse_fstab -v
```

## Code-Style

### Python

- **PEP 8** Standard
- **Black** Formatter (line-length: 100)
- **Type Hints** verwenden
- **Docstrings** für alle öffentlichen Funktionen/Klassen

```python
def mount_share(source: str, mountpoint: str, options: List[str]) -> bool:
    """
    Bindet ein Netzwerk-Share ein.

    Args:
        source: Der Quell-Pfad (z.B. '//nas/share')
        mountpoint: Der Ziel-Mountpoint (z.B. '/mnt/nas')
        options: Mount-Optionen als Liste

    Returns:
        True bei Erfolg, False bei Fehler

    Raises:
        PermissionError: Wenn Root-Rechte fehlen
    """
    pass
```

### Commits

Wir nutzen [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Neue Funktion hinzufügen
fix: Bug beheben
docs: Dokumentation ändern
style: Code-Formatierung (keine funktionale Änderung)
refactor: Code umstrukturieren
test: Tests hinzufügen/ändern
chore: Build-Prozess, Dependencies
```

Beispiele:
```
feat: NAS-Template für Synology hinzufügen
fix: fstab-Backup-Funktion reparieren
docs: Benutzerhandbuch aktualisieren
```

## Projekt-Struktur

```
src/mountrix/
├── core/          # Backend-Logik
│   ├── detector.py    # Desktop/Laufwerk-Erkennung
│   ├── mounter.py     # Mount-Operationen
│   ├── fstab.py       # fstab-Management
│   └── ...
├── gui/           # GUI-Implementierung
│   ├── qt/        # PyQt6
│   └── gtk/       # GTK4
└── utils/         # Hilfs-Funktionen
```

## Testing-Richtlinien

- **Unit-Tests** für alle Core-Module
- **Mocks** für System-Aufrufe (kein echtes Mounten in Tests!)
- **Coverage** mindestens 80%
- **Edge Cases** testen (leere Eingaben, ungültige Pfade, etc.)

## Dokumentation

- Code-Kommentare auf **Englisch**
- User-Dokumentation auf **Deutsch** (primär) und **Englisch**
- Docstrings für alle Public APIs
- README aktualisieren bei neuen Features

## Review-Prozess

1. Automatische Checks (GitHub Actions):
   - pytest
   - black --check
   - flake8
   - mypy

2. Code-Review durch Maintainer
3. Mindestens 1 Approval nötig
4. Merge in `main`

## Fragen?

Bei Fragen kannst du:
- Ein [Issue](https://github.com/<username>/mountrix/issues) erstellen
- Eine [Discussion](https://github.com/<username>/mountrix/discussions) starten

Vielen Dank für deine Beiträge! 🚀
