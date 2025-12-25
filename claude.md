# Mountrix - Claude Projekt-Kontext

## Projektübersicht
Mountrix ist ein benutzerfreundliches GUI-Tool zum Einbinden von Netzlaufwerken (NFS, SMB/CIFS) und lokalen Laufwerken unter Linux. Ziel ist es, unerfahrenen Nutzern das Mounten zu vereinfachen, während Power-User volle Kontrolle behalten.

## Technische Entscheidungen

### GUI-Framework
- **PyQt6** für Qt-basierte Desktops (KDE, LXQt)
- **GTK4/PyGObject** für GTK-basierte Desktops (GNOME, XFCE, Cinnamon)
- Automatische Erkennung via `$XDG_CURRENT_DESKTOP`

### Python-Version
- Minimum: **Python 3.10+**
- Grund: Bessere Type Hints, Match-Statements, moderne Features

### Berechtigungen
- **PolicyKit/pkexec** für Root-Operationen
- Keine sudo-Passwort-Dialoge
- Helper-Script für privilegierte Operationen

### Ziel-Distributionen
- Ubuntu
- Debian
- Linux Mint

## Entwicklungsumgebung

### Python Virtual Environment
- **Pfad**: `/home/nicole/projekte/Mountrix/venv`
- **Python**: 3.10+ (aktuell 3.12.3)
- **Aktivierung**: `source venv/bin/activate`

**WICHTIG**: Mountrix muss IMMER im venv ausgeführt werden:
```bash
source venv/bin/activate
python3 -m src.mountrix.main
```

### WSL2 + Wayland Konfiguration
- **Display**: DISPLAY=:0
- **Wayland**: WAYLAND_DISPLAY=wayland-0
- **Socket**: `/run/user/1000/wayland-0` → `/mnt/wslg/runtime-dir/wayland-0`
- **Platform**: PyQt6 läuft nativ auf Wayland
- **WSLg**: Vollständig funktionsfähig

### Dependencies
Alle Pakete definiert in `requirements.txt` und `pyproject.toml`:
- **GUI**: PyQt6 >= 6.6.0
- **System**: psutil >= 5.9.0, netifaces >= 0.11.0
- **Network**: smbprotocol >= 1.10.0, pysmb >= 1.2.9
- **Security**: keyring >= 23.0.0, cryptography >= 41.0.0
- **Dev**: pytest, black, flake8, mypy

Installation im venv:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Feature-Scope v1.0

### Protokolle (Priorität)
1. **SMB/CIFS** (Windows-Shares, NAS)
2. **NFS** (Unix/Linux-Shares)
3. **Interne Laufwerke** (SATA, NVMe: ext4, NTFS, exFAT)
4. **Externe Laufwerke** (USB, eSATA: ext4, NTFS, exFAT)

### NAS-Templates
Vorkonfigurierte Templates für:
- AVM FRITZ!NAS
- QNAP NAS
- Western Digital My Cloud
- Synology DiskStation
- UGREEN NAS

### Mount-Typen
- **Statische fstab-Einträge** (v1.0)
- `nofail` Option für fehlertoleranten Boot
- systemd automount in Roadmap

### Benutzer-Modi
1. **Assistent-Modus**: Schritt-für-Schritt für Anfänger
2. **Power-User-Modus**: Direkte Kontrolle über alle Parameter

### Mount-Optionen
- User entscheidet: Nur für ihn (`/media/<username>`) oder alle User (`/mnt`)
- Automatische Mountpoint-Erstellung

### Sicherheit
- Rollback-Funktion bei Fehlern
- Automatisches fstab-Backup vor Änderungen
- Credentials via libsecret (GNOME Keyring / KWallet)
- Logging in `/var/log/mountrix.log`

## Roadmap

### v1.0 (Q1 2026 - Aktuell in Entwicklung)
- GUI mit PyQt6 und GTK4
- NFS, SMB/CIFS
- Interne Laufwerke (SATA, NVMe)
- Externe Laufwerke (USB, eSATA)
- NAS-Templates
- Assistent + Power-User-Modus
- PolicyKit-Integration
- Rollback-Funktion
- Deutsch + Englisch

### v1.1 (Q2 2026)
- CLI-Interface
- Mount-Gruppen / Profile
- Konfiguration Import/Export

### v1.2 (Q3 2026)
- WebDAV
- SSHFS
- systemd automount Option

### v2.0 (Q1 2027)
- rsync-Integration
- Scheduled Mounts
- Web-Interface für Remote-Management

## Paketierung
- **.deb** für Debian/Ubuntu/Mint (Priorität)
- **Snap** für universelle Distribution
- **Flatpak** (später)
- Updates über Paketmanager

## Code-Richtlinien

### Struktur
- Backend unabhängig von GUI (ermöglicht spätere CLI)
- Core-Module in `src/mountrix/core/`
- GUI-spezifisch in `src/mountrix/gui/qt/` und `src/mountrix/gui/gtk/`

### Sicherheit
- Alle User-Eingaben validieren
- Path Traversal verhindern
- Keine Passwörter in Logs
- Credentials mit chmod 600

### Testing
- Unit-Tests mit pytest
- Integration-Tests mit Mock-fstab
- 80%+ Test-Coverage angestrebt

### Logging
- Strukturiertes Logging
- Log-Level: DEBUG, INFO, WARNING, ERROR
- Rotation bei 10MB

## Wichtige Dateien
- `/etc/fstab` - Ziel-Datei für Mount-Einträge
- `/var/backups/fstab.backup.<timestamp>` - Automatische Backups
- `~/.mountrix/credentials/` - Verschlüsselte Zugangsdaten
- `~/.config/mountrix/config.ini` - User-Konfiguration
- `/usr/share/polkit-1/actions/org.mountrix.policy` - PolicyKit

## Aktueller Status
- ✅ Projekt-Konzept definiert
- ✅ Implementierungsplan erstellt
- ✅ Repository erstellt (GitHub)
- ✅ **Phase 1: Core-Backend entwickeln** (ABGESCHLOSSEN!)
  - ✅ detector.py - Desktop & Laufwerk-Erkennung (17 Tests, 84% Coverage)
  - ✅ fstab.py - fstab-Management (23 Tests, 83% Coverage)
  - ✅ templates.py - NAS-Template-Management (23 Tests, 77% Coverage)
  - ✅ network.py - Netzwerk-Diagnostik (38 Tests, 90% Coverage)
  - ✅ mounter.py - Mount-Logik (37 Tests, 86% Coverage)
  - ✅ credentials.py - Authentifizierung (38 Tests, 86% Coverage)
- ✅ **Phase 2: GUI entwickeln** (ABGESCHLOSSEN!)
  - ✅ PyQt6 Hauptfenster (main_window.py) - 90% Coverage, 26 Tests
  - ✅ 9-Schritt-Assistent (wizard.py) - 79% Coverage, 37 Tests
  - ✅ Power-User-Modus (advanced.py) - 87% Coverage, 25 Tests
  - ✅ Dialogs (dialogs.py) - 97% Coverage, 27 Tests
  - ✅ **115 GUI-Tests insgesamt** - Alle bestanden in 0.77s
  - 🔲 GTK4 GUI (optional - nicht erforderlich für v1.0)
- 🔲 Phase 3: Features integrieren
- 🔲 Phase 4: Integration-Testing
- 🔲 Phase 5: Paketierung & Release

### Letzte Änderungen (2025-12-24)
- 🎨 **Dark Mode Implementation** - Automatische Theme-Erkennung
  - `detect_system_theme()` in detector.py implementiert
  - Unterstützt KDE (kreadconfig5), GNOME (gsettings), XFCE (xfconf-query)
  - `create_dark_palette()` und `create_light_palette()` in main_window.py
  - `apply_theme()` mit "system", "dark", "light" Modi
  - Automatische Anwendung bei GUI-Start basierend auf Desktop-Theme
  - Theme-Umschaltung in Einstellungen-Dialog integriert
- 🔧 **ComboBox UX-Fix für WSL2/Wayland** (GELÖST!)
  - **Problem**: Dropdowns blieben nach Auswahl geöffnet, Auswahl nur durch Klick außerhalb übernommen
  - **Ursache**: Qt-Signals `clicked` und `activated` funktionieren nicht auf WSL2/Wayland
  - **Lösung**: `setup_combobox_auto_close()` Helper-Funktion in dialogs.py
    - Nutzt `view().pressed` Signal (einziges Signal das auf Wayland funktioniert)
    - Schließt Popup-Fenster direkt: `view().window().hide()` + `view().window().close()`
    - Standard `hidePopup()` alleine funktioniert nicht auf Wayland
    - Setzt Auswahl mit 10ms Verzögerung nach Popup-Schließung
  - Angewendet auf alle 7 ComboBoxes: dialogs.py (4x), advanced.py (1x), wizard.py (2x)
  - WSL2/Wayland-spezifischer Workaround, behebt komplettes UX-Problem
- 🎉 **Phase 2 ABGESCHLOSSEN!** - GUI vollständig getestet
  - **115 GUI-Tests geschrieben** für alle 4 PyQt6-Module
  - test_gui_dialogs.py: 27 Tests, 97% Coverage (5 Dialog-Klassen)
  - test_gui_main_window.py: 26 Tests, 90% Coverage (Hauptfenster)
  - test_gui_wizard.py: 37 Tests, 79% Coverage (9-Schritt-Assistent)
  - test_gui_advanced.py: 25 Tests, 87% Coverage (Power-User-Modus)
  - Alle Tests bestehen in 0.77s
  - Gesamtprojekt-Coverage: 55% (1865 Statements)
- 🎉 **Stabile Basis erreicht!** - Komplette Verifizierung der Entwicklungsumgebung
  - Virtual Environment vollständig eingerichtet
  - Alle 176 Core-Backend-Tests + 115 GUI-Tests = **291 Tests insgesamt**
  - PyQt6 GUI-Module erfolgreich getestet
  - Wayland-Integration in WSL2 funktioniert einwandfrei
  - MountrixMainWindow kann erstellt werden (Qt Platform: wayland)
- ✅ **Dependencies stabilisiert**
  - psutil, PyQt6, keyring, netifaces, smbprotocol installiert
  - requirements.txt und pyproject.toml synchronisiert
  - Dokumentation der venv-Nutzung in claude.md
- ✅ **Alle Core-Module verifiziert**
  - detector.py, fstab.py, templates.py, network.py, mounter.py, credentials.py
  - Alle Imports funktionieren fehlerfrei
  - Core-Coverage durchschnittlich 85%

### Änderungen (2025-12-17)
- ✅ **main.py implementiert** - Desktop-Erkennung und GUI-Framework-Loading
  - Automatische Erkennung von Qt-basierten (KDE, LXQt) und GTK-basierten Desktops (GNOME, XFCE, Cinnamon)
  - Intelligente Framework-Auswahl: Nativer Stack wird bevorzugt, Fallback auf alternative GUI
  - Dependency-Checks für PyQt6 und GTK4
  - Fehlerbehandlung bei fehlenden Abhängigkeiten
- ✅ **bin/mountrix Einstiegspunkt** - Kommandozeilen-Script zum direkten Starten
- ✅ **GUI auf "Du"-Form umgestellt** - Alle Dialoge nutzen informelle Ansprache
- 🎉 **Phase 2.1 PyQt6 GUI komplett abgeschlossen!**
  - main_window.py (400 Zeilen)
  - wizard.py (600 Zeilen, 9-Schritt-Assistent)
  - advanced.py (400 Zeilen, Power-User-Modus)
  - dialogs.py (400 Zeilen, 5 Dialog-Typen)
- 🎉 **Phase 1 Core-Backend komplett abgeschlossen!**
- **credentials.py vollständig implementiert** mit folgenden Funktionen:
  - `save_credentials_keyring()` - Speichert Credentials in GNOME Keyring/KWallet
  - `load_credentials_keyring()` - Lädt Credentials aus Keyring
  - `delete_credentials_keyring()` - Löscht Credentials aus Keyring
  - `generate_credentials_file()` - Erstellt CIFS-Credential-Dateien (chmod 600)
  - `delete_credentials_file()` - Löscht Credential-Dateien (mit Security-Check)
  - `validate_ssh_key()` - Validiert SSH-Keys (Permissions, Format)
  - `get_credential_files()` - Listet alle Credential-Dateien
  - `read_credentials_file()` - Liest und parsed Credential-Dateien
  - `is_keyring_available()` - Prüft Keyring-Verfügbarkeit
- **38 Unit-Tests** für credentials.py mit 86% Code-Coverage
- Alle 176 Core-Backend-Tests bestehen ✅

**Phase 1 Statistik:**
- 6 Module vollständig implementiert
- 176 Unit-Tests insgesamt
- Durchschnittliche Coverage: 85%

**Phase 2.1 PyQt6 GUI - Fortschritt:**
- ✅ main_window.py: Hauptfenster mit Menü, Toolbar, TreeView
- ✅ wizard.py: 9-Schritt-Assistent für Anfänger
- ✅ advanced.py: Power-User-Modus mit Syntax-Highlighting
- ✅ dialogs.py: Bestätigung, Fehler, Progress, Rollback, Einstellungen
- ✅ Integration mit main.py (Desktop-Erkennung)
- ✅ Einstiegspunkt bin/mountrix erstellt
- 🔲 GUI-Tests

## Hinweise für Claude
- Alle Ausgaben im Terminal auf **Deutsch**
- Bei Script-Updates nicht jede Änderung nachfragen
- Diese claude.md automatisch fortführen bei Projekt-Fortschritt
- Code-Style: PEP 8, Type Hints verwenden
- Kommentare auf Englisch im Code, Dokumentation auf Deutsch
- **GUI-Dialoge und Benutzeransprache: "Du" statt "Sie"**

### KRITISCH: Virtual Environment
**IMMER das venv aktivieren** vor allen Python-Operationen:
```bash
source venv/bin/activate
```

Betroffen:
- ✅ `python3 -m src.mountrix.main` (Mountrix starten)
- ✅ `pytest tests/` (Tests ausführen)
- ✅ `pip install` (Pakete installieren)
- ✅ Alle Python-Imports und -Ausführungen

**Ohne venv werden fehlende Dependencies auftreten!**
