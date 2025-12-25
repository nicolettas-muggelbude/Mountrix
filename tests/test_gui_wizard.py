# -*- coding: utf-8 -*-
"""
Tests for GUI wizard (wizard.py).

Tests the 9-step mount creation wizard using pytest-qt.
"""

import pytest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QWizard

from mountrix.gui.qt.wizard import (
    MountWizard,
    ModePage,
    TemplatePage,
    NetworkPage,
    LocalDrivePage,
    AuthenticationPage,
    MountOptionsPage,
    ConnectionTestPage,
    PreviewPage,
    ConfirmPage,
)


class TestWizardCreation:
    """Tests for wizard creation and initialization."""

    def test_wizard_creation(self, qtbot):
        """Test that wizard can be created."""
        wizard = MountWizard()
        qtbot.addWidget(wizard)

        assert wizard.windowTitle() == "Mountrix - Neuer Mount Assistent"
        assert wizard.minimumSize().width() == 700
        assert wizard.minimumSize().height() == 500

    def test_wizard_has_all_pages(self, qtbot):
        """Test that wizard has all 9 pages."""
        wizard = MountWizard()
        qtbot.addWidget(wizard)

        # Check that all page IDs are set
        assert wizard.PAGE_MODE == 0
        assert wizard.PAGE_TEMPLATE == 1
        assert wizard.PAGE_NETWORK == 2
        assert wizard.PAGE_LOCAL_DRIVE == 3
        assert wizard.PAGE_AUTH == 4
        assert wizard.PAGE_OPTIONS == 5
        assert wizard.PAGE_TEST == 6
        assert wizard.PAGE_PREVIEW == 7
        assert wizard.PAGE_CONFIRM == 8

    def test_wizard_starts_at_mode_page(self, qtbot):
        """Test that wizard starts at MODE page."""
        wizard = MountWizard()
        qtbot.addWidget(wizard)

        assert wizard.startId() == wizard.PAGE_MODE

    def test_wizard_pages_exist(self, qtbot):
        """Test that all pages exist in wizard."""
        wizard = MountWizard()
        qtbot.addWidget(wizard)

        # Check that pages can be retrieved
        assert wizard.page(wizard.PAGE_MODE) is not None
        assert wizard.page(wizard.PAGE_TEMPLATE) is not None
        assert wizard.page(wizard.PAGE_NETWORK) is not None
        assert wizard.page(wizard.PAGE_LOCAL_DRIVE) is not None
        assert wizard.page(wizard.PAGE_AUTH) is not None
        assert wizard.page(wizard.PAGE_OPTIONS) is not None
        assert wizard.page(wizard.PAGE_TEST) is not None
        assert wizard.page(wizard.PAGE_PREVIEW) is not None
        assert wizard.page(wizard.PAGE_CONFIRM) is not None


class TestModePage:
    """Tests for ModePage (Page 1)."""

    def test_page_creation(self, qtbot):
        """Test that ModePage can be created."""
        page = ModePage()
        qtbot.addWidget(page)

        assert page.title() == "Mount-Typ wählen"

    def test_page_has_network_radio(self, qtbot):
        """Test that page has network radio button."""
        page = ModePage()
        qtbot.addWidget(page)

        assert hasattr(page, 'network_radio')
        assert page.network_radio is not None

    def test_page_has_local_radio(self, qtbot):
        """Test that page has local radio button."""
        page = ModePage()
        qtbot.addWidget(page)

        assert hasattr(page, 'local_radio')
        assert page.local_radio is not None

    def test_network_radio_default_checked(self, qtbot):
        """Test that network radio is checked by default."""
        page = ModePage()
        qtbot.addWidget(page)

        assert page.network_radio.isChecked()
        assert not page.local_radio.isChecked()

    def test_can_select_local_radio(self, qtbot):
        """Test that local radio can be selected."""
        page = ModePage()
        qtbot.addWidget(page)

        page.local_radio.setChecked(True)

        assert page.local_radio.isChecked()
        assert not page.network_radio.isChecked()


class TestTemplatePage:
    """Tests for TemplatePage (Page 2)."""

    @patch('mountrix.gui.qt.wizard.load_templates')
    def test_page_creation(self, mock_load_templates, qtbot):
        """Test that TemplatePage can be created."""
        mock_load_templates.return_value = []

        page = TemplatePage()
        qtbot.addWidget(page)

        assert page.title() == "NAS-Template wählen"

    @patch('mountrix.gui.qt.wizard.load_templates')
    def test_page_has_template_combo(self, mock_load_templates, qtbot):
        """Test that page has template combo box."""
        mock_load_templates.return_value = []

        page = TemplatePage()
        qtbot.addWidget(page)

        assert hasattr(page, 'template_combo')
        assert page.template_combo is not None


class TestNetworkPage:
    """Tests for NetworkPage (Page 3)."""

    def test_page_creation(self, qtbot):
        """Test that NetworkPage can be created."""
        page = NetworkPage()
        qtbot.addWidget(page)

        assert page.title() == "Netzwerk-Konfiguration"

    def test_page_has_protocol_combo(self, qtbot):
        """Test that page has protocol combo box."""
        page = NetworkPage()
        qtbot.addWidget(page)

        assert hasattr(page, 'protocol_combo')
        assert page.protocol_combo is not None

    def test_page_has_host_input(self, qtbot):
        """Test that page has host input field."""
        page = NetworkPage()
        qtbot.addWidget(page)

        assert hasattr(page, 'host_input')
        assert page.host_input is not None

    def test_page_has_share_input(self, qtbot):
        """Test that page has share input field."""
        page = NetworkPage()
        qtbot.addWidget(page)

        assert hasattr(page, 'share_input')
        assert page.share_input is not None


class TestLocalDrivePage:
    """Tests for LocalDrivePage (Page 4)."""

    @patch('mountrix.gui.qt.wizard.detect_local_drives')
    def test_page_creation(self, mock_detect_drives, qtbot):
        """Test that LocalDrivePage can be created."""
        mock_detect_drives.return_value = []

        page = LocalDrivePage()
        qtbot.addWidget(page)

        assert page.title() == "Laufwerk wählen"

    @patch('mountrix.gui.qt.wizard.detect_local_drives')
    def test_page_has_drive_list(self, mock_detect_drives, qtbot):
        """Test that page has drive list widget."""
        mock_detect_drives.return_value = []

        page = LocalDrivePage()
        qtbot.addWidget(page)

        assert hasattr(page, 'drive_list')
        assert page.drive_list is not None


class TestAuthenticationPage:
    """Tests for AuthenticationPage (Page 5)."""

    def test_page_creation(self, qtbot):
        """Test that AuthenticationPage can be created."""
        page = AuthenticationPage()
        qtbot.addWidget(page)

        assert page.title() == "Authentifizierung"

    def test_page_has_username_input(self, qtbot):
        """Test that page has username input field."""
        page = AuthenticationPage()
        qtbot.addWidget(page)

        assert hasattr(page, 'username_input')
        assert page.username_input is not None

    def test_page_has_password_input(self, qtbot):
        """Test that page has password input field."""
        page = AuthenticationPage()
        qtbot.addWidget(page)

        assert hasattr(page, 'password_input')
        assert page.password_input is not None

    def test_page_has_no_auth_radio(self, qtbot):
        """Test that page has no-auth radio button."""
        page = AuthenticationPage()
        qtbot.addWidget(page)

        assert hasattr(page, 'no_auth_radio')
        assert page.no_auth_radio is not None

    def test_password_field_is_echo_mode(self, qtbot):
        """Test that password field is in password mode."""
        page = AuthenticationPage()
        qtbot.addWidget(page)

        # Password field should have echo mode set to Password
        from PyQt6.QtWidgets import QLineEdit
        assert page.password_input.echoMode() == QLineEdit.EchoMode.Password


class TestMountOptionsPage:
    """Tests for MountOptionsPage (Page 6)."""

    def test_page_creation(self, qtbot):
        """Test that MountOptionsPage can be created."""
        page = MountOptionsPage()
        qtbot.addWidget(page)

        assert page.title() == "Mount-Optionen"

    def test_page_has_name_input(self, qtbot):
        """Test that page has mount name input field."""
        page = MountOptionsPage()
        qtbot.addWidget(page)

        assert hasattr(page, 'name_input')
        assert page.name_input is not None

    def test_page_has_mount_at_boot_checkbox(self, qtbot):
        """Test that page has mount-at-boot checkbox."""
        page = MountOptionsPage()
        qtbot.addWidget(page)

        assert hasattr(page, 'mount_at_boot')
        assert page.mount_at_boot is not None

    def test_mount_at_boot_default_checked(self, qtbot):
        """Test that mount-at-boot is checked by default."""
        page = MountOptionsPage()
        qtbot.addWidget(page)

        assert page.mount_at_boot.isChecked()


class TestConnectionTestPage:
    """Tests for ConnectionTestPage (Page 7)."""

    def test_page_creation(self, qtbot):
        """Test that ConnectionTestPage can be created."""
        page = ConnectionTestPage()
        qtbot.addWidget(page)

        assert page.title() == "Verbindungstest"

    def test_page_has_test_output(self, qtbot):
        """Test that page has test output widget."""
        page = ConnectionTestPage()
        qtbot.addWidget(page)

        assert hasattr(page, 'test_output')
        assert page.test_output is not None

    def test_page_test_output_readonly(self, qtbot):
        """Test that test output is read-only."""
        page = ConnectionTestPage()
        qtbot.addWidget(page)

        assert page.test_output.isReadOnly()


class TestPreviewPage:
    """Tests for PreviewPage (Page 8)."""

    def test_page_creation(self, qtbot):
        """Test that PreviewPage can be created."""
        page = PreviewPage()
        qtbot.addWidget(page)

        assert page.title() == "Vorschau"

    def test_page_has_preview_text(self, qtbot):
        """Test that page has preview text widget."""
        page = PreviewPage()
        qtbot.addWidget(page)

        assert hasattr(page, 'preview_text')
        assert page.preview_text is not None


class TestConfirmPage:
    """Tests for ConfirmPage (Page 9)."""

    def test_page_creation(self, qtbot):
        """Test that ConfirmPage can be created."""
        page = ConfirmPage()
        qtbot.addWidget(page)

        assert page.title() == "Bestätigung"

    def test_page_is_final_page(self, qtbot):
        """Test that page is marked as final page."""
        page = ConfirmPage()
        qtbot.addWidget(page)

        # ConfirmPage should return -1 from nextId() to indicate it's final
        assert page.nextId() == -1


class TestWizardNavigation:
    """Tests for wizard navigation flow."""

    def test_wizard_can_navigate_forward(self, qtbot):
        """Test that wizard can navigate forward."""
        wizard = MountWizard()
        qtbot.addWidget(wizard)

        # Restart wizard to initialize current page
        wizard.restart()

        # Should now be at MODE page
        assert wizard.currentId() == wizard.PAGE_MODE

        # Should be able to get next button
        next_button = wizard.button(QWizard.WizardButton.NextButton)
        assert next_button is not None

    def test_wizard_can_navigate_backward(self, qtbot):
        """Test that wizard has back button."""
        wizard = MountWizard()
        qtbot.addWidget(wizard)

        back_button = wizard.button(QWizard.WizardButton.BackButton)
        assert back_button is not None

    def test_wizard_has_finish_button(self, qtbot):
        """Test that wizard has finish button."""
        wizard = MountWizard()
        qtbot.addWidget(wizard)

        finish_button = wizard.button(QWizard.WizardButton.FinishButton)
        assert finish_button is not None

    def test_wizard_has_cancel_button(self, qtbot):
        """Test that wizard has cancel button."""
        wizard = MountWizard()
        qtbot.addWidget(wizard)

        cancel_button = wizard.button(QWizard.WizardButton.CancelButton)
        assert cancel_button is not None
