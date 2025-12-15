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
- 🔄 **Phase 1: Core-Backend entwickeln** (in Arbeit)
  - ✅ detector.py - Desktop & Laufwerk-Erkennung (17 Tests, 84% Coverage)
  - ✅ fstab.py - fstab-Management (23 Tests, 83% Coverage)
  - ✅ templates.py - NAS-Template-Management (23 Tests, 77% Coverage)
  - ✅ network.py - Netzwerk-Diagnostik (38 Tests, 90% Coverage)
  - ✅ mounter.py - Mount-Logik (37 Tests, 86% Coverage)
  - 🔲 credentials.py - Authentifizierung
- 🔲 Phase 2: GUI entwickeln
- 🔲 Phase 3: Features integrieren
- 🔲 Phase 4: Testing
- 🔲 Phase 5: Paketierung & Release

### Letzte Änderungen (2025-12-15)
- **mounter.py vollständig implementiert** mit folgenden Funktionen:
  - `create_mountpoint()` - Erstellt Mountpoints (/media/<user> oder /mnt)
  - `mount_entry()` - Mountet fstab-Einträge
  - `unmount_entry()` - Unmountet Dateisysteme (mit force-Option)
  - `verify_mount()` - Prüft Mount-Status via /proc/mounts
  - `get_mount_info()` - Liefert detaillierte Mount-Informationen
  - `remount_entry()` - Unmount + Mount in einem Schritt
  - `get_current_username()` - Ermittelt aktuellen Benutzer
- **37 Unit-Tests** für mounter.py mit 86% Code-Coverage
- **network.py vollständig implementiert** (38 Tests, 90% Coverage)
- Alle Tests bestehen ✅

## Hinweise für Claude
- Alle Ausgaben im Terminal auf **Deutsch**
- Bei Script-Updates nicht jede Änderung nachfragen
- Diese claude.md automatisch fortführen bei Projekt-Fortschritt
- Code-Style: PEP 8, Type Hints verwenden
- Kommentare auf Englisch im Code, Dokumentation auf Deutsch
