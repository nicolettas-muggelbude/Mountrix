# -*- coding: utf-8 -*-
"""
Tests for credentials.py

Tests credential storage and SSH key validation.
"""

import stat
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from mountrix.core.credentials import (
    CredentialResult,
    delete_credentials_file,
    delete_credentials_keyring,
    generate_credentials_file,
    get_credential_files,
    is_keyring_available,
    load_credentials_keyring,
    read_credentials_file,
    save_credentials_keyring,
    validate_ssh_key,
)


class TestKeyringAvailability:
    """Tests for keyring availability check."""

    @patch("mountrix.core.credentials.KEYRING_AVAILABLE", True)
    @patch("mountrix.core.credentials.keyring")
    def test_keyring_available(self, mock_keyring):
        """Test when keyring is available."""
        mock_backend = MagicMock()
        mock_backend.priority = 10
        mock_keyring.get_keyring.return_value = mock_backend

        assert is_keyring_available() is True

    @patch("mountrix.core.credentials.KEYRING_AVAILABLE", False)
    def test_keyring_not_installed(self):
        """Test when keyring package is not installed."""
        assert is_keyring_available() is False

    @patch("mountrix.core.credentials.KEYRING_AVAILABLE", True)
    @patch("mountrix.core.credentials.keyring")
    def test_keyring_low_priority_backend(self, mock_keyring):
        """Test when keyring backend has low priority (fail backend)."""
        mock_backend = MagicMock()
        mock_backend.priority = 0
        mock_keyring.get_keyring.return_value = mock_backend

        assert is_keyring_available() is False

    @patch("mountrix.core.credentials.KEYRING_AVAILABLE", True)
    @patch("mountrix.core.credentials.keyring")
    def test_keyring_exception(self, mock_keyring):
        """Test when keyring raises exception."""
        mock_keyring.get_keyring.side_effect = Exception("Keyring error")

        assert is_keyring_available() is False


class TestSaveCredentialsKeyring:
    """Tests for save_credentials_keyring function."""

    @patch("mountrix.core.credentials.is_keyring_available")
    @patch("mountrix.core.credentials.keyring")
    def test_save_success(self, mock_keyring, mock_available):
        """Test successful save to keyring."""
        mock_available.return_value = True

        result = save_credentials_keyring("nas1", "admin", "secret")

        assert result.success is True
        assert "saved" in result.message.lower()
        assert result.username == "admin"
        mock_keyring.set_password.assert_called_once_with("nas1", "admin", "secret")

    @patch("mountrix.core.credentials.is_keyring_available")
    def test_save_keyring_not_available(self, mock_available):
        """Test save when keyring is not available."""
        mock_available.return_value = False

        result = save_credentials_keyring("nas1", "admin", "secret")

        assert result.success is False
        assert "not available" in result.message.lower()

    def test_save_empty_service(self):
        """Test save with empty service name."""
        result = save_credentials_keyring("", "admin", "secret")

        assert result.success is False
        assert "required" in result.message.lower()

    def test_save_empty_username(self):
        """Test save with empty username."""
        result = save_credentials_keyring("nas1", "", "secret")

        assert result.success is False
        assert "required" in result.message.lower()

    @patch("mountrix.core.credentials.is_keyring_available")
    @patch("mountrix.core.credentials.keyring")
    def test_save_password_set_error(self, mock_keyring, mock_available):
        """Test save when keyring raises an error."""
        mock_available.return_value = True

        # Create a real exception that can be caught
        class PasswordSetError(Exception):
            pass

        mock_keyring.errors.PasswordSetError = PasswordSetError
        mock_keyring.set_password.side_effect = PasswordSetError("Permission denied")

        result = save_credentials_keyring("nas1", "admin", "secret")

        assert result.success is False
        assert "failed" in result.message.lower()


class TestLoadCredentialsKeyring:
    """Tests for load_credentials_keyring function."""

    @patch("mountrix.core.credentials.is_keyring_available")
    @patch("mountrix.core.credentials.keyring")
    def test_load_success(self, mock_keyring, mock_available):
        """Test successful load from keyring."""
        mock_available.return_value = True
        mock_keyring.get_password.return_value = "secret"

        success, password = load_credentials_keyring("nas1", "admin")

        assert success is True
        assert password == "secret"
        mock_keyring.get_password.assert_called_once_with("nas1", "admin")

    @patch("mountrix.core.credentials.is_keyring_available")
    @patch("mountrix.core.credentials.keyring")
    def test_load_not_found(self, mock_keyring, mock_available):
        """Test load when credentials not found."""
        mock_available.return_value = True
        mock_keyring.get_password.return_value = None

        success, password = load_credentials_keyring("nas1", "admin")

        assert success is False
        assert password is None

    @patch("mountrix.core.credentials.is_keyring_available")
    def test_load_keyring_not_available(self, mock_available):
        """Test load when keyring is not available."""
        mock_available.return_value = False

        success, password = load_credentials_keyring("nas1", "admin")

        assert success is False
        assert password is None

    def test_load_empty_service(self):
        """Test load with empty service."""
        success, password = load_credentials_keyring("", "admin")

        assert success is False
        assert password is None

    @patch("mountrix.core.credentials.is_keyring_available")
    @patch("mountrix.core.credentials.keyring")
    def test_load_exception(self, mock_keyring, mock_available):
        """Test load when keyring raises exception."""
        mock_available.return_value = True
        mock_keyring.get_password.side_effect = Exception("Error")

        success, password = load_credentials_keyring("nas1", "admin")

        assert success is False
        assert password is None


class TestDeleteCredentialsKeyring:
    """Tests for delete_credentials_keyring function."""

    @patch("mountrix.core.credentials.is_keyring_available")
    @patch("mountrix.core.credentials.keyring")
    def test_delete_success(self, mock_keyring, mock_available):
        """Test successful delete from keyring."""
        mock_available.return_value = True

        result = delete_credentials_keyring("nas1", "admin")

        assert result.success is True
        assert "deleted" in result.message.lower()
        mock_keyring.delete_password.assert_called_once_with("nas1", "admin")

    @patch("mountrix.core.credentials.is_keyring_available")
    def test_delete_keyring_not_available(self, mock_available):
        """Test delete when keyring not available."""
        mock_available.return_value = False

        result = delete_credentials_keyring("nas1", "admin")

        assert result.success is False


class TestGenerateCredentialsFile:
    """Tests for generate_credentials_file function."""

    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.chmod")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.home")
    def test_generate_file_success(self, mock_home, mock_mkdir, mock_chmod, mock_write):
        """Test successful credential file generation."""
        mock_home.return_value = Path("/home/testuser")

        result = generate_credentials_file("admin", "secret", "WORKGROUP")

        assert result.success is True
        assert result.file_path is not None
        assert ".mountrix/credentials" in result.file_path
        assert result.username == "admin"

        # Verify write was called with correct content
        write_call = mock_write.call_args[0][0]
        assert "username=admin" in write_call
        assert "password=secret" in write_call
        assert "domain=WORKGROUP" in write_call

    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.chmod")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.home")
    def test_generate_file_without_domain(self, mock_home, mock_mkdir, mock_chmod, mock_write):
        """Test generating file without domain."""
        mock_home.return_value = Path("/home/testuser")

        result = generate_credentials_file("admin", "secret")

        assert result.success is True

        write_call = mock_write.call_args[0][0]
        assert "username=admin" in write_call
        assert "password=secret" in write_call
        assert "domain=" not in write_call

    def test_generate_file_empty_username(self):
        """Test with empty username."""
        result = generate_credentials_file("", "secret")

        assert result.success is False
        assert "required" in result.message.lower()

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.home")
    def test_generate_file_mkdir_error(self, mock_home, mock_mkdir):
        """Test error creating credentials directory."""
        mock_home.return_value = Path("/home/testuser")
        mock_mkdir.side_effect = PermissionError("Permission denied")

        result = generate_credentials_file("admin", "secret")

        assert result.success is False
        assert "failed to create" in result.message.lower()

    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.chmod")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.home")
    def test_generate_file_write_error(self, mock_home, mock_mkdir, mock_chmod, mock_write):
        """Test error writing credential file."""
        mock_home.return_value = Path("/home/testuser")
        mock_write.side_effect = IOError("Disk full")

        result = generate_credentials_file("admin", "secret")

        assert result.success is False
        assert "failed to create" in result.message.lower()


class TestDeleteCredentialsFile:
    """Tests for delete_credentials_file function."""

    @patch("pathlib.Path.unlink")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.home")
    def test_delete_file_success(self, mock_home, mock_exists, mock_unlink):
        """Test successful file deletion."""
        mock_home.return_value = Path("/home/testuser")
        mock_exists.return_value = True

        file_path = "/home/testuser/.mountrix/credentials/test.cred"
        result = delete_credentials_file(file_path)

        assert result.success is True
        assert "deleted" in result.message.lower()
        mock_unlink.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.home")
    def test_delete_file_not_exists(self, mock_home, mock_exists):
        """Test delete when file doesn't exist."""
        mock_home.return_value = Path("/home/testuser")
        mock_exists.return_value = False

        file_path = "/home/testuser/.mountrix/credentials/test.cred"
        result = delete_credentials_file(file_path)

        assert result.success is True
        assert "does not exist" in result.message.lower()

    def test_delete_file_empty_path(self):
        """Test delete with empty path."""
        result = delete_credentials_file("")

        assert result.success is False
        assert "required" in result.message.lower()

    @patch("pathlib.Path.home")
    def test_delete_file_security_check(self, mock_home):
        """Test security check prevents deleting files outside credentials dir."""
        mock_home.return_value = Path("/home/testuser")

        # Try to delete a file outside .mountrix/credentials/
        file_path = "/etc/passwd"
        result = delete_credentials_file(file_path)

        assert result.success is False
        assert "security" in result.message.lower()


class TestValidateSshKey:
    """Tests for validate_ssh_key function."""

    def test_validate_empty_path(self):
        """Test with empty path."""
        valid, error = validate_ssh_key("")

        assert valid is False
        assert "required" in error.lower()

    @patch("pathlib.Path.exists")
    def test_validate_file_not_exists(self, mock_exists):
        """Test when file doesn't exist."""
        mock_exists.return_value = False

        valid, error = validate_ssh_key("/home/user/.ssh/id_rsa")

        assert valid is False
        assert "does not exist" in error.lower()

    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.exists")
    def test_validate_not_a_file(self, mock_exists, mock_is_file):
        """Test when path is not a file."""
        mock_exists.return_value = True
        mock_is_file.return_value = False

        valid, error = validate_ssh_key("/home/user/.ssh")

        assert valid is False
        assert "not a file" in error.lower()

    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.stat")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.exists")
    def test_validate_insecure_permissions(self, mock_exists, mock_is_file, mock_stat, mock_read):
        """Test with insecure permissions."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        # Mock file with 644 permissions (readable by group and others)
        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
        mock_stat.return_value = mock_stat_result

        valid, error = validate_ssh_key("/home/user/.ssh/id_rsa")

        assert valid is False
        assert "insecure permissions" in error.lower()

    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.stat")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.exists")
    def test_validate_valid_rsa_key(self, mock_exists, mock_is_file, mock_stat, mock_read):
        """Test with valid RSA key."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        # Mock file with 600 permissions
        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IWUSR
        mock_stat.return_value = mock_stat_result

        mock_read.return_value = "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----"

        valid, error = validate_ssh_key("/home/user/.ssh/id_rsa")

        assert valid is True
        assert "valid" in error.lower()

    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.stat")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.exists")
    def test_validate_openssh_key(self, mock_exists, mock_is_file, mock_stat, mock_read):
        """Test with OpenSSH format key."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IWUSR
        mock_stat.return_value = mock_stat_result

        mock_read.return_value = "-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----"

        valid, error = validate_ssh_key("/home/user/.ssh/id_ed25519")

        assert valid is True

    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.stat")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.exists")
    def test_validate_invalid_content(self, mock_exists, mock_is_file, mock_stat, mock_read):
        """Test with invalid key content."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IWUSR
        mock_stat.return_value = mock_stat_result

        mock_read.return_value = "This is not an SSH key"

        valid, error = validate_ssh_key("/home/user/.ssh/id_rsa")

        assert valid is False
        assert "not appear to be" in error.lower()


class TestGetCredentialFiles:
    """Tests for get_credential_files function."""

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.home")
    def test_get_files_success(self, mock_home, mock_exists, mock_glob):
        """Test getting credential files."""
        mock_home.return_value = Path("/home/testuser")
        mock_exists.return_value = True

        # Mock glob to return some files
        mock_file1 = MagicMock(spec=Path)
        mock_file1.is_file.return_value = True
        mock_file1.__str__ = lambda x: "/home/testuser/.mountrix/credentials/file1.cred"

        mock_file2 = MagicMock(spec=Path)
        mock_file2.is_file.return_value = True
        mock_file2.__str__ = lambda x: "/home/testuser/.mountrix/credentials/file2.cred"

        mock_glob.return_value = [mock_file1, mock_file2]

        files = get_credential_files()

        assert len(files) == 2
        assert all(".cred" in f for f in files)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.home")
    def test_get_files_dir_not_exists(self, mock_home, mock_exists):
        """Test when credentials directory doesn't exist."""
        mock_home.return_value = Path("/home/testuser")
        mock_exists.return_value = False

        files = get_credential_files()

        assert files == []


class TestReadCredentialsFile:
    """Tests for read_credentials_file function."""

    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_read_file_success(self, mock_exists, mock_read):
        """Test reading credential file."""
        mock_exists.return_value = True
        mock_read.return_value = "username=admin\npassword=secret\ndomain=WORKGROUP\n"

        success, creds = read_credentials_file("/path/to/file.cred")

        assert success is True
        assert creds["username"] == "admin"
        assert creds["password"] == "secret"
        assert creds["domain"] == "WORKGROUP"

    @patch("pathlib.Path.exists")
    def test_read_file_not_exists(self, mock_exists):
        """Test reading non-existent file."""
        mock_exists.return_value = False

        success, creds = read_credentials_file("/path/to/file.cred")

        assert success is False
        assert creds == {}

    def test_read_file_empty_path(self):
        """Test with empty path."""
        success, creds = read_credentials_file("")

        assert success is False
        assert creds == {}

    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_read_file_error(self, mock_exists, mock_read):
        """Test error reading file."""
        mock_exists.return_value = True
        mock_read.side_effect = IOError("Read error")

        success, creds = read_credentials_file("/path/to/file.cred")

        assert success is False
        assert creds == {}
