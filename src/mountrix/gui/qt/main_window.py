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
from PyQt6.QtGui import QAction, QIcon, QPalette, QColor
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

from ...core.detector import detect_desktop_environment, detect_system_theme
from ...core.fstab import parse_fstab
from ...core.mounter import verify_mount


def get_modern_stylesheet(theme: str = "light") -> str:
    """
    Get modern stylesheet with Mountrix logo colors.

    Logo Colors (from mountrix-logo.svg):
    - Primary Blue: #3498db (light) → #2980b9 (dark)
    - Accent Green: #2ecc71 (light) → #27ae60 (dark)

    Args:
        theme: Theme name ("light" or "dark")

    Returns:
        str: QSS stylesheet with modern, clean design
    """
    # Color scheme based on theme
    if theme == "dark":
        bg_primary = "#2c3e50"
        bg_secondary = "#34495e"
        bg_input = "#34495e"
        text_primary = "#ecf0f1"
        text_secondary = "#bdc3c7"
        border_color = "#7f8c8d"
        hover_bg = "#3d566e"
    else:  # light
        bg_primary = "white"
        bg_secondary = "#ecf0f1"
        bg_input = "white"
        text_primary = "#2c3e50"
        text_secondary = "#7f8c8d"
        border_color = "#bdc3c7"
        hover_bg = "#ecf0f1"

    return f"""
/* === BUTTONS === */
QPushButton {{
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 10pt;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: #5dade2;
}}

QPushButton:pressed {{
    background-color: #2980b9;
}}

QPushButton:disabled {{
    background-color: #bdc3c7;
    color: #7f8c8d;
}}

/* === INPUT FIELDS === */
QLineEdit {{
    background-color: {bg_input};
    border: 2px solid {border_color};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 10pt;
    color: {text_primary};
    selection-background-color: #3498db;
    selection-color: white;
}}

QLineEdit:focus {{
    border-color: #3498db;
}}

QLineEdit:disabled {{
    background-color: {bg_secondary};
    color: {text_secondary};
}}

QTextEdit, QPlainTextEdit {{
    background-color: {bg_input};
    border: 2px solid {border_color};
    border-radius: 4px;
    padding: 6px;
    font-size: 10pt;
    color: {text_primary};
    selection-background-color: #3498db;
    selection-color: white;
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: #3498db;
}}

/* === COMBOBOX === */
QComboBox {{
    background-color: {bg_input};
    border: 2px solid {border_color};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 10pt;
    color: {text_primary};
}}

QComboBox:hover {{
    border-color: #3498db;
}}

QComboBox:focus {{
    border-color: #3498db;
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {text_secondary};
    margin-right: 5px;
}}

QComboBox:on {{
    border-color: #3498db;
}}

QComboBox QAbstractItemView {{
    background-color: {bg_input};
    color: {text_primary};
    border: 1px solid {border_color};
    selection-background-color: #3498db;
    selection-color: white;
}}

/* === TREE WIDGET === */
QTreeWidget {{
    background-color: {bg_primary};
    border: 2px solid {border_color};
    border-radius: 4px;
    font-size: 10pt;
    color: {text_primary};
    alternate-background-color: {bg_secondary};
}}

QTreeWidget::item {{
    padding: 4px;
    color: {text_primary};
}}

QTreeWidget::item:selected {{
    background-color: #3498db;
    color: white;
}}

QTreeWidget::item:hover {{
    background-color: {hover_bg};
}}

QHeaderView::section {{
    background-color: {bg_secondary};
    color: {text_primary};
    padding: 6px;
    border: none;
    border-bottom: 2px solid {border_color};
    font-weight: bold;
}}

/* === CHECKBOX === */
QCheckBox {{
    spacing: 8px;
    font-size: 10pt;
    color: {text_primary};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {border_color};
    border-radius: 3px;
    background-color: {bg_input};
}}

QCheckBox::indicator:hover {{
    border-color: #3498db;
}}

QCheckBox::indicator:checked {{
    background-color: #2ecc71;
    border-color: #27ae60;
}}

QCheckBox::indicator:checked:hover {{
    background-color: #27ae60;
}}

/* === RADIOBUTTON === */
QRadioButton {{
    spacing: 8px;
    font-size: 10pt;
    color: {text_primary};
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {border_color};
    border-radius: 9px;
    background-color: {bg_input};
}}

QRadioButton::indicator:hover {{
    border-color: #3498db;
}}

QRadioButton::indicator:checked {{
    background-color: #3498db;
    border-color: #2980b9;
}}

/* === GROUPBOX === */
QGroupBox {{
    border: 2px solid {border_color};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
    font-size: 10pt;
    color: {text_primary};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: {text_primary};
}}

/* === MENU === */
QMenuBar {{
    background-color: {bg_secondary};
    border-bottom: 1px solid {border_color};
    font-size: 10pt;
    color: {text_primary};
}}

QMenuBar::item {{
    padding: 6px 12px;
    background-color: transparent;
    color: {text_primary};
}}

QMenuBar::item:selected {{
    background-color: #3498db;
    color: white;
}}

QMenuBar::item:pressed {{
    background-color: #2980b9;
    color: white;
}}

QMenu {{
    background-color: {bg_primary};
    border: 1px solid {border_color};
    font-size: 10pt;
    color: {text_primary};
}}

QMenu::item {{
    padding: 6px 30px 6px 20px;
    color: {text_primary};
}}

QMenu::item:selected {{
    background-color: #3498db;
    color: white;
}}

/* === TOOLBAR === */
QToolBar {{
    background-color: {bg_secondary};
    border-bottom: 1px solid {border_color};
    spacing: 6px;
    padding: 4px;
}}

QToolBar::separator {{
    background-color: {border_color};
    width: 1px;
    margin: 4px;
}}

/* === STATUSBAR === */
QStatusBar {{
    background-color: {bg_secondary};
    border-top: 1px solid {border_color};
    font-size: 9pt;
    color: {text_primary};
}}

/* === SCROLLBAR === */
QScrollBar:vertical {{
    border: none;
    background-color: {bg_secondary};
    width: 12px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {border_color};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {text_secondary};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    border: none;
    background-color: {bg_secondary};
    height: 12px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {border_color};
    border-radius: 6px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {text_secondary};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* === PROGRESS BAR === */
QProgressBar {{
    border: 2px solid {border_color};
    border-radius: 4px;
    text-align: center;
    font-size: 10pt;
    background-color: {bg_input};
    color: {text_primary};
}}

QProgressBar::chunk {{
    background-color: #3498db;
    border-radius: 2px;
}}
"""


def create_dark_palette() -> QPalette:
    """
    Create a dark color palette for the application.

    Returns:
        QPalette: Dark color scheme palette
    """
    dark_palette = QPalette()

    # Window colors
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))

    # Base colors (for input fields, lists, etc.)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))

    # Text colors
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(128, 128, 128))

    # Button colors
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))

    # Highlight colors - Mountrix Blue
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(52, 152, 219))  # #3498db
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    # Link colors - Mountrix Blue
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(52, 152, 219))  # #3498db
    dark_palette.setColor(QPalette.ColorRole.LinkVisited, QColor(46, 204, 113))  # #2ecc71

    # Disabled colors
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
                          QColor(128, 128, 128))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
                          QColor(128, 128, 128))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                          QColor(128, 128, 128))

    return dark_palette


def create_light_palette() -> QPalette:
    """
    Create a light color palette for the application.

    Returns:
        QPalette: Light color scheme palette (system default)
    """
    # Return the default system palette
    app = QApplication.instance()
    if app and app.style():
        return app.style().standardPalette()

    # Fallback: create a default light palette
    return QPalette()


def apply_theme(theme: str) -> None:
    """
    Apply a theme to the application.

    Args:
        theme: Theme name ("dark", "light", or "system")
    """
    app = QApplication.instance()
    if not app:
        return

    # Determine actual theme
    actual_theme = theme
    if theme == "system":
        system_theme = detect_system_theme()
        actual_theme = "dark" if system_theme == "dark" else "light"

    # Apply palette
    if actual_theme == "dark":
        app.setPalette(create_dark_palette())
    else:
        app.setPalette(create_light_palette())

    # WICHTIG: Stylesheet nach setPalette() neu anwenden mit richtigem Theme
    app.setStyleSheet(get_modern_stylesheet(actual_theme))


class MountrixMainWindow(QMainWindow):
    """Main window for Mountrix application."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("Mountrix - Mount Manager")
        self.setMinimumSize(900, 600)

        # Theme tracking
        self.current_theme = "light"

        # Initialize UI components
        self._create_hamburger_menu()
        self._create_central_widget()
        self._create_status_bar()

        # Load initial data
        self.refresh_mount_list()

    def _update_hamburger_button_style(self):
        """Update hamburger button style based on current theme."""
        if self.current_theme == "dark":
            self.hamburger_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 24pt;
                    color: #ecf0f1;
                    padding: 0;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    border-radius: 4px;
                }
                QPushButton:pressed {
                    background-color: #7f8c8d;
                }
            """)
        else:
            self.hamburger_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 24pt;
                    color: #2c3e50;
                    padding: 0;
                }
                QPushButton:hover {
                    background-color: #ecf0f1;
                    border-radius: 4px;
                }
                QPushButton:pressed {
                    background-color: #bdc3c7;
                }
            """)

    def _create_hamburger_menu(self):
        """Create hamburger menu button in top-left corner."""
        from PyQt6.QtWidgets import QMenu

        # Create hamburger button
        self.hamburger_button = QPushButton("☰")
        self.hamburger_button.setFixedSize(40, 40)
        self._update_hamburger_button_style()

        # Create menu
        self.hamburger_menu = QMenu(self)

        # Datei Section
        new_action = QAction("Neu...", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_mount)
        self.hamburger_menu.addAction(new_action)

        self.hamburger_menu.addSeparator()

        refresh_action = QAction("Aktualisieren", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_mount_list)
        self.hamburger_menu.addAction(refresh_action)

        self.hamburger_menu.addSeparator()

        # Ansicht Section
        self.dark_mode_action = QAction("Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.triggered.connect(self.on_toggle_dark_mode)
        self.hamburger_menu.addAction(self.dark_mode_action)

        settings_action = QAction("Einstellungen", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.on_settings)
        self.hamburger_menu.addAction(settings_action)

        self.hamburger_menu.addSeparator()

        # Hilfe Section
        about_action = QAction("Über Mountrix", self)
        about_action.triggered.connect(self.on_about)
        self.hamburger_menu.addAction(about_action)

        help_action = QAction("Hilfe", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.on_help)
        self.hamburger_menu.addAction(help_action)

        self.hamburger_menu.addSeparator()

        exit_action = QAction("Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        self.hamburger_menu.addAction(exit_action)

        # Connect button to menu
        self.hamburger_button.clicked.connect(self._show_hamburger_menu)

    def _show_hamburger_menu(self):
        """Show hamburger menu below button."""
        button_pos = self.hamburger_button.mapToGlobal(self.hamburger_button.rect().bottomLeft())
        self.hamburger_menu.exec(button_pos)

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

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Top bar with action buttons and hamburger menu
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(8, 8, 8, 8)
        top_bar_layout.setSpacing(8)

        # Action buttons (left)
        self.new_button = QPushButton("Neu")
        self.new_button.setStatusTip("Neuen Mount erstellen")
        self.new_button.clicked.connect(self.on_new_mount)
        self.new_button.setShortcut("Ctrl+N")
        top_bar_layout.addWidget(self.new_button)

        self.edit_button = QPushButton("Bearbeiten")
        self.edit_button.setStatusTip("Ausgewählten Mount bearbeiten")
        self.edit_button.clicked.connect(self.on_edit_mount)
        self.edit_button.setShortcut("Ctrl+E")
        top_bar_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Löschen")
        self.delete_button.setStatusTip("Ausgewählten Mount löschen")
        self.delete_button.clicked.connect(self.on_delete_mount)
        self.delete_button.setShortcut("Delete")
        top_bar_layout.addWidget(self.delete_button)

        self.refresh_button = QPushButton("Aktualisieren")
        self.refresh_button.setStatusTip("Mount-Liste aktualisieren")
        self.refresh_button.clicked.connect(self.refresh_mount_list)
        self.refresh_button.setShortcut("F5")
        top_bar_layout.addWidget(self.refresh_button)

        # Spacer
        top_bar_layout.addStretch()

        # Hamburger menu button (right)
        top_bar_layout.addWidget(self.hamburger_button)

        main_layout.addLayout(top_bar_layout)

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

        main_layout.addWidget(self.mount_tree)

        # Bottom button row
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

        main_layout.addLayout(button_layout)

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
        from .dialogs import SettingsDialog

        dialog = SettingsDialog(self)

        # Pre-select current theme
        theme_map = {"system": "System", "dark": "Dunkel", "light": "Hell"}
        current_theme_text = theme_map.get(self.current_theme, "System")
        dialog.theme_combo.setCurrentText(current_theme_text)

        if dialog.exec():
            settings = dialog.get_settings()

            # Apply theme based on settings
            theme_text = settings["theme"]
            if theme_text == "System":
                apply_theme("system")
                self.current_theme = "system"
                self.dark_mode_action.setChecked(False)
            elif theme_text == "Dunkel":
                apply_theme("dark")
                self.current_theme = "dark"
                self.dark_mode_action.setChecked(True)
            elif theme_text == "Hell":
                apply_theme("light")
                self.current_theme = "light"
                self.dark_mode_action.setChecked(False)

            # Update hamburger button style
            self._update_hamburger_button_style()

            self.status_bar.showMessage(f"Einstellungen gespeichert: Theme '{theme_text}'")

    def on_toggle_dark_mode(self, checked):
        """Toggle dark mode."""
        if checked:
            apply_theme("dark")
            self.current_theme = "dark"
            self._update_hamburger_button_style()
            self.status_bar.showMessage("Dark Mode aktiviert")
        else:
            apply_theme("light")
            self.current_theme = "light"
            self._update_hamburger_button_style()
            self.status_bar.showMessage("Light Mode aktiviert")

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

    # Stylesheet VOR Fenster-Erstellung anwenden
    app.setStyleSheet(get_modern_stylesheet())

    window = MountrixMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
