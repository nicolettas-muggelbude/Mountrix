Projekt Mountrix

Motivation: Immer wieder ist in Foren und Linux-Gruppen zu lesen das es Probleme mit dem Einbinden (Mounten) von NAS und Laufwerken gibt. 
Linux soll einfach für Nutzer sein. Die Nutzung von NAS und auch FritzNAS wird immer beliebter, nicht nur bei Power-User. Eine weitere SSD oder HDD ist bei Gamern und Foto/Video-Fans beliebt.

1. Projektvorbereitung

GitHub-Repository erstellen (Lizenz: GPLv3).
Projektstruktur festlegen:


/project
├── src/               # Quellcode
├── gui/               # GUI-Dateien (UI-Design)
├── locale/            # Sprachdateien (de, en, ...)
├── scripts/           # Installationsskripte
├── tests/             # Testfälle
└── docs/              # Dokumentation


Abhängigkeiten definieren:

Python 3.8+
PyQt6 oder PyGObject (je nach Desktop-Umgebung)
python3-nfs, python3-smbprotocol (für NFS/SMB)
python3-pycryptodome (für Schlüsseldateien)


2. GUI-Entwicklung

Logo & Branding

Logo-Idee: Ein stilisiertes "M" mit integriertem Netzwerk- oder Laufwerksymbol (z. B. ein abstraktes Mount-Punkt-Symbol).
Farben: Blau (Vertrauen, Technologie) + Grün (Erfolg, Verbindung) oder ein futuristisches Neon-Lila.

Automatische Erkennung der Desktop-Umgebung (GNOME/KDE/XFCE) und Auswahl der passenden GUI-Bibliothek (GTK/Qt).
Design-Prinzipien:

Assistentenmodus für unerfahrene Nutzer (Schritt-für-Schritt-Anleitung).
Power-User-Modus für manuelle Eingaben.
Darkmode-Unterstützung (automatisch oder manuell umschaltbar).
Mehrsprachigkeit (Deutsch als Standard, Englisch als Fallback, Sprachdateien für weitere Sprachen).

GUI-Tools:

Qt Designer (für PyQt) oder Glade (für GTK).


3. Kernfunktionalität
a) Netzlaufwerk-Erkennung, und interne Laufwerke

Automatische Suche nach SATA/NVMe-Laufwerken, NFS/SMB-Freigaben im lokalen Netzwerk (z. B. über nmap, avahi-browse oder smbtree).
Manuelle Eingabe für Power-User (IP/Hostname, Pfad, Protokoll).
b) Authentifizierung

Schlüsseldateien (SSH/NFS) bevorzugen.
Fallback auf Zugangsdaten (Benutzername/Passwort) mit sicherer Speicherung (z. B. keyring-Bibliothek).
c) Einbindung in /etc/fstab

Standardoptionen vorschlagen (z. B. defaults,noatime für NFS/SMB).
Manuelle Anpassung für Power-User.
Backup der /etc/fstab vor Änderungen mit Bestätigungsdialog.
d) Netzwerkdiagnose

Ping/Verbindungscheck vor der Einbindung.
Abfrage ob für alle User, oder nur für einen selbst einbinden. (Mointpoint media oder mnt)
Evt. temporärer Mounttest
Fehlermeldungen in der GUI anzeigen (z. B. "Laufwerk/Host nicht erreichbar").

4. Sicherheit

Bestätigungsdialog vor dem Schreiben in /etc/fstab.
Logging (Aktionen, Fehler) in /var/log/<toolname>.log.
Keine Positiv/Negativ-Liste, aber Hinweise auf sichere Nutzung (z. B. "Nur vertrauenswürdige Hosts einbinden").

5. Benachrichtigungen

Desktop-Benachrichtigungen bei Erfolg/Fehler (z. B. mit notify-send).
Fehlerprotokoll in der GUI einsehbar.

6. Verteilung

Paketformate:

.deb (für Debian/Ubuntu)
Snap (für alle Distributionen)
Flatpak (für alle Distributionen)

7. Update-Funktion

8. Dokumentation

Benutzerhandbuch (Markdown/PDF) für GUI und CLI.
Entwicklerdokumentation (Code-Kommentare, API-Beschreibung).

9. Testphase

Manuelle Tests auf Debian/Ubuntu mit verschiedenen Desktop-Umgebungen.
Automatisierte Tests (z. B. mit pytest für Python).
Beta-Test mit unerfahrenen Nutzern (Feedback einholen).

10. Veröffentlichung

GitHub-Releases mit vorcompilierten Paketen.
Anleitung zur Installation im Repository.

11. Roadmap für zukünftige Features

Unterstützung für weitere Protokolle (WebDAV, SSHFS, sftp).
Whitelist/Blacklist-Funktion (optional, mit neutraler Terminologie).
Integration in Systemdienste für automatische Einbindung beim Start.
