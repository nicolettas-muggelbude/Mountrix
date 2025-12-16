# -*- coding: utf-8 -*-
"""
Main window for Mountrix PyQt6 GUI.

Provides the main user interface with:
- Menu bar (File, Edit, View, Help)
- Toolbar (New, Edit, Delete, Refresh)
- Mount list (TreeView)
- Status bar
"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...core.detector import detect_desktop_environment
from ...core.fstab import parse_fstab
from ...core.mounter import verify_mount


class MountrixMainWindow(QMainWindow):
    """Main window for Mountrix application."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("Mountrix - Mount Manager")
        self.setMinimumSize(900, 600)

        # Initialize UI components
        self._create_menu_bar()
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()

        # Load initial data
        self.refresh_mount_list()

    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&Datei")

        new_action = QAction("&Neu...", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Neuen Mount erstellen")
        new_action.triggered.connect(self.on_new_mount)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        refresh_action = QAction("&Aktualisieren", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Mount-Liste aktualisieren")
        refresh_action.triggered.connect(self.refresh_mount_list)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Programm beenden")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Bearbeiten")

        edit_action = QAction("&Bearbeiten", self)
        edit_action.setShortcut("Ctrl+E")
        edit_action.setStatusTip("Ausgewählten Mount bearbeiten")
        edit_action.triggered.connect(self.on_edit_mount)
        edit_menu.addAction(edit_action)

        delete_action = QAction("&Löschen", self)
        delete_action.setShortcut("Delete")
        delete_action.setStatusTip("Ausgewählten Mount löschen")
        delete_action.triggered.connect(self.on_delete_mount)
        edit_menu.addAction(delete_action)

        edit_menu.addSeparator()

        settings_action = QAction("&Einstellungen", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("Programm-Einstellungen")
        settings_action.triggered.connect(self.on_settings)
        edit_menu.addAction(settings_action)

        # View Menu
        view_menu = menubar.addMenu("&Ansicht")

        dark_mode_action = QAction("&Dark Mode", self)
        dark_mode_action.setCheckable(True)
        dark_mode_action.setStatusTip("Dark Mode aktivieren/deaktivieren")
        dark_mode_action.triggered.connect(self.on_toggle_dark_mode)
        view_menu.addAction(dark_mode_action)

        # Help Menu
        help_menu = menubar.addMenu("&Hilfe")

        about_action = QAction("Über &Mountrix", self)
        about_action.setStatusTip("Über Mountrix")
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

        help_action = QAction("&Hilfe", self)
        help_action.setShortcut("F1")
        help_action.setStatusTip("Hilfe anzeigen")
        help_action.triggered.connect(self.on_help)
        help_menu.addAction(help_action)

    def _create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar("Hauptwerkzeugleiste")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New Mount
        new_button = QAction("Neu", self)
        new_button.setStatusTip("Neuen Mount erstellen")
        new_button.triggered.connect(self.on_new_mount)
        toolbar.addAction(new_button)

        toolbar.addSeparator()

        # Edit Mount
        edit_button = QAction("Bearbeiten", self)
        edit_button.setStatusTip("Ausgewählten Mount bearbeiten")
        edit_button.triggered.connect(self.on_edit_mount)
        toolbar.addAction(edit_button)

        # Delete Mount
        delete_button = QAction("Löschen", self)
        delete_button.setStatusTip("Ausgewählten Mount löschen")
        delete_button.triggered.connect(self.on_delete_mount)
        toolbar.addAction(delete_button)

        toolbar.addSeparator()

        # Refresh
        refresh_button = QAction("Aktualisieren", self)
        refresh_button.setStatusTip("Mount-Liste aktualisieren")
        refresh_button.triggered.connect(self.refresh_mount_list)
        toolbar.addAction(refresh_button)

    def _create_central_widget(self):
        """Create the central widget with mount list."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Mount list (TreeView)
        self.mount_tree = QTreeWidget()
        self.mount_tree.setHeaderLabels(
            ["Name", "Typ", "Quelle", "Mountpoint", "Status"]
        )
        self.mount_tree.setAlternatingRowColors(True)
        self.mount_tree.setSortingEnabled(True)
        self.mount_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)

        # Set column widths
        header = self.mount_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Connect double-click to edit
        self.mount_tree.itemDoubleClicked.connect(self.on_edit_mount)

        layout.addWidget(self.mount_tree)

        # Button row
        button_layout = QHBoxLayout()

        wizard_button = QPushButton("Assistent-Modus")
        wizard_button.setStatusTip("Neuen Mount mit Assistent erstellen")
        wizard_button.clicked.connect(self.on_wizard_mode)
        button_layout.addWidget(wizard_button)

        advanced_button = QPushButton("Power-User-Modus")
        advanced_button.setStatusTip("Erweiterte Mount-Konfiguration")
        advanced_button.clicked.connect(self.on_advanced_mode)
        button_layout.addWidget(advanced_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Bereit")

    def refresh_mount_list(self):
        """Refresh the mount list from fstab."""
        self.mount_tree.clear()
        self.status_bar.showMessage("Lade Mount-Liste...")

        try:
            # Parse fstab
            entries = parse_fstab()

            # Filter for network and local mounts (exclude system mounts)
            relevant_entries = [
                e
                for e in entries
                if e.fstype in ("nfs", "nfs4", "cifs", "smb", "ext4", "ntfs", "exfat")
                and not e.mountpoint.startswith(("/sys", "/proc", "/dev"))
                and e.mountpoint not in ("/", "/boot", "/home")
            ]

            # Add to tree
            for entry in relevant_entries:
                # Determine mount name from mountpoint
                name = entry.mountpoint.split("/")[-1] or entry.mountpoint

                # Check if mounted
                is_mounted = verify_mount(entry.mountpoint)
                status = "Gemountet" if is_mounted else "Nicht gemountet"

                # Create tree item
                item = QTreeWidgetItem(
                    [
                        name,
                        entry.fstype.upper(),
                        entry.source,
                        entry.mountpoint,
                        status,
                    ]
                )

                # Color-code status
                if is_mounted:
                    item.setForeground(4, Qt.GlobalColor.darkGreen)
                else:
                    item.setForeground(4, Qt.GlobalColor.red)

                self.mount_tree.addTopLevelItem(item)

            count = len(relevant_entries)
            mounted_count = sum(
                1 for e in relevant_entries if verify_mount(e.mountpoint)
            )
            self.status_bar.showMessage(
                f"{count} Mounts gefunden ({mounted_count} gemountet)"
            )

        except FileNotFoundError:
            QMessageBox.warning(
                self, "Fehler", "Konnte /etc/fstab nicht lesen. Root-Rechte erforderlich?"
            )
            self.status_bar.showMessage("Fehler beim Laden der fstab")
        except Exception as e:
            QMessageBox.critical(
                self, "Fehler", f"Fehler beim Laden der Mount-Liste:\n{str(e)}"
            )
            self.status_bar.showMessage("Fehler")

    def on_new_mount(self):
        """Handle new mount action."""
        # TODO: Show wizard or advanced dialog
        QMessageBox.information(
            self,
            "Neuer Mount",
            "Assistent-Modus oder Power-User-Modus?\n\n"
            "Verwenden Sie die Buttons unten für den gewünschten Modus.",
        )

    def on_edit_mount(self):
        """Handle edit mount action."""
        selected_items = self.mount_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Keine Auswahl", "Bitte wähle einen Mount zum Bearbeiten aus."
            )
            return

        item = selected_items[0]
        mountpoint = item.text(3)

        # TODO: Open edit dialog
        QMessageBox.information(
            self, "Mount bearbeiten", f"Bearbeiten: {mountpoint}\n\n(Noch nicht implementiert)"
        )

    def on_delete_mount(self):
        """Handle delete mount action."""
        selected_items = self.mount_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Keine Auswahl", "Bitte wähle einen Mount zum Löschen aus."
            )
            return

        item = selected_items[0]
        mountpoint = item.text(3)

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Mount löschen",
            f"Möchtest du den Mount wirklich löschen?\n\nMountpoint: {mountpoint}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Implement deletion
            QMessageBox.information(
                self, "Löschen", "Löschen-Funktion noch nicht implementiert."
            )

    def on_wizard_mode(self):
        """Open wizard mode for creating new mount."""
        # TODO: Open wizard dialog
        QMessageBox.information(
            self,
            "Assistent-Modus",
            "Der Assistent-Modus führt dich Schritt für Schritt durch "
            "die Erstellung eines neuen Mounts.\n\n"
            "(Noch nicht implementiert)",
        )

    def on_advanced_mode(self):
        """Open advanced mode for power users."""
        # TODO: Open advanced dialog
        QMessageBox.information(
            self,
            "Power-User-Modus",
            "Im Power-User-Modus kannst du alle fstab-Parameter "
            "direkt konfigurieren.\n\n"
            "(Noch nicht implementiert)",
        )

    def on_settings(self):
        """Open settings dialog."""
        # TODO: Open settings dialog
        QMessageBox.information(
            self, "Einstellungen", "Einstellungen-Dialog noch nicht implementiert."
        )

    def on_toggle_dark_mode(self, checked):
        """Toggle dark mode."""
        # TODO: Implement dark mode toggle
        if checked:
            self.status_bar.showMessage("Dark Mode aktiviert")
        else:
            self.status_bar.showMessage("Dark Mode deaktiviert")

    def on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "Über Mountrix",
            "<h2>Mountrix v1.0</h2>"
            "<p>Benutzerfreundliches Mounten von Netzlaufwerken und lokalen Laufwerken unter Linux</p>"
            "<p><b>Entwickelt mit:</b> Python, PyQt6</p>"
            "<p><b>Lizenz:</b> GNU GPL v3.0</p>"
            "<p><b>Desktop:</b> " + str(detect_desktop_environment().value) + "</p>"
            "<p>🤖 Generated with Claude Code</p>",
        )

    def on_help(self):
        """Show help dialog."""
        QMessageBox.information(
            self,
            "Hilfe",
            "<h3>Mountrix - Schnellstart</h3>"
            "<p><b>Neuen Mount erstellen:</b></p>"
            "<ul>"
            "<li><b>Assistent-Modus:</b> Für Anfänger - Schritt-für-Schritt-Anleitung</li>"
            "<li><b>Power-User-Modus:</b> Für Experten - Direkte fstab-Konfiguration</li>"
            "</ul>"
            "<p><b>Tastenkürzel:</b></p>"
            "<ul>"
            "<li>Strg+N: Neuer Mount</li>"
            "<li>F5: Aktualisieren</li>"
            "<li>Entf: Löschen</li>"
            "<li>F1: Diese Hilfe</li>"
            "</ul>",
        )


def main():
    """Run the application."""
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName("Mountrix")
    app.setOrganizationName("Mountrix")

    window = MountrixMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
