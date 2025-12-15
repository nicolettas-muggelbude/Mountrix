# -*- coding: utf-8 -*-
"""
Tests for mounter.py

Tests mount/unmount operations and mountpoint management.
"""

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from mountrix.core.fstab import FstabEntry
from mountrix.core.mounter import (
    MountResult,
    create_mountpoint,
    get_current_username,
    get_mount_info,
    mount_entry,
    remount_entry,
    unmount_entry,
    verify_mount,
)


class TestGetCurrentUsername:
    """Tests for get_current_username function."""

    def test_get_username_from_user_env(self, monkeypatch):
        """Test getting username from USER environment variable."""
        monkeypatch.setenv("USER", "testuser")
        assert get_current_username() == "testuser"

    def test_get_username_from_username_env(self, monkeypatch):
        """Test getting username from USERNAME environment variable."""
        monkeypatch.delenv("USER", raising=False)
        monkeypatch.setenv("USERNAME", "windowsuser")
        assert get_current_username() == "windowsuser"

    def test_get_username_fallback(self, monkeypatch):
        """Test fallback when no username env vars are set."""
        monkeypatch.delenv("USER", raising=False)
        monkeypatch.delenv("USERNAME", raising=False)
        assert get_current_username() == "user"


class TestCreateMountpoint:
    """Tests for create_mountpoint function."""

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    @patch("mountrix.core.mounter.get_current_username")
    def test_create_user_mountpoint(self, mock_username, mock_exists, mock_mkdir):
        """Test creating user-specific mountpoint."""
        mock_username.return_value = "testuser"
        mock_exists.return_value = False

        result = create_mountpoint("nas_data", user_only=True)

        assert result.success is True
        assert "/media/testuser/nas_data" in result.mountpoint
        mock_mkdir.assert_called_once()

    @patch("pathlib.Path.chmod")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    def test_create_system_mountpoint(self, mock_exists, mock_mkdir, mock_chmod):
        """Test creating system-wide mountpoint."""
        mock_exists.return_value = False

        result = create_mountpoint("nas_data", user_only=False)

        assert result.success is True
        assert "/mnt/nas_data" in result.mountpoint
        mock_mkdir.assert_called_once()

    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_create_mountpoint_already_exists(self, mock_exists, mock_is_dir):
        """Test when mountpoint already exists."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True

        result = create_mountpoint("existing", user_only=False)

        assert result.success is True
        assert "already exists" in result.message.lower()

    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_create_mountpoint_exists_not_dir(self, mock_exists, mock_is_dir):
        """Test when path exists but is not a directory."""
        mock_exists.return_value = True
        mock_is_dir.return_value = False

        result = create_mountpoint("file", user_only=False)

        assert result.success is False
        assert "not a directory" in result.message.lower()

    def test_create_mountpoint_empty_path(self):
        """Test with empty path."""
        result = create_mountpoint("")
        assert result.success is False
        assert "cannot be empty" in result.message.lower()

    @patch("pathlib.Path.chmod")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    def test_create_mountpoint_sanitizes_path(self, mock_exists, mock_mkdir, mock_chmod):
        """Test that path is sanitized."""
        mock_exists.return_value = False

        result = create_mountpoint("/../dangerous/../../path", user_only=False)

        assert result.success is True
        # Path should be sanitized (no .. allowed)
        assert ".." not in result.mountpoint

    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    def test_create_mountpoint_permission_error(self, mock_exists, mock_mkdir):
        """Test permission error when creating mountpoint."""
        mock_exists.return_value = False
        mock_mkdir.side_effect = PermissionError("Permission denied")

        result = create_mountpoint("nas", user_only=False)

        assert result.success is False
        assert "permission denied" in result.message.lower()


class TestMountEntry:
    """Tests for mount_entry function."""

    @patch("subprocess.run")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_mount_success(self, mock_exists, mock_is_dir, mock_run):
        """Test successful mount."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")

        entry = FstabEntry(
            source="//nas/public", mountpoint="/mnt/nas", fstype="cifs"
        )

        result = mount_entry(entry)

        assert result.success is True
        assert "successfully mounted" in result.message.lower()
        assert result.mountpoint == "/mnt/nas"

        # Verify mount command
        mount_call = mock_run.call_args[0][0]
        assert mount_call[0] == "mount"
        assert "-t" in mount_call
        assert "cifs" in mount_call

    @patch("subprocess.run")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_mount_with_options(self, mock_exists, mock_is_dir, mock_run):
        """Test mount with options."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")

        entry = FstabEntry(
            source="192.168.1.100:/data",
            mountpoint="/mnt/nfs",
            fstype="nfs",
            options=["ro", "soft", "nofail"],
        )

        result = mount_entry(entry)

        assert result.success is True

        # Verify options are passed
        mount_call = mock_run.call_args[0][0]
        assert "-o" in mount_call
        opts_index = mount_call.index("-o") + 1
        assert "ro,soft,nofail" == mount_call[opts_index]

    @patch("pathlib.Path.exists")
    def test_mount_mountpoint_not_exists(self, mock_exists):
        """Test mount when mountpoint doesn't exist."""
        mock_exists.return_value = False

        entry = FstabEntry(
            source="//nas/share", mountpoint="/mnt/nonexistent", fstype="cifs"
        )

        result = mount_entry(entry)

        assert result.success is False
        assert "does not exist" in result.message.lower()

    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_mount_mountpoint_not_dir(self, mock_exists, mock_is_dir):
        """Test mount when mountpoint is not a directory."""
        mock_exists.return_value = True
        mock_is_dir.return_value = False

        entry = FstabEntry(
            source="//nas/share", mountpoint="/mnt/file", fstype="cifs"
        )

        result = mount_entry(entry)

        assert result.success is False
        assert "not a directory" in result.message.lower()

    def test_mount_invalid_entry(self):
        """Test mount with invalid entry."""
        result = mount_entry(None)
        assert result.success is False
        assert "invalid" in result.message.lower()

        # Missing source
        entry = FstabEntry(source="", mountpoint="/mnt/test", fstype="nfs")
        result = mount_entry(entry)
        assert result.success is False

    @patch("subprocess.run")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_mount_failure(self, mock_exists, mock_is_dir, mock_run):
        """Test mount failure."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_run.return_value = MagicMock(
            returncode=32, stderr="mount error: access denied", stdout=""
        )

        entry = FstabEntry(
            source="//nas/private", mountpoint="/mnt/nas", fstype="cifs"
        )

        result = mount_entry(entry)

        assert result.success is False
        assert "failed" in result.message.lower()
        assert result.error_code == 32

    @patch("subprocess.run")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.exists")
    def test_mount_timeout(self, mock_exists, mock_is_dir, mock_run):
        """Test mount timeout."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired("mount", 30)

        entry = FstabEntry(source="//nas/share", mountpoint="/mnt/nas", fstype="cifs")

        result = mount_entry(entry)

        assert result.success is False
        assert "timed out" in result.message.lower()


class TestUnmountEntry:
    """Tests for unmount_entry function."""

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_unmount_success(self, mock_exists, mock_run):
        """Test successful unmount."""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")

        result = unmount_entry("/mnt/nas")

        assert result.success is True
        assert "successfully unmounted" in result.message.lower()
        assert result.mountpoint == "/mnt/nas"

        # Verify umount command
        umount_call = mock_run.call_args[0][0]
        assert umount_call[0] == "umount"
        assert "/mnt/nas" in umount_call

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_unmount_force(self, mock_exists, mock_run):
        """Test force unmount."""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")

        result = unmount_entry("/mnt/nas", force=True)

        assert result.success is True

        # Verify force flag
        umount_call = mock_run.call_args[0][0]
        assert "-f" in umount_call

    def test_unmount_empty_mountpoint(self):
        """Test unmount with empty mountpoint."""
        result = unmount_entry("")
        assert result.success is False
        assert "cannot be empty" in result.message.lower()

    @patch("pathlib.Path.exists")
    def test_unmount_nonexistent_mountpoint(self, mock_exists):
        """Test unmount when mountpoint doesn't exist."""
        mock_exists.return_value = False

        result = unmount_entry("/mnt/nonexistent")

        assert result.success is False
        assert "does not exist" in result.message.lower()

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_unmount_not_mounted(self, mock_exists, mock_run):
        """Test unmount when already not mounted."""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=32, stderr="not mounted", stdout=""
        )

        result = unmount_entry("/mnt/nas")

        # Should still be success since the end result is unmounted
        assert result.success is True
        assert "not mounted" in result.message.lower()

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_unmount_device_busy(self, mock_exists, mock_run):
        """Test unmount when device is busy."""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=16, stderr="umount: target is busy", stdout=""
        )

        result = unmount_entry("/mnt/nas")

        assert result.success is False
        assert "busy" in result.message.lower()

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_unmount_timeout(self, mock_exists, mock_run):
        """Test unmount timeout."""
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired("umount", 30)

        result = unmount_entry("/mnt/nas")

        assert result.success is False
        assert "timed out" in result.message.lower()


class TestVerifyMount:
    """Tests for verify_mount function."""

    def test_verify_mount_empty_mountpoint(self):
        """Test with empty mountpoint."""
        assert verify_mount("") is False

    @patch("builtins.open", new_callable=mock_open, read_data="/dev/sda1 /mnt/nas ext4 rw 0 0\n")
    def test_verify_mount_is_mounted(self, mock_file):
        """Test when mountpoint is mounted."""
        assert verify_mount("/mnt/nas") is True

    @patch("builtins.open", new_callable=mock_open, read_data="/dev/sda1 /mnt/other ext4 rw 0 0\n")
    def test_verify_mount_not_mounted(self, mock_file):
        """Test when mountpoint is not mounted."""
        assert verify_mount("/mnt/nas") is False

    @patch("builtins.open", new_callable=mock_open, read_data="//nas/share /mnt/nas\\040data cifs rw 0 0\n")
    def test_verify_mount_with_escaped_spaces(self, mock_file):
        """Test mountpoint with escaped spaces."""
        assert verify_mount("/mnt/nas data") is True

    @patch("builtins.open")
    @patch("subprocess.run")
    def test_verify_mount_fallback_to_command(self, mock_run, mock_open_func):
        """Test fallback to mount command when /proc/mounts doesn't exist."""
        mock_open_func.side_effect = FileNotFoundError()
        mock_run.return_value = MagicMock(
            returncode=0, stdout="/dev/sda1 on /mnt/nas type ext4 (rw)\n"
        )

        assert verify_mount("/mnt/nas") is True

    @patch("builtins.open")
    def test_verify_mount_error_handling(self, mock_open_func):
        """Test error handling."""
        mock_open_func.side_effect = Exception("Unexpected error")

        # Should return False on error, not raise
        assert verify_mount("/mnt/nas") is False


class TestGetMountInfo:
    """Tests for get_mount_info function."""

    @patch("mountrix.core.mounter.verify_mount")
    def test_get_mount_info_not_mounted(self, mock_verify):
        """Test getting info when not mounted."""
        mock_verify.return_value = False

        result = get_mount_info("/mnt/nas")

        assert result is None

    @patch("builtins.open", new_callable=mock_open, read_data="//nas/share /mnt/nas cifs rw,user=test 0 0\n")
    @patch("mountrix.core.mounter.verify_mount")
    def test_get_mount_info_success(self, mock_verify, mock_file):
        """Test getting mount info successfully."""
        mock_verify.return_value = True

        result = get_mount_info("/mnt/nas")

        assert result is not None
        assert result["source"] == "//nas/share"
        assert result["mountpoint"] == "/mnt/nas"
        assert result["fstype"] == "cifs"
        assert "rw" in result["options"]
        assert "user=test" in result["options"]

    @patch("builtins.open")
    @patch("mountrix.core.mounter.verify_mount")
    def test_get_mount_info_error(self, mock_verify, mock_open_func):
        """Test error handling."""
        mock_verify.return_value = True
        mock_open_func.side_effect = Exception("Error")

        result = get_mount_info("/mnt/nas")

        assert result is None


class TestRemountEntry:
    """Tests for remount_entry function."""

    @patch("mountrix.core.mounter.mount_entry")
    @patch("mountrix.core.mounter.unmount_entry")
    @patch("mountrix.core.mounter.verify_mount")
    def test_remount_currently_mounted(
        self, mock_verify, mock_unmount, mock_mount
    ):
        """Test remounting when currently mounted."""
        mock_verify.return_value = True
        mock_unmount.return_value = MountResult(success=True, message="Unmounted")
        mock_mount.return_value = MountResult(success=True, message="Mounted")

        entry = FstabEntry(
            source="//nas/share", mountpoint="/mnt/nas", fstype="cifs"
        )

        result = remount_entry(entry)

        assert result.success is True
        mock_unmount.assert_called_once_with("/mnt/nas")
        mock_mount.assert_called_once_with(entry)

    @patch("mountrix.core.mounter.mount_entry")
    @patch("mountrix.core.mounter.verify_mount")
    def test_remount_not_currently_mounted(self, mock_verify, mock_mount):
        """Test remounting when not currently mounted."""
        mock_verify.return_value = False
        mock_mount.return_value = MountResult(success=True, message="Mounted")

        entry = FstabEntry(
            source="//nas/share", mountpoint="/mnt/nas", fstype="cifs"
        )

        result = remount_entry(entry)

        assert result.success is True
        mock_mount.assert_called_once_with(entry)

    @patch("mountrix.core.mounter.unmount_entry")
    @patch("mountrix.core.mounter.verify_mount")
    def test_remount_unmount_fails(self, mock_verify, mock_unmount):
        """Test remount when unmount fails."""
        mock_verify.return_value = True
        mock_unmount.return_value = MountResult(
            success=False, message="Unmount failed"
        )

        entry = FstabEntry(
            source="//nas/share", mountpoint="/mnt/nas", fstype="cifs"
        )

        result = remount_entry(entry)

        assert result.success is False
        assert "failed to unmount" in result.message.lower()

    def test_remount_invalid_entry(self):
        """Test remount with invalid entry."""
        result = remount_entry(None)
        assert result.success is False
        assert "invalid" in result.message.lower()
