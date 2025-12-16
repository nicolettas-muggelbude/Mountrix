# -*- coding: utf-8 -*-
"""
Common dialogs for Mountrix PyQt6 GUI.

Provides confirmation, error, progress, and settings dialogs.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class ConfirmationDialog(QDialog):
    """Dialog to confirm fstab changes."""

    def __init__(self, parent=None, changes_text=""):
        """
        Initialize the confirmation dialog.

        Args:
            parent: Parent widget
            changes_text: Text describing the changes
        """
        super().__init__(parent)

        self.setWindowTitle("Änderungen bestätigen")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # Warning icon and text
        warning_layout = QHBoxLayout()
        warning_label = QLabel(
            "<h3>⚠ Bestätigung erforderlich</h3>"
            "<p>Die fstab-Datei wird geändert. Bitte überprüfe die Änderungen.</p>"
        )
        warning_label.setWordWrap(True)
        warning_layout.addWidget(warning_label)
        layout.addLayout(warning_layout)

        # Changes preview
        changes_group = QGroupBox("Geplante Änderungen")
        changes_layout = QVBoxLayout()

        self.changes_text = QTextEdit()
        self.changes_text.setReadOnly(True)
        self.changes_text.setPlainText(changes_text)
        self.changes_text.setFontFamily("Monospace")
        changes_layout.addWidget(self.changes_text)

        changes_group.setLayout(changes_layout)
        layout.addWidget(changes_group)

        # Backup confirmation
        self.backup_check = QCheckBox("Backup der aktuellen fstab erstellen (empfohlen)")
        self.backup_check.setChecked(True)
        layout.addWidget(self.backup_check)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Make OK button more prominent
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Änderungen übernehmen")
        ok_button.setDefault(True)

        layout.addWidget(button_box)

        self.setLayout(layout)

    def should_create_backup(self):
        """Check if backup should be created."""
        return self.backup_check.isChecked()


class ErrorDialog(QDialog):
    """Dialog to display detailed error information."""

    def __init__(self, parent=None, error_message="", error_details=""):
        """
        Initialize the error dialog.

        Args:
            parent: Parent widget
            error_message: Main error message
            error_details: Detailed error information
        """
        super().__init__(parent)

        self.setWindowTitle("Fehler")
        self.setMinimumSize(500, 300)

        layout = QVBoxLayout()

        # Error icon and message
        error_header = QLabel(f"<h3>❌ {error_message}</h3>")
        error_header.setWordWrap(True)
        layout.addWidget(error_header)

        # Error details
        if error_details:
            details_group = QGroupBox("Details")
            details_layout = QVBoxLayout()

            details_text = QTextEdit()
            details_text.setReadOnly(True)
            details_text.setPlainText(error_details)
            details_text.setFontFamily("Monospace")
            details_layout.addWidget(details_text)

            details_group.setLayout(details_layout)
            layout.addWidget(details_group)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)


class ProgressDialog(QDialog):
    """Dialog to show operation progress."""

    def __init__(self, parent=None, title="Operation läuft", steps=None):
        """
        Initialize the progress dialog.

        Args:
            parent: Parent widget
            title: Dialog title
            steps: List of step descriptions
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setMinimumSize(400, 200)
        self.setModal(True)

        self.steps = steps or []
        self.current_step = 0

        layout = QVBoxLayout()

        # Current step label
        self.step_label = QLabel("Vorbereitung...")
        self.step_label.setWordWrap(True)
        layout.addWidget(self.step_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(len(self.steps) if self.steps else 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status text
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        layout.addWidget(self.status_text)

        # Cancel button
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def set_step(self, step_index):
        """
        Set the current step.

        Args:
            step_index: Index of the current step
        """
        if step_index < len(self.steps):
            self.current_step = step_index
            self.step_label.setText(f"Schritt {step_index + 1}/{len(self.steps)}: {self.steps[step_index]}")
            self.progress_bar.setValue(step_index + 1)
            self.add_status(f"✓ {self.steps[step_index]}")

    def add_status(self, message):
        """
        Add a status message.

        Args:
            message: Status message to add
        """
        self.status_text.append(message)

    def set_completed(self):
        """Mark the operation as completed."""
        self.step_label.setText("✓ Abgeschlossen!")
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.cancel_button.setText("Schließen")
        self.cancel_button.clicked.disconnect()
        self.cancel_button.clicked.connect(self.accept)


class RollbackDialog(QDialog):
    """Dialog to offer rollback after an error."""

    def __init__(self, parent=None, error_message="", backup_path=""):
        """
        Initialize the rollback dialog.

        Args:
            parent: Parent widget
            error_message: Error that occurred
            backup_path: Path to backup file
        """
        super().__init__(parent)

        self.setWindowTitle("Rollback angeboten")
        self.setMinimumSize(500, 300)

        layout = QVBoxLayout()

        # Error description
        error_label = QLabel(
            f"<h3>⚠ Ein Fehler ist aufgetreten</h3>"
            f"<p>{error_message}</p>"
            f"<p>Es wurde ein Backup der vorherigen fstab erstellt:<br>"
            f"<b>{backup_path}</b></p>"
        )
        error_label.setWordWrap(True)
        layout.addWidget(error_label)

        # Rollback options
        options_group = QGroupBox("Optionen")
        options_layout = QVBoxLayout()

        rollback_label = QLabel(
            "Möchtest du die Änderungen rückgängig machen und "
            "das Backup wiederherstellen?"
        )
        rollback_label.setWordWrap(True)
        options_layout.addWidget(rollback_label)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Buttons
        button_layout = QHBoxLayout()

        rollback_btn = QPushButton("Rollback durchführen")
        rollback_btn.clicked.connect(self.accept)
        rollback_btn.setDefault(True)

        keep_btn = QPushButton("Änderungen behalten")
        keep_btn.clicked.connect(self.reject)

        button_layout.addWidget(rollback_btn)
        button_layout.addWidget(keep_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)

        self.setWindowTitle("Einstellungen")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # General settings
        general_group = QGroupBox("Allgemein")
        general_layout = QFormLayout()

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Deutsch", "English"])
        general_layout.addRow("Sprache:", self.language_combo)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Hell", "Dunkel"])
        general_layout.addRow("Theme:", self.theme_combo)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # Behavior settings
        behavior_group = QGroupBox("Verhalten")
        behavior_layout = QVBoxLayout()

        self.confirm_delete_check = QCheckBox(
            "Löschvorgänge bestätigen"
        )
        self.confirm_delete_check.setChecked(True)

        self.auto_backup_check = QCheckBox(
            "Automatisches fstab-Backup vor Änderungen"
        )
        self.auto_backup_check.setChecked(True)

        self.auto_refresh_check = QCheckBox(
            "Mount-Liste automatisch aktualisieren"
        )
        self.auto_refresh_check.setChecked(True)

        behavior_layout.addWidget(self.confirm_delete_check)
        behavior_layout.addWidget(self.auto_backup_check)
        behavior_layout.addWidget(self.auto_refresh_check)

        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)

        # Advanced settings
        advanced_group = QGroupBox("Erweitert")
        advanced_layout = QFormLayout()

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        advanced_layout.addRow("Log-Level:", self.log_level_combo)

        self.backup_count_combo = QComboBox()
        self.backup_count_combo.addItems(["3", "5", "10", "20"])
        self.backup_count_combo.setCurrentText("5")
        advanced_layout.addRow("Max. Backup-Anzahl:", self.backup_count_combo)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_settings(self):
        """Get the configured settings."""
        return {
            "language": self.language_combo.currentText(),
            "theme": self.theme_combo.currentText(),
            "confirm_delete": self.confirm_delete_check.isChecked(),
            "auto_backup": self.auto_backup_check.isChecked(),
            "auto_refresh": self.auto_refresh_check.isChecked(),
            "log_level": self.log_level_combo.currentText(),
            "backup_count": int(self.backup_count_combo.currentText()),
        }


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test ConfirmationDialog
    dialog = ConfirmationDialog(
        changes_text="//nas/share /mnt/nas cifs defaults,nofail 0 0"
    )
    dialog.exec()

    sys.exit(0)
