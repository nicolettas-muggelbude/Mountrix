# -*- coding: utf-8 -*-
"""
Tests for detector.py

Tests desktop environment detection and drive detection functionality.
"""

import json
import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from mountrix.core.detector import (
    DesktopEnvironment,
    Drive,
    DriveType,
    NetworkShare,
    detect_desktop_environment,
    detect_local_drives,
    get_filesystem_type,
    scan_network_shares,
)


class TestDesktopEnvironment:
    """Tests for desktop environment detection."""

    def test_detect_gnome_via_xdg(self, monkeypatch):
        """Test GNOME detection via XDG_CURRENT_DESKTOP."""
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME")
        assert detect_desktop_environment() == DesktopEnvironment.GNOME

    def test_detect_kde_via_xdg(self, monkeypatch):
        """Test KDE detection via XDG_CURRENT_DESKTOP."""
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "KDE")
        assert detect_desktop_environment() == DesktopEnvironment.KDE

    def test_detect_xfce_via_xdg(self, monkeypatch):
        """Test XFCE detection via XDG_CURRENT_DESKTOP."""
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "XFCE")
        assert detect_desktop_environment() == DesktopEnvironment.XFCE

    def test_detect_cinnamon_via_xdg(self, monkeypatch):
        """Test Cinnamon detection via XDG_CURRENT_DESKTOP."""
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "X-Cinnamon")
        assert detect_desktop_environment() == DesktopEnvironment.CINNAMON

    def test_detect_lxqt_via_xdg(self, monkeypatch):
        """Test LXQt detection via XDG_CURRENT_DESKTOP."""
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "LXQt")
        assert detect_desktop_environment() == DesktopEnvironment.LXQT

    def test_detect_kde_via_desktop_session(self, monkeypatch):
        """Test KDE detection via DESKTOP_SESSION fallback."""
        monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)
        monkeypatch.setenv("DESKTOP_SESSION", "plasma")
        assert detect_desktop_environment() == DesktopEnvironment.KDE

    def test_detect_unknown_desktop(self, monkeypatch):
        """Test unknown desktop when no env vars set."""
        monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)
        monkeypatch.delenv("DESKTOP_SESSION", raising=False)
        assert detect_desktop_environment() == DesktopEnvironment.UNKNOWN


class TestFilesystemType:
    """Tests for filesystem type detection."""

    @patch("subprocess.run")
    def test_get_filesystem_type_ext4(self, mock_run):
        """Test detecting ext4 filesystem."""
        mock_run.return_value = MagicMock(stdout="ext4\n", returncode=0)
        assert get_filesystem_type("/dev/sda1") == "ext4"

    @patch("subprocess.run")
    def test_get_filesystem_type_ntfs(self, mock_run):
        """Test detecting NTFS filesystem."""
        mock_run.return_value = MagicMock(stdout="ntfs\n", returncode=0)
        assert get_filesystem_type("/dev/sdb1") == "ntfs"

    @patch("subprocess.run")
    def test_get_filesystem_type_unknown(self, mock_run):
        """Test unknown filesystem when command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "lsblk")
        assert get_filesystem_type("/dev/sdc1") == "unknown"

    @patch("subprocess.run")
    def test_get_filesystem_type_empty(self, mock_run):
        """Test empty filesystem output."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        assert get_filesystem_type("/dev/sdd1") == "unknown"


class TestDriveDetection:
    """Tests for local drive detection."""

    @patch("subprocess.run")
    def test_detect_local_drives_with_lsblk(self, mock_run):
        """Test drive detection with lsblk."""
        lsblk_output = {
            "blockdevices": [
                {
                    "name": "sda",
                    "type": "disk",
                    "size": 1000204886016,
                    "fstype": None,
                    "mountpoint": None,
                    "label": None,
                    "uuid": None,
                    "children": [
                        {
                            "name": "sda1",
                            "type": "part",
                            "size": 536870912,
                            "fstype": "ext4",
                            "mountpoint": "/boot",
                            "label": "BOOT",
                            "uuid": "abc-123",
                        },
                        {
                            "name": "sda2",
                            "type": "part",
                            "size": 999668015104,
                            "fstype": "ext4",
                            "mountpoint": "/",
                            "label": "ROOT",
                            "uuid": "def-456",
                        },
                    ],
                },
                {
                    "name": "nvme0n1",
                    "type": "disk",
                    "size": 512110190592,
                    "fstype": None,
                    "mountpoint": None,
                    "label": None,
                    "uuid": None,
                    "children": [
                        {
                            "name": "nvme0n1p1",
                            "type": "part",
                            "size": 512110190592,
                            "fstype": "ntfs",
                            "mountpoint": "/mnt/data",
                            "label": "Data",
                            "uuid": "ghi-789",
                        }
                    ],
                },
            ]
        }

        mock_run.return_value = MagicMock(
            stdout=json.dumps(lsblk_output), returncode=0
        )

        drives = detect_local_drives()

        assert len(drives) == 3
        
        # Check first drive (sda1)
        assert drives[0].device == "/dev/sda1"
        assert drives[0].name == "BOOT"
        assert drives[0].filesystem == "ext4"
        assert drives[0].mountpoint == "/boot"
        assert drives[0].drive_type == DriveType.SATA
        assert drives[0].is_mounted == True
        
        # Check second drive (sda2)
        assert drives[1].device == "/dev/sda2"
        assert drives[1].name == "ROOT"
        
        # Check NVMe drive
        assert drives[2].device == "/dev/nvme0n1p1"
        assert drives[2].drive_type == DriveType.NVME
        assert drives[2].filesystem == "ntfs"

    @patch("subprocess.run")
    @patch("psutil.disk_partitions")
    @patch("psutil.disk_usage")
    def test_detect_local_drives_fallback_psutil(
        self, mock_usage, mock_partitions, mock_run
    ):
        """Test drive detection fallback to psutil."""
        # Make lsblk fail
        mock_run.side_effect = subprocess.CalledProcessError(1, "lsblk")

        # Mock psutil
        mock_partitions.return_value = [
            MagicMock(
                device="/dev/sda1",
                mountpoint="/",
                fstype="ext4",
            )
        ]
        mock_usage.return_value = MagicMock(total=1000000000000)

        drives = detect_local_drives()

        assert len(drives) == 1
        assert drives[0].device == "/dev/sda1"
        assert drives[0].filesystem == "ext4"
        assert drives[0].size_bytes == 1000000000000


class TestDriveClass:
    """Tests for Drive dataclass."""

    def test_drive_size_gb(self):
        """Test size_gb property."""
        drive = Drive(
            device="/dev/sda1",
            name="Test",
            drive_type=DriveType.SATA,
            filesystem="ext4",
            size_bytes=1073741824,  # 1 GB
        )
        assert drive.size_gb == pytest.approx(1.0, rel=0.01)

    def test_drive_is_mounted(self):
        """Test is_mounted property."""
        drive_mounted = Drive(
            device="/dev/sda1",
            name="Test",
            drive_type=DriveType.SATA,
            filesystem="ext4",
            size_bytes=1000000,
            mountpoint="/mnt/test",
        )
        assert drive_mounted.is_mounted == True

        drive_not_mounted = Drive(
            device="/dev/sda2",
            name="Test2",
            drive_type=DriveType.SATA,
            filesystem="ext4",
            size_bytes=1000000,
        )
        assert drive_not_mounted.is_mounted == False


class TestNetworkShares:
    """Tests for network share scanning."""

    def test_scan_network_shares_empty(self):
        """Test that scan_network_shares returns empty list (TODO)."""
        shares = scan_network_shares()
        assert isinstance(shares, list)
        assert len(shares) == 0


class TestNetworkShareClass:
    """Tests for NetworkShare dataclass."""

    def test_network_share_creation(self):
        """Test creating a NetworkShare."""
        share = NetworkShare(
            protocol="smb",
            host="192.168.1.100",
            share_path="/data",
            name="My NAS",
        )
        assert share.protocol == "smb"
        assert share.host == "192.168.1.100"
        assert share.share_path == "/data"
        assert share.name == "My NAS"
