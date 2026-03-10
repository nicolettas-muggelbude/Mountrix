# Mountrix

<div align="center">
  <img src="data/icons/mountrix-logo.svg" alt="Mountrix Logo" width="200"/>

  **Benutzerfreundliches Mounten von Netzlaufwerken und lokalen Laufwerken unter Linux**

  [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  ![Status](https://img.shields.io/badge/status-in%20development-yellow)
  ![Tests](https://img.shields.io/badge/tests-176%20passing-brightgreen)
  ![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)
</div>

---

## 📖 Über Mountrix

Mountrix ist ein modernes GUI-Tool für Linux, das das Einbinden (Mounten) von Netzlaufwerken und lokalen Laufwerken vereinfacht. Es richtet sich sowohl an unerfahrene Nutzer als auch an Power-User, die volle Kontrolle über ihre Mount-Konfigurationen benötigen.

### Problem
Immer wieder treten in Linux-Foren Probleme beim Einbinden von NAS, FritzNAS oder internen/externen Laufwerken auf. Die manuelle Bearbeitung der `/etc/fstab` ist fehleranfällig und für Einsteiger eine Hürde.

### Lösung
Mountrix bietet einen intuitiven Assistenten und automatische Konfiguration für gängige NAS-Systeme, ohne dass Nutzer die Kommandozeile bemühen müssen.

---

## ✨ Features

### v1.0 (In Entwicklung)

- **🎨 Adaptive GUI**: Automatische Erkennung der Desktop-Umgebung
  - PyQt6 für KDE, LXQt
  - GTK4 für GNOME, XFCE, Cinnamon

- **🔌 Protokoll-Unterstützung**:
  - SMB/CIFS (Windows-Shares, NAS)
  - NFS (Unix/Linux-Shares)
  - Interne Laufwerke (SATA, NVMe: ext4, NTFS, exFAT)
  - Externe Laufwerke (USB, eSATA: ext4, NTFS, exFAT)

- **🏢 NAS-Templates**:
  - AVM FRITZ!NAS
  - QNAP
  - Western Digital My Cloud
  - Synology DiskStation
  - UGREEN

- **👥 Zwei Benutzer-Modi**:
  - **Assistent**: Schritt-für-Schritt-Anleitung für Anfänger
  - **Power-User**: Direkte Kontrolle über alle fstab-Parameter

- **🔒 Sicherheit**:
  - PolicyKit-Integration (keine sudo-Passwort-Dialoge)
  - Automatisches Backup der `/etc/fstab`
  - Rollback-Funktion bei Fehlern
  - Sichere Credential-Speicherung (GNOME Keyring / KWallet)

- **🌐 Mehrsprachigkeit**: Deutsch, Englisch

- **🔍 Netzwerk-Diagnostik**:
  - Automatisches Scannen nach Netzwerk-Freigaben
  - Verbindungstest vor dem Mounten
  - Temporärer Mount-Test

---

## 🎯 Zielgruppen

- **Linux-Einsteiger**: Einfaches Mounten ohne Terminal-Kenntnisse
- **Home-User**: NAS und interne/externe Festplatten unkompliziert einbinden
- **Power-User**: Volle Kontrolle mit erweiterten Optionen
- **Gamer & Content Creator**: Zusätzliche interne SSDs/NVMe oder externe HDDs einfach verfügbar machen

---

## 🚀 Installation

> **Hinweis**: Mountrix befindet sich aktuell in Entwicklung. Erste Releases folgen in Kürze.

### Geplante Paketformate

```bash
# Debian/Ubuntu/Mint (.deb)
sudo apt install ./mountrix_1.0.0_amd64.deb

# Snap (universell)
sudo snap install mountrix

# Flatpak (später)
flatpak install mountrix
```

---

## 📋 Anforderungen

- **Betriebssystem**: Ubuntu 22.04+, Debian 11+, Linux Mint 20+
- **Python**: 3.10 oder höher
- **Desktop**: GNOME, KDE, XFCE, Cinnamon, LXQt

### System-Dependencies

```bash
sudo apt install \
  python3.10 \
  python3-pip \
  nfs-common \
  cifs-utils \
  policykit-1
```

---

## 🛠️ Entwicklung

### Setup (WSL/Linux)

```bash
# Repository klonen
git clone https://github.com/<username>/mountrix.git
cd mountrix

# Virtual Environment erstellen
python3.10 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Entwicklungsversion starten
python src/mountrix/main.py
```

### Icons generieren

```bash
# Benötigt inkscape oder imagemagick
sudo apt install inkscape

# PNG-Icons in verschiedenen Größen erstellen
./scripts/generate_icons.sh
```

### Tests ausführen

```bash
# Alle Tests ausführen
pytest tests/ -v

# Mit Coverage-Report
pytest tests/ -v --cov=src/mountrix --cov-report=term

# Aktueller Status: 176 Tests, 85% Coverage ✅
```

### Aktueller Entwicklungsstand

**Phase 1 - Core-Backend: ✅ ABGESCHLOSSEN**

| Modul | Funktionen | Tests | Coverage |
|-------|-----------|-------|----------|
| detector.py | Desktop & Laufwerk-Erkennung | 17 | 84% |
| fstab.py | fstab-Management & Backup | 23 | 83% |
| templates.py | NAS-Templates (FRITZ!NAS, QNAP, etc.) | 23 | 77% |
| network.py | Netzwerk-Diagnostik & Mount-Tests | 38 | 90% |
| mounter.py | Mount/Unmount-Operationen | 37 | 86% |
| credentials.py | Keyring & Credential-Management | 38 | 86% |
| **GESAMT** | **47 Funktionen** | **176** | **85%** |

**Phase 2 - GUI-Design: ✅ ABGESCHLOSSEN**

| Komponente | Beschreibung |
|-----------|-------------|
| main_window.py | Hauptfenster mit Hamburger-Menü, Dark Mode, TreeWidget |
| wizard.py | 9-seitiger Assistent (Typ, Template, Netzwerk, Auth, Optionen, Test, Preview) |
| advanced.py | Power-User-Modus mit fstab-Syntax-Highlighting |
| dialogs.py | Einstellungen, Fehler, Bestätigung, Progress |

**Phase 3 - GUI-Backend-Anbindung: ✅ ABGESCHLOSSEN**

| Feature | Beschreibung |
|--------|-------------|
| Wizard → fstab | Assistent schreibt fstab-Eintrag und mountet sofort |
| Advanced → fstab | Power-User-Dialog schreibt und mountet |
| Bearbeiten | AdvancedDialog im Edit-Modus, tauscht fstab-Eintrag aus |
| Löschen | Unmountet + entfernt aus fstab |
| Kontextmenü | Rechtsklick: Mount / Unmount / Bearbeiten / Löschen |

---

## 📚 Dokumentation

- [Benutzerhandbuch](docs/Benutzerhandbuch.md) (in Arbeit)
- [Implementierungsplan](IMPLEMENTIERUNGSPLAN.md)
- [API-Dokumentation](docs/API.md) (in Arbeit)
- [Contributing Guide](CONTRIBUTING.md) (in Arbeit)

---

## 🗺️ Roadmap

### v1.0 (Q1 2026)
- ✅ Projekt-Setup und Planung
- ✅ **Phase 1: Core-Backend komplett** (176 Tests, 85% Coverage)
  - ✅ Desktop & Laufwerk-Erkennung (detector.py)
  - ✅ fstab-Management (fstab.py)
  - ✅ NAS-Template-System (templates.py)
  - ✅ Netzwerk-Diagnostik (network.py)
  - ✅ Mount-Logik (mounter.py)
  - ✅ Credentials-Management (credentials.py)
- ✅ **Phase 2: GUI-Design komplett**
  - ✅ PyQt6 Hauptfenster mit Dark Mode & Hamburger-Menü
  - ✅ Assistent-Modus (9 Seiten)
  - ✅ Power-User-Modus mit Syntax-Highlighting
- ✅ **Phase 3: GUI-Backend-Anbindung komplett**
  - ✅ Wizard/Advanced → fstab schreiben + mounten
  - ✅ Bearbeiten, Löschen, Kontextmenü
- 🔲 Phase 4: sudo/pkexec-Integration, Credentials-Keyring, Tests
- 🔲 Phase 5: Paketierung (.deb, Snap)

### v1.1
- CLI-Interface
- Mount-Gruppen / Profile
- Konfigurations-Import/Export

### v1.2
- WebDAV-Unterstützung
- SSHFS
- systemd automount

### v2.0
- rsync-Integration
- Scheduled Mounts
- Web-Interface für Remote-Management

---

## 🤝 Beitragen

Beiträge sind willkommen! Ob Bug-Reports, Feature-Requests oder Pull Requests - jede Hilfe ist geschätzt.

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

---

## 📜 Lizenz

Dieses Projekt steht unter der [GNU General Public License v3.0](LICENSE).

---

## 👨‍💻 Autor

**Nicole** - [GitHub Profil](https://github.com/<username>)

---

## 🙏 Danksagungen

- Linux-Community für Feedback und Ideen
- Alle Beta-Tester
- Contributors

---

## 📞 Support & Kontakt

- **Issues**: [GitHub Issues](https://github.com/<username>/mountrix/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/<username>/mountrix/discussions)

---

<div align="center">
  Made with ❤️ for the Linux Community
</div>
