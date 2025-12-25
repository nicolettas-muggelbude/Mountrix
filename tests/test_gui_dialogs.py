# -*- coding: utf-8 -*-
"""
Tests for GUI dialogs (dialogs.py).

Tests all dialog classes using pytest-qt.
"""

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox

from mountrix.gui.qt.dialogs import (
    ConfirmationDialog,
    ErrorDialog,
    ProgressDialog,
    RollbackDialog,
    SettingsDialog,
)


class TestConfirmationDialog:
    """Tests for ConfirmationDialog."""

    def test_dialog_creation(self, qtbot):
        """Test that ConfirmationDialog can be created."""
        dialog = ConfirmationDialog()
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Änderungen bestätigen"
        assert dialog.minimumSize().width() == 500
        assert dialog.minimumSize().height() == 400

    def test_changes_text_display(self, qtbot):
        """Test that changes text is displayed correctly."""
        test_changes = "//nas/share /mnt/nas cifs defaults,nofail 0 0"
        dialog = ConfirmationDialog(changes_text=test_changes)
        qtbot.addWidget(dialog)

        assert dialog.changes_text.toPlainText() == test_changes
        assert dialog.changes_text.isReadOnly()

    def test_backup_checkbox_default_checked(self, qtbot):
        """Test that backup checkbox is checked by default."""
        dialog = ConfirmationDialog()
        qtbot.addWidget(dialog)

        assert dialog.backup_check.isChecked()
        assert dialog.should_create_backup()

    def test_backup_checkbox_unchecked(self, qtbot):
        """Test that backup checkbox can be unchecked."""
        dialog = ConfirmationDialog()
        qtbot.addWidget(dialog)

        dialog.backup_check.setChecked(False)
        assert not dialog.should_create_backup()

    def test_empty_changes_text(self, qtbot):
        """Test dialog with empty changes text."""
        dialog = ConfirmationDialog(changes_text="")
        qtbot.addWidget(dialog)

        assert dialog.changes_text.toPlainText() == ""


class TestErrorDialog:
    """Tests for ErrorDialog."""

    def test_dialog_creation(self, qtbot):
        """Test that ErrorDialog can be created."""
        dialog = ErrorDialog(error_message="Test Error")
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Fehler"
        assert dialog.minimumSize().width() == 500

    def test_error_message_display(self, qtbot):
        """Test that error message is displayed."""
        error_msg = "Mount failed"
        dialog = ErrorDialog(error_message=error_msg)
        qtbot.addWidget(dialog)

        # Check if error message is in the dialog
        assert error_msg in dialog.findChild(type(dialog.layout().itemAt(0).widget())).text()

    def test_error_with_details(self, qtbot):
        """Test error dialog with details."""
        error_msg = "Mount failed"
        error_details = "Device not found: /dev/sdb1"
        dialog = ErrorDialog(error_message=error_msg, error_details=error_details)
        qtbot.addWidget(dialog)

        # Dialog should have details
        assert error_msg in dialog.layout().itemAt(0).widget().text()

    def test_error_without_details(self, qtbot):
        """Test error dialog without details."""
        dialog = ErrorDialog(error_message="Simple error")
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Fehler"


class TestProgressDialog:
    """Tests for ProgressDialog."""

    def test_dialog_creation(self, qtbot):
        """Test that ProgressDialog can be created."""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Operation läuft"
        assert dialog.isModal()

    def test_dialog_with_steps(self, qtbot):
        """Test progress dialog with steps."""
        steps = ["Step 1", "Step 2", "Step 3"]
        dialog = ProgressDialog(steps=steps)
        qtbot.addWidget(dialog)

        assert dialog.steps == steps
        assert dialog.progress_bar.maximum() == len(steps)
        assert dialog.progress_bar.value() == 0

    def test_set_step(self, qtbot):
        """Test setting current step."""
        steps = ["Backup erstellen", "Mount hinzufügen", "fstab aktualisieren"]
        dialog = ProgressDialog(steps=steps)
        qtbot.addWidget(dialog)

        dialog.set_step(0)
        assert dialog.current_step == 0
        assert dialog.progress_bar.value() == 1
        assert "Backup erstellen" in dialog.step_label.text()

        dialog.set_step(1)
        assert dialog.current_step == 1
        assert dialog.progress_bar.value() == 2

    def test_add_status(self, qtbot):
        """Test adding status messages."""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)

        dialog.add_status("Status message 1")
        dialog.add_status("Status message 2")

        status_content = dialog.status_text.toPlainText()
        assert "Status message 1" in status_content
        assert "Status message 2" in status_content

    def test_set_completed(self, qtbot):
        """Test marking operation as completed."""
        steps = ["Step 1", "Step 2"]
        dialog = ProgressDialog(steps=steps)
        qtbot.addWidget(dialog)

        dialog.set_completed()

        assert "Abgeschlossen" in dialog.step_label.text()
        assert dialog.progress_bar.value() == dialog.progress_bar.maximum()
        assert dialog.cancel_button.text() == "Schließen"

    def test_progress_without_steps(self, qtbot):
        """Test progress dialog without predefined steps."""
        dialog = ProgressDialog()
        qtbot.addWidget(dialog)

        assert dialog.progress_bar.maximum() == 100
        assert len(dialog.steps) == 0


class TestRollbackDialog:
    """Tests for RollbackDialog."""

    def test_dialog_creation(self, qtbot):
        """Test that RollbackDialog can be created."""
        dialog = RollbackDialog()
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Rollback angeboten"
        assert dialog.minimumSize().width() == 500

    def test_error_message_display(self, qtbot):
        """Test that error message is displayed."""
        error_msg = "fstab validation failed"
        backup_path = "/var/backups/fstab.backup.20231224"
        dialog = RollbackDialog(error_message=error_msg, backup_path=backup_path)
        qtbot.addWidget(dialog)

        # Check if error message and backup path are displayed
        label_text = dialog.layout().itemAt(0).widget().text()
        assert error_msg in label_text
        assert backup_path in label_text

    def test_rollback_buttons(self, qtbot):
        """Test that rollback dialog has correct buttons."""
        dialog = RollbackDialog()
        qtbot.addWidget(dialog)

        # Find buttons by iterating through layout
        buttons = []
        for i in range(dialog.layout().count()):
            item = dialog.layout().itemAt(i)
            if item and item.layout():
                for j in range(item.layout().count()):
                    widget = item.layout().itemAt(j).widget()
                    if widget and hasattr(widget, 'text'):
                        buttons.append(widget.text())

        assert "Rollback durchführen" in buttons
        assert "Änderungen behalten" in buttons


class TestSettingsDialog:
    """Tests for SettingsDialog."""

    def test_dialog_creation(self, qtbot):
        """Test that SettingsDialog can be created."""
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Einstellungen"
        assert dialog.minimumSize().width() == 500

    def test_default_settings(self, qtbot):
        """Test default settings values."""
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        settings = dialog.get_settings()

        assert settings["language"] == "Deutsch"
        assert settings["theme"] == "System"
        assert settings["confirm_delete"] is True
        assert settings["auto_backup"] is True
        assert settings["auto_refresh"] is True
        assert settings["log_level"] == "INFO"
        assert settings["backup_count"] == 5

    def test_modify_language(self, qtbot):
        """Test modifying language setting."""
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        dialog.language_combo.setCurrentText("English")
        settings = dialog.get_settings()

        assert settings["language"] == "English"

    def test_modify_theme(self, qtbot):
        """Test modifying theme setting."""
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        dialog.theme_combo.setCurrentText("Dunkel")
        settings = dialog.get_settings()

        assert settings["theme"] == "Dunkel"

    def test_modify_checkboxes(self, qtbot):
        """Test modifying checkbox settings."""
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        dialog.confirm_delete_check.setChecked(False)
        dialog.auto_backup_check.setChecked(False)
        dialog.auto_refresh_check.setChecked(False)

        settings = dialog.get_settings()

        assert settings["confirm_delete"] is False
        assert settings["auto_backup"] is False
        assert settings["auto_refresh"] is False

    def test_modify_log_level(self, qtbot):
        """Test modifying log level setting."""
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        dialog.log_level_combo.setCurrentText("DEBUG")
        settings = dialog.get_settings()

        assert settings["log_level"] == "DEBUG"

    def test_modify_backup_count(self, qtbot):
        """Test modifying backup count setting."""
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        dialog.backup_count_combo.setCurrentText("10")
        settings = dialog.get_settings()

        assert settings["backup_count"] == 10

    def test_all_language_options(self, qtbot):
        """Test that all language options are available."""
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        languages = [dialog.language_combo.itemText(i) for i in range(dialog.language_combo.count())]
        assert "Deutsch" in languages
        assert "English" in languages

    def test_all_theme_options(self, qtbot):
        """Test that all theme options are available."""
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        themes = [dialog.theme_combo.itemText(i) for i in range(dialog.theme_combo.count())]
        assert "System" in themes
        assert "Hell" in themes
        assert "Dunkel" in themes
