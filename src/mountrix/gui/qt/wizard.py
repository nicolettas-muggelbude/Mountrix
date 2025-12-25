# -*- coding: utf-8 -*-
"""
Mount creation wizard for Mountrix.

Step-by-step assistant for creating new mounts.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWizard,
    QWizardPage,
    QListWidget,
)

from ...core.templates import load_templates
from ...core.network import ping_host, check_port, diagnose_connection
from ...core.detector import detect_local_drives
from .dialogs import setup_combobox_auto_close


class MountWizard(QWizard):
    """Wizard for creating new mounts step by step."""

    # Page IDs
    PAGE_MODE = 0
    PAGE_TEMPLATE = 1
    PAGE_NETWORK = 2
    PAGE_LOCAL_DRIVE = 3
    PAGE_AUTH = 4
    PAGE_OPTIONS = 5
    PAGE_TEST = 6
    PAGE_PREVIEW = 7
    PAGE_CONFIRM = 8

    def __init__(self, parent=None):
        """Initialize the wizard."""
        super().__init__(parent)

        self.setWindowTitle("Mountrix - Neuer Mount Assistent")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(700, 500)

        # Add pages
        self.setPage(self.PAGE_MODE, ModePage())
        self.setPage(self.PAGE_TEMPLATE, TemplatePage())
        self.setPage(self.PAGE_NETWORK, NetworkPage())
        self.setPage(self.PAGE_LOCAL_DRIVE, LocalDrivePage())
        self.setPage(self.PAGE_AUTH, AuthenticationPage())
        self.setPage(self.PAGE_OPTIONS, MountOptionsPage())
        self.setPage(self.PAGE_TEST, ConnectionTestPage())
        self.setPage(self.PAGE_PREVIEW, PreviewPage())
        self.setPage(self.PAGE_CONFIRM, ConfirmPage())

        self.setStartId(self.PAGE_MODE)


class ModePage(QWizardPage):
    """Page 1: Choose mount mode (Network or Local)."""

    def __init__(self):
        """Initialize the mode selection page."""
        super().__init__()
        self.setTitle("Mount-Typ wählen")
        self.setSubTitle(
            "Wähle, ob du ein Netzlaufwerk oder ein lokales Laufwerk mounten möchtest."
        )

        layout = QVBoxLayout()

        # Network mount option
        self.network_radio = QRadioButton("Netzlaufwerk (NFS / SMB/CIFS)")
        self.network_radio.setChecked(True)
        network_desc = QLabel("  • NAS-Systeme (FRITZ!NAS, QNAP, Synology, etc.)\n"
                               "  • Windows-Freigaben\n"
                               "  • Linux NFS-Shares")
        network_desc.setStyleSheet("color: gray; margin-left: 20px;")

        # Local mount option
        self.local_radio = QRadioButton("Lokales Laufwerk")
        local_desc = QLabel("  • Interne Festplatten (SATA, NVMe)\n"
                            "  • Externe Laufwerke (USB, eSATA)\n"
                            "  • Unterstützte Dateisysteme: ext4, NTFS, exFAT")
        local_desc.setStyleSheet("color: gray; margin-left: 20px;")

        layout.addWidget(self.network_radio)
        layout.addWidget(network_desc)
        layout.addSpacing(20)
        layout.addWidget(self.local_radio)
        layout.addWidget(local_desc)
        layout.addStretch()

        self.setLayout(layout)

        # Register fields
        self.registerField("mode.network", self.network_radio)
        self.registerField("mode.local", self.local_radio)

    def nextId(self):
        """Determine next page based on selection."""
        if self.network_radio.isChecked():
            return MountWizard.PAGE_TEMPLATE
        else:
            return MountWizard.PAGE_LOCAL_DRIVE


class TemplatePage(QWizardPage):
    """Page 2: Choose NAS template or manual configuration."""

    def __init__(self):
        """Initialize the template selection page."""
        super().__init__()
        self.setTitle("NAS-Template wählen")
        self.setSubTitle(
            "Wähle dein NAS-System für optimierte Einstellungen, "
            "oder konfiguriere manuell."
        )

        layout = QVBoxLayout()

        # Template selection
        template_group = QGroupBox("NAS-Template")
        template_layout = QVBoxLayout()

        self.template_combo = QComboBox()
        self.template_combo.setEditable(False)
        setup_combobox_auto_close(self.template_combo)
        self.template_combo.addItem("Manuell konfigurieren", "manual")

        # Load templates
        try:
            templates = load_templates()
            for template_id, template in templates.items():
                self.template_combo.addItem(
                    f"{template.name} ({template.protocol.upper()})",
                    template_id
                )
        except Exception:
            pass

        template_layout.addWidget(self.template_combo)

        # Template description
        self.template_desc = QLabel()
        self.template_desc.setWordWrap(True)
        self.template_desc.setStyleSheet("color: gray; margin-top: 10px;")
        template_layout.addWidget(self.template_desc)

        template_group.setLayout(template_layout)
        layout.addWidget(template_group)

        layout.addStretch()
        self.setLayout(layout)

        # Connect signals
        self.template_combo.currentIndexChanged.connect(self._update_description)
        self._update_description()

        # Register field
        self.registerField("template", self.template_combo)

    def _update_description(self):
        """Update template description."""
        template_id = self.template_combo.currentData()
        if template_id == "manual":
            self.template_desc.setText(
                "Du kannst alle Parameter manuell eingeben."
            )
        else:
            try:
                templates = load_templates()
                if template_id in templates:
                    t = templates[template_id]
                    self.template_desc.setText(
                        f"Protokoll: {t.protocol.upper()}\n"
                        f"Port: {t.default_port}\n"
                        f"Standard-Optionen: {', '.join(t.default_options)}"
                    )
            except Exception:
                self.template_desc.setText("")

    def nextId(self):
        """Go to network configuration page."""
        return MountWizard.PAGE_NETWORK


class NetworkPage(QWizardPage):
    """Page 3: Network configuration (IP/Hostname, Share path)."""

    def __init__(self):
        """Initialize the network configuration page."""
        super().__init__()
        self.setTitle("Netzwerk-Konfiguration")
        self.setSubTitle("Gib die Adresse und den Freigabepfad deines NAS ein.")

        layout = QVBoxLayout()

        # Host input
        host_group = QGroupBox("Server-Adresse")
        host_layout = QVBoxLayout()

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("z.B. 192.168.1.100 oder nas.local")
        host_layout.addWidget(QLabel("IP-Adresse oder Hostname:"))
        host_layout.addWidget(self.host_input)

        host_group.setLayout(host_layout)
        layout.addWidget(host_group)

        # Share path input
        share_group = QGroupBox("Freigabepfad")
        share_layout = QVBoxLayout()

        self.share_input = QLineEdit()
        self.share_input.setPlaceholderText("z.B. /data oder public")
        share_layout.addWidget(QLabel("Freigabename oder Pfad:"))
        share_layout.addWidget(self.share_input)

        share_group.setLayout(share_layout)
        layout.addWidget(share_group)

        # Protocol selection
        protocol_group = QGroupBox("Protokoll")
        protocol_layout = QHBoxLayout()

        self.protocol_combo = QComboBox()
        self.protocol_combo.setEditable(False)
        setup_combobox_auto_close(self.protocol_combo)
        self.protocol_combo.addItems(["SMB/CIFS (Windows, NAS)", "NFS (Linux, Unix)"])
        protocol_layout.addWidget(self.protocol_combo)

        protocol_group.setLayout(protocol_layout)
        layout.addWidget(protocol_group)

        layout.addStretch()
        self.setLayout(layout)

        # Register fields
        self.registerField("network.host*", self.host_input)
        self.registerField("network.share*", self.share_input)
        self.registerField("network.protocol", self.protocol_combo)

    def nextId(self):
        """Go to authentication page."""
        return MountWizard.PAGE_AUTH


class LocalDrivePage(QWizardPage):
    """Page 4: Local drive selection."""

    def __init__(self):
        """Initialize the local drive page."""
        super().__init__()
        self.setTitle("Laufwerk wählen")
        self.setSubTitle("Wähle das Laufwerk, das du mounten möchtest.")

        layout = QVBoxLayout()

        # Drive list
        self.drive_list = QListWidget()
        layout.addWidget(QLabel("Verfügbare Laufwerke:"))
        layout.addWidget(self.drive_list)

        # Refresh button
        refresh_btn = QPushButton("Aktualisieren")
        refresh_btn.clicked.connect(self._refresh_drives)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)

        # Initial load
        self._refresh_drives()

    def _refresh_drives(self):
        """Refresh the drive list."""
        self.drive_list.clear()
        try:
            drives = detect_local_drives()
            for drive in drives:
                label = f"{drive.name} ({drive.device}) - {drive.filesystem} - {drive.size_gb:.1f} GB"
                if drive.label:
                    label += f" [{drive.label}]"
                self.drive_list.addItem(label)
        except Exception as e:
            self.drive_list.addItem(f"Fehler: {str(e)}")

    def nextId(self):
        """Go to mount options page (skip auth for local drives)."""
        return MountWizard.PAGE_OPTIONS


class AuthenticationPage(QWizardPage):
    """Page 5: Authentication configuration."""

    def __init__(self):
        """Initialize the authentication page."""
        super().__init__()
        self.setTitle("Authentifizierung")
        self.setSubTitle("Gib die Anmeldedaten für den Zugriff ein (falls erforderlich).")

        layout = QVBoxLayout()

        # Auth method selection
        method_group = QGroupBox("Authentifizierungsmethode")
        method_layout = QVBoxLayout()

        self.auth_group = QButtonGroup()

        self.no_auth_radio = QRadioButton("Keine Authentifizierung (Gast-Zugriff)")
        self.no_auth_radio.setChecked(True)
        self.auth_group.addButton(self.no_auth_radio, 0)

        self.password_radio = QRadioButton("Benutzername & Passwort")
        self.auth_group.addButton(self.password_radio, 1)

        method_layout.addWidget(self.no_auth_radio)
        method_layout.addWidget(self.password_radio)
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)

        # Credentials input
        creds_group = QGroupBox("Anmeldedaten")
        creds_layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Benutzername")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Passwort")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        creds_layout.addWidget(QLabel("Benutzername:"))
        creds_layout.addWidget(self.username_input)
        creds_layout.addWidget(QLabel("Passwort:"))
        creds_layout.addWidget(self.password_input)

        # Save credentials checkbox
        self.save_creds_check = QCheckBox("Anmeldedaten im Keyring speichern")
        self.save_creds_check.setChecked(True)
        creds_layout.addWidget(self.save_creds_check)

        creds_group.setLayout(creds_layout)
        layout.addWidget(creds_group)

        layout.addStretch()
        self.setLayout(layout)

        # Enable/disable credentials based on auth method
        self.auth_group.buttonClicked.connect(self._update_creds_state)
        self._update_creds_state()

        # Register fields
        self.registerField("auth.username", self.username_input)
        self.registerField("auth.password", self.password_input)
        self.registerField("auth.save", self.save_creds_check)

    def _update_creds_state(self):
        """Enable/disable credential inputs based on auth method."""
        enabled = self.password_radio.isChecked()
        self.username_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self.save_creds_check.setEnabled(enabled)

    def nextId(self):
        """Go to mount options page."""
        return MountWizard.PAGE_OPTIONS


class MountOptionsPage(QWizardPage):
    """Page 6: Mount options configuration."""

    def __init__(self):
        """Initialize the mount options page."""
        super().__init__()
        self.setTitle("Mount-Optionen")
        self.setSubTitle("Konfiguriere, wie und wo das Laufwerk gemountet werden soll.")

        layout = QVBoxLayout()

        # Mount location
        location_group = QGroupBox("Mount-Speicherort")
        location_layout = QVBoxLayout()

        self.user_mount_radio = QRadioButton("Nur für mich (/media/<benutzer>)")
        self.user_mount_radio.setChecked(True)
        self.system_mount_radio = QRadioButton("Für alle Benutzer (/mnt)")

        location_layout.addWidget(self.user_mount_radio)
        location_layout.addWidget(self.system_mount_radio)
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)

        # Mount name
        name_group = QGroupBox("Mount-Name")
        name_layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("z.B. nas_daten oder externe_festplatte")
        name_layout.addWidget(QLabel("Verzeichnisname:"))
        name_layout.addWidget(self.name_input)
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)

        # Mount at boot
        self.mount_at_boot = QCheckBox("Beim Systemstart automatisch mounten")
        self.mount_at_boot.setChecked(True)
        layout.addWidget(self.mount_at_boot)

        # Fail-safe option
        self.nofail_option = QCheckBox(
            "Systemstart nicht blockieren, wenn Mount fehlschlägt (nofail)"
        )
        self.nofail_option.setChecked(True)
        layout.addWidget(self.nofail_option)

        layout.addStretch()
        self.setLayout(layout)

        # Register fields
        self.registerField("options.user_mount", self.user_mount_radio)
        self.registerField("options.name*", self.name_input)
        self.registerField("options.boot", self.mount_at_boot)
        self.registerField("options.nofail", self.nofail_option)

    def nextId(self):
        """Go to connection test page."""
        return MountWizard.PAGE_TEST


class ConnectionTestPage(QWizardPage):
    """Page 7: Test connection before creating mount."""

    def __init__(self):
        """Initialize the connection test page."""
        super().__init__()
        self.setTitle("Verbindungstest")
        self.setSubTitle("Teste die Verbindung vor dem Erstellen des Mounts.")

        layout = QVBoxLayout()

        # Test results
        self.test_output = QTextEdit()
        self.test_output.setReadOnly(True)
        layout.addWidget(self.test_output)

        # Test button
        test_btn = QPushButton("Verbindung testen")
        test_btn.clicked.connect(self._run_test)
        layout.addWidget(test_btn)

        self.setLayout(layout)

    def _run_test(self):
        """Run connection test."""
        self.test_output.clear()
        self.test_output.append("Verbindungstest läuft...\n")

        # Get wizard data
        wizard = self.wizard()
        is_network = wizard.field("mode.network")

        if not is_network:
            self.test_output.append("✓ Lokales Laufwerk - kein Netzwerktest erforderlich")
            return

        host = wizard.field("network.host")

        self.test_output.append(f"Teste Verbindung zu: {host}\n")

        # Ping test
        self.test_output.append("1. Ping-Test...")
        if ping_host(host):
            self.test_output.append("   ✓ Host ist erreichbar\n")
        else:
            self.test_output.append("   ✗ Host nicht erreichbar\n")
            return

        # Port test
        protocol_idx = wizard.field("network.protocol")
        port = 445 if protocol_idx == 0 else 2049  # SMB or NFS

        self.test_output.append(f"2. Port-Test (Port {port})...")
        if check_port(host, port):
            self.test_output.append("   ✓ Port ist offen\n")
        else:
            self.test_output.append("   ✗ Port ist geschlossen\n")

        self.test_output.append("\nVerbindungstest abgeschlossen.")

    def nextId(self):
        """Go to preview page."""
        return MountWizard.PAGE_PREVIEW


class PreviewPage(QWizardPage):
    """Page 8: Preview fstab entry."""

    def __init__(self):
        """Initialize the preview page."""
        super().__init__()
        self.setTitle("Vorschau")
        self.setSubTitle("Überprüfe die fstab-Konfiguration vor dem Erstellen.")

        layout = QVBoxLayout()

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFontFamily("Monospace")
        layout.addWidget(self.preview_text)

        self.setLayout(layout)

    def initializePage(self):
        """Update preview when page is shown."""
        wizard = self.wizard()

        # Build preview
        preview = "# Mountrix - Mount-Konfiguration\n\n"

        is_network = wizard.field("mode.network")

        if is_network:
            host = wizard.field("network.host")
            share = wizard.field("network.share")
            protocol_idx = wizard.field("network.protocol")
            protocol = "cifs" if protocol_idx == 0 else "nfs"

            if protocol == "cifs":
                source = f"//{host}/{share}"
            else:
                source = f"{host}:{share}"

            preview += f"Quelle: {source}\n"
            preview += f"Protokoll: {protocol}\n"
        else:
            preview += "Lokales Laufwerk\n"

        mount_name = wizard.field("options.name")
        user_mount = wizard.field("options.user_mount")

        if user_mount:
            mountpoint = f"/media/$USER/{mount_name}"
        else:
            mountpoint = f"/mnt/{mount_name}"

        preview += f"Mountpoint: {mountpoint}\n\n"
        preview += "Optionen:\n"

        if wizard.field("options.boot"):
            preview += "  - Beim Systemstart mounten\n"
        else:
            preview += "  - Nicht automatisch mounten (noauto)\n"

        if wizard.field("options.nofail"):
            preview += "  - Systemstart nicht blockieren (nofail)\n"

        self.preview_text.setPlainText(preview)

    def nextId(self):
        """Go to confirmation page."""
        return MountWizard.PAGE_CONFIRM


class ConfirmPage(QWizardPage):
    """Page 9: Final confirmation and execution."""

    def __init__(self):
        """Initialize the confirmation page."""
        super().__init__()
        self.setTitle("Bestätigung")
        self.setSubTitle("Klicke auf 'Fertig', um den Mount zu erstellen.")

        layout = QVBoxLayout()

        info = QLabel(
            "<b>Der Mount wird jetzt erstellt.</b><br><br>"
            "Folgende Schritte werden ausgeführt:<br>"
            "1. Backup der aktuellen fstab<br>"
            "2. Mountpoint erstellen<br>"
            "3. fstab-Eintrag hinzufügen<br>"
            "4. Mount testen<br><br>"
            "Möchtest du fortfahren?"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()
        self.setLayout(layout)

    def nextId(self):
        """This is the last page."""
        return -1


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    wizard = MountWizard()
    wizard.show()
    sys.exit(app.exec())
