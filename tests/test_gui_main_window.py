# -*- coding: utf-8 -*-
"""
Tests for GUI main window (main_window.py).

Tests the main application window using pytest-qt.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox

from mountrix.gui.qt.main_window import MountrixMainWindow


class TestMainWindowCreation:
    """Tests for MainWindow creation and initialization."""

    def test_window_creation(self, qtbot):
        """Test that main window can be created."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        assert window.windowTitle() == "Mountrix - Mount Manager"
        assert window.minimumSize().width() == 900
        assert window.minimumSize().height() == 600

    def test_window_has_menubar(self, qtbot):
        """Test that window has a menu bar."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        menubar = window.menuBar()
        assert menubar is not None

        # Check for main menus
        menu_actions = [action.text() for action in menubar.actions()]
        assert "&Datei" in menu_actions
        assert "&Bearbeiten" in menu_actions

    def test_window_has_toolbar(self, qtbot):
        """Test that window has a toolbar."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        toolbars = window.findChildren(type(window.addToolBar("")))
        assert len(toolbars) > 0

    def test_window_has_statusbar(self, qtbot):
        """Test that window has a status bar."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        statusbar = window.statusBar()
        assert statusbar is not None

    def test_window_has_central_widget(self, qtbot):
        """Test that window has a central widget."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        central_widget = window.centralWidget()
        assert central_widget is not None


class TestMenuBar:
    """Tests for menu bar functionality."""

    def test_file_menu_exists(self, qtbot):
        """Test that File menu exists."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        menubar = window.menuBar()
        file_menu = None
        for action in menubar.actions():
            if "Datei" in action.text():
                file_menu = action.menu()
                break

        assert file_menu is not None

    def test_edit_menu_exists(self, qtbot):
        """Test that Edit menu exists."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        menubar = window.menuBar()
        edit_menu = None
        for action in menubar.actions():
            if "Bearbeiten" in action.text():
                edit_menu = action.menu()
                break

        assert edit_menu is not None

    def test_file_menu_has_new_action(self, qtbot):
        """Test that File menu has New action."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        menubar = window.menuBar()
        file_menu = None
        for action in menubar.actions():
            if "Datei" in action.text():
                file_menu = action.menu()
                break

        assert file_menu is not None
        actions = [action.text() for action in file_menu.actions() if action.text()]
        assert any("Neu" in action for action in actions)

    def test_file_menu_has_refresh_action(self, qtbot):
        """Test that File menu has Refresh action."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        menubar = window.menuBar()
        file_menu = None
        for action in menubar.actions():
            if "Datei" in action.text():
                file_menu = action.menu()
                break

        actions = [action.text() for action in file_menu.actions() if action.text()]
        assert any("Aktualisieren" in action for action in actions)

    def test_file_menu_has_exit_action(self, qtbot):
        """Test that File menu has Exit action."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        menubar = window.menuBar()
        file_menu = None
        for action in menubar.actions():
            if "Datei" in action.text():
                file_menu = action.menu()
                break

        actions = [action.text() for action in file_menu.actions() if action.text()]
        assert any("Beenden" in action for action in actions)


class TestCentralWidget:
    """Tests for central widget (mount list)."""

    def test_central_widget_exists(self, qtbot):
        """Test that central widget is created."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        assert window.centralWidget() is not None

    def test_mount_tree_exists(self, qtbot):
        """Test that mount tree widget exists."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        # The mount_tree should be an attribute of the window
        assert hasattr(window, 'mount_tree')
        assert window.mount_tree is not None

    def test_mount_tree_has_headers(self, qtbot):
        """Test that mount tree has column headers."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        tree = window.mount_tree
        header_labels = [tree.headerItem().text(i) for i in range(tree.columnCount())]

        # Check for expected headers
        assert len(header_labels) > 0


class TestMountListRefresh:
    """Tests for mount list refresh functionality."""

    @patch('mountrix.gui.qt.main_window.verify_mount')
    @patch('mountrix.gui.qt.main_window.parse_fstab')
    def test_refresh_mount_list(self, mock_parse_fstab, mock_verify, qtbot):
        """Test refreshing the mount list."""
        # Mock verify_mount to return False (not mounted)
        mock_verify.return_value = False

        # Mock fstab entries - using FstabEntry from core.fstab
        from mountrix.core.fstab import FstabEntry
        mock_parse_fstab.return_value = [
            FstabEntry(
                source='//nas/share',
                mountpoint='/mnt/nas',
                fstype='cifs',
                options=['defaults', 'nofail'],
                dump=0,
                pass_num=0
            )
        ]

        window = MountrixMainWindow()
        qtbot.addWidget(window)

        # Refresh should have been called in __init__
        assert mock_parse_fstab.called

        # Clear and refresh again
        window.mount_tree.clear()
        window.refresh_mount_list()

        # Tree should have items
        assert window.mount_tree.topLevelItemCount() == 1

    @patch('mountrix.gui.qt.main_window.verify_mount')
    @patch('mountrix.gui.qt.main_window.parse_fstab')
    def test_refresh_empty_mount_list(self, mock_parse_fstab, mock_verify, qtbot):
        """Test refreshing with empty mount list."""
        mock_parse_fstab.return_value = []
        mock_verify.return_value = False

        window = MountrixMainWindow()
        qtbot.addWidget(window)

        window.refresh_mount_list()

        # Tree should be empty
        assert window.mount_tree.topLevelItemCount() == 0

    @patch('PyQt6.QtWidgets.QMessageBox.critical')
    @patch('mountrix.gui.qt.main_window.verify_mount')
    @patch('mountrix.gui.qt.main_window.parse_fstab')
    def test_refresh_handles_exception(self, mock_parse_fstab, mock_verify, mock_critical, qtbot):
        """Test that refresh handles exceptions gracefully."""
        mock_parse_fstab.side_effect = Exception("Test error")
        mock_verify.return_value = False

        window = MountrixMainWindow()
        qtbot.addWidget(window)

        # Should not crash
        window.refresh_mount_list()

        # Critical dialog should be shown
        assert mock_critical.called


class TestEventHandlers:
    """Tests for event handler methods."""

    @patch('mountrix.gui.qt.main_window.QMessageBox.information')
    def test_on_new_mount_calls_wizard(self, mock_msgbox, qtbot):
        """Test that on_new_mount calls wizard mode."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        window.on_new_mount()

        # Message box should be called (wizard not yet implemented)
        assert mock_msgbox.called

    @patch('PyQt6.QtWidgets.QMessageBox.information')
    def test_on_wizard_mode(self, mock_info, qtbot):
        """Test wizard mode handler."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        window.on_wizard_mode()

        # Should show info dialog
        assert mock_info.called

    @patch('PyQt6.QtWidgets.QMessageBox.information')
    def test_on_advanced_mode(self, mock_info, qtbot):
        """Test advanced mode handler."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        window.on_advanced_mode()

        # Should show info dialog
        assert mock_info.called

    @patch('PyQt6.QtWidgets.QMessageBox.information')
    def test_on_settings(self, mock_info, qtbot):
        """Test settings dialog handler."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        window.on_settings()

        # Settings dialog should show message
        assert mock_info.called

    @patch('PyQt6.QtWidgets.QMessageBox.about')
    def test_on_about(self, mock_about, qtbot):
        """Test about dialog handler."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        window.on_about()

        # About dialog should be shown
        assert mock_about.called

    @patch('PyQt6.QtWidgets.QMessageBox.information')
    def test_on_help(self, mock_info, qtbot):
        """Test help dialog handler."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        window.on_help()

        # Help dialog should be shown
        assert mock_info.called

    @patch('PyQt6.QtWidgets.QMessageBox.warning')
    def test_on_delete_mount_no_selection(self, mock_warning, qtbot):
        """Test delete mount with no selection."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        # Clear selection
        window.mount_tree.clearSelection()

        window.on_delete_mount()

        # Warning should be shown
        assert mock_warning.called

    @patch('PyQt6.QtWidgets.QMessageBox.warning')
    def test_on_edit_mount_no_selection(self, mock_warning, qtbot):
        """Test edit mount with no selection."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        # Clear selection
        window.mount_tree.clearSelection()

        window.on_edit_mount()

        # Warning should be shown
        assert mock_warning.called


class TestDarkModeToggle:
    """Tests for dark mode toggle."""

    def test_toggle_dark_mode_on(self, qtbot):
        """Test toggling dark mode on."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        # Should not crash
        window.on_toggle_dark_mode(True)

    def test_toggle_dark_mode_off(self, qtbot):
        """Test toggling dark mode off."""
        window = MountrixMainWindow()
        qtbot.addWidget(window)

        # Should not crash
        window.on_toggle_dark_mode(False)
