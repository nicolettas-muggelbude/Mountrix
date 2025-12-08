# Mountrix - Detaillierter Implementierungsplan

## Projektziel
Benutzerfreundliches GUI-Tool zum Einbinden von Netzlaufwerken (NFS, SMB/CIFS) und lokalen Laufwerken unter Linux mit Fokus auf Anfänger und Power-User.

---

## 1. Technische Basis

### 1.1 Anforderungen
- **Python**: 3.10+
- **GUI-Frameworks**:
  - PyQt6 (für KDE, LXQt)
  - GTK4/PyGObject (für GNOME, XFCE, Cinnamon)
  - Automatische Desktop-Erkennung via `$XDG_CURRENT_DESKTOP`
- **Privilegien**: PolicyKit/pkexec für Root-Operationen
- **Ziel-Distributionen**: Ubuntu, Debian, Linux Mint

### 1.2 Projektstruktur
```
/mountrix
├── src/
│   ├── mountrix/
│   │   ├── __init__.py
│   │   ├── main.py                 # Entry Point
│   │   ├── core/                   # Backend-Logik
│   │   │   ├── __init__.py
│   │   │   ├── detector.py         # Desktop/Laufwerk-Erkennung
│   │   │   ├── mounter.py          # Mount-Logik
│   │   │   ├── fstab.py            # fstab-Management
│   │   │   ├── network.py          # Netzwerk-Diagnostik
│   │   │   ├── credentials.py      # Schlüssel/Passwort-Verwaltung
│   │   │   └── templates.py        # NAS-Templates
│   │   ├── gui/
│   │   │   ├── __init__.py
│   │   │   ├── qt/                 # PyQt6 GUI
│   │   │   │   ├── main_window.py
│   │   │   │   ├── wizard.py       # Assistent
│   │   │   │   ├── advanced.py     # Power-User-Modus
│   │   │   │   └── dialogs.py
│   │   │   └── gtk/                # GTK4 GUI
│   │   │       ├── main_window.py
│   │   │       ├── wizard.py
│   │   │       ├── advanced.py
│   │   │       └── dialogs.py
│   │   └── utils/
│   │       ├── logger.py           # Logging
│   │       ├── config.py           # Konfiguration
│   │       └── backup.py           # Backup/Rollback
├── gui/                            # UI-Design-Dateien
│   ├── qt/
│   │   └── *.ui                    # Qt Designer Dateien
│   └── gtk/
│       └── *.ui                    # Glade Dateien
├── locale/                         # Übersetzungen
│   ├── de/
│   │   └── LC_MESSAGES/
│   │       └── mountrix.po
│   └── en/
│       └── LC_MESSAGES/
│           └── mountrix.po
├── data/
│   ├── icons/                      # Logo & Icons
│   ├── nas_templates.json          # NAS-Konfigurationen
│   └── mountrix.desktop            # Desktop Entry
├── scripts/
│   ├── mountrix-pkexec-helper      # PolicyKit Helper-Script
│   └── build/                      # Build-Skripte
│       ├── build_deb.sh
│       ├── build_snap.sh
│       └── build_flatpak.sh
├── tests/
│   ├── test_detector.py
│   ├── test_mounter.py
│   ├── test_fstab.py
│   └── test_network.py
├── docs/
│   ├── Benutzerhandbuch.md
│   ├── API.md
│   └── screenshots/
├── setup.py
├── pyproject.toml
├── requirements.txt
├── LICENSE (GPLv3)
└── README.md
```

---

## 2. Implementierung in Phasen

### Phase 1: Projekt-Setup & Core-Backend (Woche 1-2)

#### 1.1 Repository & Grundstruktur
- [ ] GitHub-Repository erstellen (GPLv3 Lizenz)
- [ ] Projektstruktur anlegen
- [ ] Git-Workflow einrichten (.gitignore, README.md)
- [ ] Virtual Environment Setup dokumentieren

#### 1.2 Core-Module entwickeln

**a) detector.py - Desktop & Laufwerk-Erkennung**
```python
Funktionen:
- detect_desktop_environment() -> str  # GNOME, KDE, XFCE, etc.
- detect_local_drives() -> List[Drive]  # SATA, NVMe erkennen
- scan_network_shares() -> List[Share]  # NFS/SMB scannen
  - Nutze: avahi-browse, smbtree, nmap (optional)
- get_filesystem_type(device: str) -> str  # ext4, NTFS, exFAT, etc.
```

**b) network.py - Netzwerk-Diagnostik**
```python
Funktionen:
- ping_host(host: str) -> bool
- check_port(host: str, port: int) -> bool  # Port 445 für SMB, 2049 für NFS
- resolve_hostname(hostname: str) -> str  # IP-Auflösung
- test_mount_temporary(config: MountConfig) -> (bool, str)  # Temporärer Test
```

**c) credentials.py - Authentifizierung**
```python
Funktionen:
- save_credentials(service: str, username: str, password: str)
  - Nutze: python-keyring (GNOME Keyring / KWallet)
- load_credentials(service: str) -> (str, str)
- generate_credentials_file(username: str, password: str) -> str
  - Erstellt ~/.mountrix/credentials/<hash>.cred mit chmod 600
- validate_ssh_key(key_path: str) -> bool
```

**d) fstab.py - fstab-Management**
```python
Funktionen:
- parse_fstab() -> List[FstabEntry]
- backup_fstab() -> str  # Backup nach /var/backups/fstab.backup.<timestamp>
- add_entry(entry: FstabEntry) -> bool
- remove_entry(uuid: str) -> bool
- validate_entry(entry: FstabEntry) -> (bool, str)
- preview_changes(entry: FstabEntry) -> str  # Zeigt Diff

Klasse FstabEntry:
- source: str  # //nas/share oder UUID=...
- mountpoint: str
- fstype: str  # nfs, cifs, ext4, ntfs
- options: List[str]  # defaults, nofail, credentials=..., uid=..., gid=...
- dump: int
- pass_num: int
```

**e) mounter.py - Mount-Logik**
```python
Funktionen:
- create_mountpoint(path: str, user_only: bool)
  - /media/<username> für user_only=True
  - /mnt/<name> für user_only=False
- mount_entry(entry: FstabEntry) -> (bool, str)
- unmount_entry(mountpoint: str) -> (bool, str)
- verify_mount(mountpoint: str) -> bool
```

**f) templates.py - NAS-Templates**
```python
Templates in data/nas_templates.json:
{
  "fritznas": {
    "name": "AVM FRITZ!NAS",
    "protocol": "cifs",
    "default_port": 445,
    "default_options": ["vers=3.0", "nofail", "noauto"],
    "auth_method": "credentials",
    "help_url": "https://..."
  },
  "synology": { ... },
  "qnap": { ... },
  "wd_mycloud": { ... },
  "ugreen": { ... }
}

Funktionen:
- load_templates() -> Dict[str, Template]
- get_template(name: str) -> Template
- apply_template(template: Template, user_input: dict) -> FstabEntry
```

#### 1.3 PolicyKit-Integration
- [ ] PolicyKit-Policy erstellen (`/usr/share/polkit-1/actions/org.mountrix.policy`)
- [ ] Helper-Script für pkexec schreiben
- [ ] Test: Root-Operationen ohne sudo-Passwort

---

### Phase 2: GUI-Entwicklung (Woche 3-5)

#### 2.1 PyQt6 GUI (Priorität)

**a) main_window.py - Hauptfenster**
```python
Features:
- Menüleiste: Datei, Bearbeiten, Ansicht, Hilfe
- Toolbar: Neu, Bearbeiten, Löschen, Aktualisieren
- Liste existierender Mounts (TreeView)
  - Spalten: Name, Typ, Quelle, Mountpoint, Status
- Status-Bar mit Verbindungsinfo
- Dark Mode Toggle
```

**b) wizard.py - Schritt-für-Schritt-Assistent**
```python
Schritte:
1. Modus wählen: Netzlaufwerk (NFS/SMB) oder Lokales Laufwerk
2. [Netzwerk] NAS-Template wählen oder Manuell
3. [Netzwerk] Netzwerk scannen oder IP/Hostname eingeben
4. [Lokal] Laufwerk aus Liste wählen
5. Authentifizierung (Schlüsseldatei / Credentials / Keine)
6. Mount-Optionen:
   - Nur für mich (/media/<user>) oder Alle User (/mnt)
   - Mount-Name vergeben
   - Erweiterte Optionen (optional)
7. Verbindungstest
8. Vorschau der fstab-Änderung
9. Bestätigung & Ausführung
```

**c) advanced.py - Power-User-Modus**
```python
Features:
- Direkte Eingabe aller fstab-Parameter
- Syntax-Highlighting für fstab-Optionen
- Validierung in Echtzeit
- Dropdown für häufige Optionen
```

**d) dialogs.py - Dialoge**
```python
- ConfirmationDialog: fstab-Änderung bestätigen
- ErrorDialog: Fehler anzeigen mit Log-Details
- ProgressDialog: Mount-Vorgang mit Fortschritt
- RollbackDialog: Rollback anbieten bei Fehler
- SettingsDialog: App-Einstellungen (Sprache, Theme, Log-Level)
```

#### 2.2 GTK4 GUI (falls GNOME/XFCE erkannt)
- [ ] Gleiche Features wie PyQt6, aber mit GTK4/Adwaita
- [ ] Glade-UI-Dateien erstellen

#### 2.3 Desktop-Erkennung & Framework-Loading
```python
# main.py
def main():
    desktop = detect_desktop_environment()

    if desktop in ['KDE', 'LXQT']:
        from mountrix.gui.qt import MainWindow
        app = QApplication(sys.argv)
    elif desktop in ['GNOME', 'XFCE', 'CINNAMON']:
        from mountrix.gui.gtk import MainWindow
        app = Gtk.Application()
    else:
        # Fallback zu PyQt6
        from mountrix.gui.qt import MainWindow
        app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
```

---

### Phase 3: Features & Integration (Woche 6-7)

#### 3.1 Logging & Benachrichtigungen
```python
# utils/logger.py
- Log nach /var/log/mountrix.log (falls Root) oder ~/.local/share/mountrix/mountrix.log
- Log-Levels: DEBUG, INFO, WARNING, ERROR
- Rotation bei 10MB

# Desktop-Notifications
- notify-send für Erfolg/Fehler
- In-App Notification-Center für Log-Historie
```

#### 3.2 Rollback-Funktion
```python
# utils/backup.py
Funktionen:
- create_backup() -> str  # Vor jeder Änderung
- list_backups() -> List[Backup]
- restore_backup(backup_id: str) -> bool
- auto_rollback_on_failure()  # Automatisch bei Mount-Fehler
```

#### 3.3 Konfigurationsdatei
```ini
# ~/.config/mountrix/config.ini
[General]
language = de
theme = auto  # auto, light, dark
log_level = INFO
default_mode = wizard  # wizard, advanced

[Defaults]
network_scan_timeout = 30
mount_test_enabled = true
backup_count = 5
```

#### 3.4 Mehrsprachigkeit
- [ ] gettext-Setup für Deutsch und Englisch
- [ ] Alle GUI-Strings übersetzbar machen
- [ ] Sprachdateien generieren

---

### Phase 4: Testing (Woche 8)

#### 4.1 Unit-Tests
```python
# tests/test_fstab.py
- Test: fstab parsen
- Test: Backup erstellen/wiederherstellen
- Test: Entry validieren
- Test: Eintrag hinzufügen/entfernen

# tests/test_network.py
- Test: Ping (mit Mock)
- Test: Port-Check
- Test: Hostname-Auflösung

# tests/test_detector.py
- Test: Desktop-Erkennung
- Test: Laufwerk-Scan
```

#### 4.2 Integration-Tests
- [ ] Mock-fstab für Tests erstellen
- [ ] Test mit verschiedenen Desktop-Umgebungen (VM)
- [ ] Test mit echten NAS-Geräten (FritzNAS, QNAP)

#### 4.3 Beta-Testing
- [ ] Beta-Version an 5-10 unerfahrene Nutzer
- [ ] Feedback-Formular
- [ ] Bugs dokumentieren und fixen

---

### Phase 5: Paketierung & Veröffentlichung (Woche 9-10)

#### 5.1 .deb-Paket (Debian/Ubuntu/Mint)
```bash
# scripts/build/build_deb.sh
- debian/control erstellen
- debian/rules erstellen
- PolicyKit-Policy installieren
- Desktop-Entry installieren
- dpkg-buildpackage ausführen
```

**Paket-Struktur:**
```
/usr/bin/mountrix                          # Entry Point
/usr/lib/python3/dist-packages/mountrix/   # Python-Module
/usr/share/applications/mountrix.desktop   # Desktop Entry
/usr/share/icons/hicolor/*/mountrix.png    # Icons
/usr/share/polkit-1/actions/org.mountrix.policy
/usr/share/locale/de/LC_MESSAGES/mountrix.mo
/usr/share/doc/mountrix/                   # Dokumentation
```

#### 5.2 Snap-Paket
```yaml
# snapcraft.yaml
name: mountrix
version: '1.0.0'
summary: Einfaches Mounten von Netzlaufwerken
confinement: classic  # Wegen /etc/fstab Zugriff
apps:
  mountrix:
    command: bin/mountrix
    plugs: [network, mount-observe, system-files]
```

#### 5.3 Flatpak (später)
- [ ] Flatpak-Manifest erstellen
- [ ] Auf Flathub veröffentlichen

#### 5.4 GitHub-Release
- [ ] Release-Notes schreiben
- [ ] Vorkompilierte Pakete hochladen (.deb, .snap)
- [ ] README mit Installation und Screenshots

---

## 3. Dependencies

### 3.1 Python-Pakete (requirements.txt)
```txt
# GUI
PyQt6>=6.6.0
PyQt6-Qt6>=6.6.0

# GTK (optional)
PyGObject>=3.42.0

# Netzwerk & SMB
smbprotocol>=1.10.0
pysmb>=1.2.9

# Authentifizierung
keyring>=23.0.0
secretstorage>=3.3.0
cryptography>=41.0.0

# System
psutil>=5.9.0
netifaces>=0.11.0

# Utils
python-dotenv>=1.0.0
configparser>=6.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-qt>=4.2.0
```

### 3.2 System-Dependencies (apt)
```bash
# Basis
python3.10
python3-pip

# GUI
python3-pyqt6
python3-gi
gir1.2-gtk-4.0

# Netzwerk-Tools
nfs-common
cifs-utils
avahi-utils  # avahi-browse
smbclient    # smbtree

# PolicyKit
policykit-1

# Optional für Netzwerk-Scan
nmap
```

---

## 4. Logo & Branding

### 4.1 Logo-Design
- **Konzept**: Stilisiertes "M" mit Mount-Symbol (Berg-Icon + Netzwerk-Verbindung)
- **Farben**:
  - Primär: `#3498db` (Blau - Vertrauen)
  - Akzent: `#2ecc71` (Grün - Erfolg)
  - Dark Mode: `#bb86fc` (Lila)
- **Formate**: SVG, PNG (16x16, 32x32, 64x64, 128x128, 256x256)

### 4.2 Icon-Set
- Laufwerk-Icons (lokal, NFS, SMB)
- Status-Icons (verbunden, getrennt, Fehler)
- Action-Icons (hinzufügen, entfernen, bearbeiten)

---

## 5. Sicherheit

### 5.1 Sicherheits-Checks
- [ ] Validierung aller User-Eingaben (Path Traversal verhindern)
- [ ] Credentials nur mit chmod 600 speichern
- [ ] fstab-Backup vor jeder Änderung
- [ ] Bestätigungsdialog für kritische Aktionen
- [ ] Keine Root-Shell, nur einzelne Operationen via pkexec

### 5.2 Logging
- [ ] Alle Root-Operationen loggen
- [ ] Keine Passwörter in Logs
- [ ] Log-Rotation implementieren

---

## 6. Dokumentation

### 6.1 Benutzerhandbuch (docs/Benutzerhandbuch.md)
- Installation (alle Paketformate)
- Schnellstart-Guide
- Schritt-für-Schritt-Anleitungen:
  - NAS einbinden (mit Screenshots)
  - Lokales Laufwerk einbinden
  - FritzNAS-spezifisch
- Fehlerbehebung
- FAQ

### 6.2 Entwickler-Dokumentation (docs/API.md)
- Architektur-Übersicht
- API-Referenz für Core-Module
- Beitragen (Contributing Guide)
- Code-Style (PEP 8)

---

## 7. Roadmap nach v1.0

### Version 1.1
- [ ] CLI-Interface (mountrix-cli)
- [ ] Mount-Gruppen / Profile
- [ ] Import/Export von Konfigurationen

### Version 1.2
- [ ] WebDAV-Unterstützung
- [ ] SSHFS-Unterstützung
- [ ] systemd automount Option

### Version 2.0
- [ ] Sync-Funktion (rsync-Integration)
- [ ] Scheduled Mounts (Zeitplan)
- [ ] Remote-Management (Web-Interface)

---

## 8. Zeitplan & Meilensteine

| Phase | Dauer | Meilenstein |
|-------|-------|-------------|
| 1. Core-Backend | 2 Wochen | Funktionierender Backend ohne GUI |
| 2. GUI PyQt6 | 3 Wochen | Vollständige PyQt6-GUI mit Assistent |
| 3. Features | 2 Wochen | Logging, Rollback, i18n fertig |
| 4. Testing | 1 Woche | Alle Tests grün, Beta-Feedback |
| 5. Paketierung | 2 Wochen | .deb und Snap verfügbar |
| **Total** | **10 Wochen** | **v1.0 Release** |

---

## 9. Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| PolicyKit-Integration komplex | Mittel | Hoch | Früh testen, Fallback auf sudo |
| NAS-Templates unvollständig | Mittel | Mittel | Community-Feedback einholen |
| GUI-Framework-Detektion fehlerhaft | Niedrig | Mittel | Fallback zu PyQt6 |
| fstab-Fehler führt zu Unbootable System | Niedrig | Sehr Hoch | Backup + Rollback + nofail-Option |

---

## 10. Erfolgskriterien

### Technisch
- [x] Automatische Desktop-Erkennung funktioniert
- [x] fstab-Einträge werden korrekt erstellt
- [x] PolicyKit-Integration ohne Passwort-Eingabe
- [x] Rollback bei Fehler funktioniert
- [x] 80%+ Test-Coverage

### Benutzererfahrung
- [x] Unerfahrene Nutzer können NAS in < 3 Minuten einbinden
- [x] Power-User haben volle Kontrolle
- [x] Fehler werden verständlich erklärt
- [x] Dark Mode funktioniert

### Veröffentlichung
- [x] Paket in Debian/Ubuntu installierbar
- [x] Dokumentation vollständig
- [x] 10+ Beta-Tester zufrieden

---

## Nächste Schritte

1. ✅ Implementierungsplan abgestimmt
2. 🔲 Repository auf GitHub erstellen
3. 🔲 Projektstruktur anlegen
4. 🔲 Phase 1 starten: Core-Backend entwickeln
