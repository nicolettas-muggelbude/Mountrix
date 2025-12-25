# Mountrix - Mount Manager für Linux

## Projektziel
Benutzerfreundliches Mounten von Netzlaufwerken und lokalen Laufwerken unter Linux mit moderner PyQt6-GUI.

## Technologie-Stack
- **Python 3.10+**
- **PyQt6** - Moderne GUI-Framework
- **Desktop**: KDE Plasma (MX-Linux), WSL2/Wayland-Support
- **Lizenz**: GNU GPL v3.0

## Aktuelle Implementierung

### Phase 1: Grundstruktur ✅
- Core-Module für fstab-Parsing, Mounting, Desktop-Erkennung
- PyQt6 GUI Grundstruktur (MainWindow + Wizard)
- Advanced Mode Dialogs (Settings, Confirmation, Error, Progress, Rollback)
- Desktop-Umgebungserkennung (KDE, GNOME, XFCE, etc.)

### Phase 2: Modernes Design ✅ (Aktuell)

#### Design-System mit Mountrix Logo-Farben
**Farbschema:**
- **Primär-Blau**: `#3498db` (Buttons, Focus, Selection)
  - Hover: `#5dade2`
  - Pressed: `#2980b9`
- **Akzent-Grün**: `#2ecc71` (CheckBoxes, Success)
  - Dark: `#27ae60`

**Light Mode:**
- Hintergrund: `white` / `#ecf0f1`
- Text: `#2c3e50`
- Rahmen: `#bdc3c7`

**Dark Mode:**
- Hintergrund: `#2c3e50` / `#34495e`
- Text: `#ecf0f1`
- Rahmen: `#7f8c8d`

#### UI-Layout
```
┌─────────────────────────────────────────────────┐
│ [Neu] [Bearbeiten] [Löschen] [Aktualisieren] ☰ │  ← Action Bar
├─────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐ │
│ │ Name │ Typ  │ Quelle │ Mountpoint │ Status │ │  ← TreeWidget
│ │──────┼──────┼────────┼────────────┼────────│ │
│ │ nas  │ CIFS │ //nas  │ /mnt/nas   │ ✓ Gem. │ │
│ └─────────────────────────────────────────────┘ │
│ [Assistent-Modus] [Power-User-Modus]            │  ← Mode Buttons
├─────────────────────────────────────────────────┤
│ Status: 3 Mounts gefunden (2 gemountet)         │  ← StatusBar
└─────────────────────────────────────────────────┘
```

**Hamburger-Menü (☰):**
- Neu, Aktualisieren
- Dark Mode (toggle)
- Einstellungen
- Über Mountrix, Hilfe
- Beenden

#### Gestylte Komponenten
- ✅ **Buttons** - Blau, abgerundete Ecken, Hover-Effekte
- ✅ **Input Fields** - Blauer Fokus-Rahmen
- ✅ **ComboBoxes** - Dropdown-Items Dark-Mode-fähig
- ✅ **TreeWidget** - Blaue Selection, alternierende Zeilen
- ✅ **CheckBoxes** - Grüner Rahmen wenn aktiviert
- ✅ **RadioButtons** - Blau wenn aktiviert
- ✅ **Menu/MenuBar** - Blaue Selection, lesbar in beiden Modi
- ✅ **Scrollbars** - Modern, schlank, abgerundete Handles
- ✅ **ProgressBar** - Blauer Fortschritt
- ✅ **Hamburger-Button** - Dynamisches Styling für Light/Dark

#### Theme-System
```python
def get_modern_stylesheet(theme: str = "light") -> str:
    """Dynamisches Stylesheet basierend auf Theme."""
    # Light/Dark Farben werden automatisch angepasst

def apply_theme(theme: str) -> None:
    """Wendet Theme an: 'light', 'dark', oder 'system'."""
    # Palette + Stylesheet werden synchronisiert
```

**Theme-Synchronisation:**
- Dark Mode Toggle im Hamburger-Menü bleibt mit Einstellungen synchronisiert
- Hamburger-Button passt Farbe automatisch an (hell im Dark Mode, dunkel im Light Mode)
- Alle Widgets unterstützen beide Modi vollständig

#### Behobene Probleme
1. ✅ Stylesheet wird vor Fenster-Erstellung gesetzt (in `main()`)
2. ✅ `apply_theme()` wendet Stylesheet nach Palette-Änderung neu an
3. ✅ TreeWidget/Liste komplett Dark-Mode-fähig
4. ✅ Hamburger-Button im Dark Mode sichtbar
5. ✅ Menü-Items lesbar in beiden Modi (kein weißer Text auf weißem Grund)
6. ✅ ComboBox-Dropdowns lesbar in Einstellungen
7. ✅ CheckBoxes visuell klar durch grünen Rahmen
8. ✅ Dark Mode Haken synchronisiert mit Einstellungen

### Spezielle Features

#### WSL2/Wayland ComboBox-Fix
```python
def setup_combobox_auto_close(combobox: QComboBox):
    """Workaround für WSL2/Wayland wo Popups nicht automatisch schließen."""
    # Verwendet 'pressed' Signal + QTimer für Event-Loop-Verzögerung
    # Schließt Popup-Fenster direkt via window().close()
```

#### Desktop-Erkennung
- Erkennt KDE Plasma, GNOME, XFCE, LXDE, etc.
- System-Theme-Detection für Auto-Dark-Mode

## Projektstruktur
```
Mountrix/
├── src/mountrix/
│   ├── core/
│   │   ├── detector.py      # Desktop/Theme-Erkennung
│   │   ├── fstab.py         # fstab-Parser
│   │   └── mounter.py       # Mount-Operationen
│   └── gui/qt/
│       ├── main_window.py   # Hauptfenster + Stylesheet
│       └── dialogs.py       # Settings, Confirmation, etc.
├── data/icons/
│   └── mountrix-logo.svg    # Logo mit #3498db + #2ecc71
├── test_modern_design.py    # GUI-Test
└── CLAUDE.md               # Diese Datei

```

## Git-Status
```
Branch: main
Letzter Commit: feat: GUI-Integration mit Desktop-Erkennung implementiert

Implementierte Features:
- PyQt6 GUI mit Wizard + Advanced Mode
- Modern Design mit Logo-Farben
- Vollständiger Dark Mode Support
- Hamburger-Menü Navigation
```

## Nächste Schritte (Phase 3+)

### TODO: Funktionalität
- [ ] Wizard-Dialog implementieren (Step-by-Step Mount-Erstellung)
- [ ] Advanced-Dialog implementieren (direkte fstab-Konfiguration)
- [ ] Mount/Unmount-Funktionalität (sudo-Handling)
- [ ] Tatsächliches Löschen/Bearbeiten von Mounts
- [ ] Backup/Rollback für fstab-Änderungen
- [ ] Validierung von Mount-Parametern

### TODO: Weitere GUI-Verbesserungen
- [ ] Icons für Buttons (statt nur Text)
- [ ] Keyboard-Navigation optimieren
- [ ] Tooltips mit mehr Details
- [ ] Animationen für Übergänge
- [ ] Drag & Drop für Mount-Reihenfolge?

### TODO: System-Integration
- [ ] .desktop-Datei für Anwendungsmenü
- [ ] Autostart-Option
- [ ] Systemtray-Integration?
- [ ] Benachrichtigungen bei Mount-Fehlern

## Entwicklungsnotizen

### Design-Philosophie
- **Modern & Clean**: Breeze-inspiriert, aber mit eigener Identität
- **Logo-Farben durchgängig**: Markenidentität in jedem UI-Element
- **Dark Mode First-Class**: Kein Nachgedanke, vollständig integriert
- **Keine Doppelungen**: Hamburger-Menü statt MenuBar + Toolbar
- **Konsistenz**: Alle Widgets folgen dem gleichen Farbschema

### Lessons Learned
1. **Qt Stylesheets + Palette**: Palette kann Stylesheet überschreiben → immer nach `setPalette()` neu `setStyleSheet()` aufrufen
2. **f-strings in QSS**: Alle CSS-Blöcke mit `{{ }}` escapen, nur Variablen mit `{ }`
3. **ComboBox Dropdowns**: `QComboBox QAbstractItemView` für Dropdown-Items stylen
4. **Hamburger-Button**: Separates Styling nötig, da transparenter Hintergrund
5. **WSL2/Wayland**: ComboBox braucht speziellen Auto-Close-Workaround

### Code-Qualität
- Type Hints durchgängig verwendet
- Docstrings für alle öffentlichen Funktionen
- Klare Trennung: Core (Backend) / GUI (Frontend)
- DRY: Stylesheet-Funktion mit Theme-Parameter statt Duplikation

## Testing
```bash
# GUI-Test mit modernem Design
python3 test_modern_design.py

# Teste:
# - Light/Dark Mode Toggle
# - Hamburger-Menü
# - Einstellungen-Dialog
# - TreeWidget Selection
# - Button Hover-Effekte
```

## Verwendete User-Präferenzen
- Ausgaben auf Deutsch
- Ungefragt Versionen aktualisieren
- CLAUDE.md für Projekt-Kontinuität

---
*Zuletzt aktualisiert: 2025-12-25*
*Status: Phase 2 (Modern Design) abgeschlossen ✅*
