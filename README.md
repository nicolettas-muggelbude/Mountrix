# Mountrix

<div align="center">
  <img src="data/icons/mountrix-logo.svg" alt="Mountrix Logo" width="200"/>

  **Benutzerfreundliches Mounten von Netzlaufwerken und lokalen Laufwerken unter Linux**

  [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  ![Status](https://img.shields.io/badge/status-in%20development-yellow)
</div>

---

## 📖 Über Mountrix

Mountrix ist ein modernes GUI-Tool für Linux, das das Einbinden (Mounten) von Netzlaufwerken und lokalen Laufwerken vereinfacht. Es richtet sich sowohl an unerfahrene Nutzer als auch an Power-User, die volle Kontrolle über ihre Mount-Konfigurationen benötigen.

### Problem
Immer wieder treten in Linux-Foren Probleme beim Einbinden von NAS, FritzNAS oder externen Laufwerken auf. Die manuelle Bearbeitung der `/etc/fstab` ist fehleranfällig und für Einsteiger eine Hürde.

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
  - Lokale Laufwerke (ext4, NTFS, exFAT)

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
- **Home-User**: NAS und externe Festplatten unkompliziert einbinden
- **Power-User**: Volle Kontrolle mit erweiterten Optionen
- **Gamer & Content Creator**: Zusätzliche SSDs/HDDs einfach verfügbar machen

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
pytest tests/ -v --cov=src/mountrix
```

---

## 📚 Dokumentation

- [Benutzerhandbuch](docs/Benutzerhandbuch.md) (in Arbeit)
- [Implementierungsplan](IMPLEMENTIERUNGSPLAN.md)
- [API-Dokumentation](docs/API.md) (in Arbeit)
- [Contributing Guide](CONTRIBUTING.md) (in Arbeit)

---

## 🗺️ Roadmap

### v1.0 (Q2 2025)
- ✅ Projekt-Setup und Planung
- 🔲 Core-Backend (Detector, Mounter, fstab)
- 🔲 PyQt6 GUI mit Assistent
- 🔲 NAS-Templates
- 🔲 Paketierung (.deb, Snap)

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
