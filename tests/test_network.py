# -*- coding: utf-8 -*-
"""
Tests for network.py

Tests network diagnostics and mount testing functionality.
"""

import socket
import subprocess
from unittest.mock import MagicMock, Mock, patch

import pytest

from mountrix.core.fstab import FstabEntry
from mountrix.core.network import (
    MountTestResult,
    check_port,
    diagnose_connection,
    get_common_nas_ports,
    ping_host,
    resolve_hostname,
    verify_mount_temporary,
    verify_nfs_mount,
    verify_smb_mount,
)


class TestPingHost:
    """Tests for ping_host function."""

    @patch("subprocess.run")
    def test_ping_successful(self, mock_run):
        """Test successful ping."""
        mock_run.return_value = MagicMock(returncode=0)
        assert ping_host("192.168.1.1") is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ping" in args
        assert "192.168.1.1" in args

    @patch("subprocess.run")
    def test_ping_failed(self, mock_run):
        """Test failed ping (host unreachable)."""
        mock_run.return_value = MagicMock(returncode=1)
        assert ping_host("192.168.1.99") is False

    @patch("subprocess.run")
    def test_ping_timeout(self, mock_run):
        """Test ping timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("ping", 5)
        assert ping_host("192.168.1.1") is False

    def test_ping_empty_host(self):
        """Test ping with empty host."""
        assert ping_host("") is False

    @patch("subprocess.run")
    def test_ping_custom_timeout(self, mock_run):
        """Test ping with custom timeout."""
        mock_run.return_value = MagicMock(returncode=0)
        ping_host("192.168.1.1", timeout=5, count=3)
        args = mock_run.call_args[0][0]
        assert "5" in args  # timeout
        assert "3" in args  # count


class TestCheckPort:
    """Tests for check_port function."""

    @patch("socket.socket")
    def test_port_open(self, mock_socket_class):
        """Test checking open port."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket

        assert check_port("192.168.1.1", 445) is True
        mock_socket.connect_ex.assert_called_once_with(("192.168.1.1", 445))
        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_port_closed(self, mock_socket_class):
        """Test checking closed port."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 1
        mock_socket_class.return_value = mock_socket

        assert check_port("192.168.1.1", 445) is False

    @patch("socket.socket")
    def test_port_timeout(self, mock_socket_class):
        """Test port check timeout."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.side_effect = socket.timeout()
        mock_socket_class.return_value = mock_socket

        assert check_port("192.168.1.1", 445) is False

    def test_port_invalid_port_number(self):
        """Test with invalid port numbers."""
        assert check_port("192.168.1.1", 0) is False
        assert check_port("192.168.1.1", 65536) is False
        assert check_port("192.168.1.1", -1) is False

    def test_port_empty_host(self):
        """Test with empty host."""
        assert check_port("", 445) is False

    @patch("socket.socket")
    def test_port_socket_error(self, mock_socket_class):
        """Test socket error handling."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.side_effect = socket.error()
        mock_socket_class.return_value = mock_socket

        assert check_port("192.168.1.1", 445) is False


class TestResolveHostname:
    """Tests for resolve_hostname function."""

    @patch("socket.gethostbyname")
    def test_resolve_hostname_success(self, mock_gethostbyname):
        """Test successful hostname resolution."""
        mock_gethostbyname.return_value = "192.168.1.100"
        result = resolve_hostname("nas.local")
        assert result == "192.168.1.100"

    @patch("socket.gethostbyname")
    def test_resolve_hostname_failure(self, mock_gethostbyname):
        """Test failed hostname resolution."""
        mock_gethostbyname.side_effect = socket.gaierror()
        result = resolve_hostname("nonexistent.local")
        assert result is None

    @patch("socket.gethostbyname")
    def test_resolve_hostname_timeout(self, mock_gethostbyname):
        """Test hostname resolution timeout."""
        mock_gethostbyname.side_effect = socket.timeout()
        result = resolve_hostname("slow.local")
        assert result is None

    def test_resolve_already_ip(self):
        """Test resolving what's already an IP address."""
        result = resolve_hostname("192.168.1.1")
        assert result == "192.168.1.1"

    def test_resolve_empty_hostname(self):
        """Test with empty hostname."""
        result = resolve_hostname("")
        assert result is None

    @patch("socket.gethostbyname")
    def test_resolve_localhost(self, mock_gethostbyname):
        """Test resolving localhost."""
        mock_gethostbyname.return_value = "127.0.0.1"
        result = resolve_hostname("localhost")
        assert result == "127.0.0.1"


class TestNfsMount:
    """Tests for verify_nfs_mount function."""

    @patch("subprocess.run")
    @patch("tempfile.mkdtemp")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.rmdir")
    def test_nfs_mount_success(self, mock_rmdir, mock_exists, mock_mkdtemp, mock_run):
        """Test successful NFS mount test."""
        mock_mkdtemp.return_value = "/tmp/mountrix_test_nfs_12345"
        mock_exists.return_value = True

        # First call: mount (success), second call: umount
        mock_run.side_effect = [
            MagicMock(returncode=0, stderr="", stdout=""),
            MagicMock(returncode=0),
        ]

        result = verify_nfs_mount("192.168.1.100", "/data")
        assert result.success is True
        assert "successful" in result.message.lower()
        assert result.error_code is None

    @patch("subprocess.run")
    @patch("tempfile.mkdtemp")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.rmdir")
    def test_nfs_mount_failure(self, mock_rmdir, mock_exists, mock_mkdtemp, mock_run):
        """Test failed NFS mount test."""
        mock_mkdtemp.return_value = "/tmp/mountrix_test_nfs_12345"
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=32, stderr="mount.nfs: access denied", stdout=""
        )

        result = verify_nfs_mount("192.168.1.100", "/data")
        assert result.success is False
        assert "failed" in result.message.lower()
        assert result.error_code == 32

    @patch("subprocess.run")
    @patch("tempfile.mkdtemp")
    def test_nfs_mount_timeout(self, mock_mkdtemp, mock_run):
        """Test NFS mount timeout."""
        mock_mkdtemp.return_value = "/tmp/mountrix_test_nfs_12345"
        mock_run.side_effect = subprocess.TimeoutExpired("mount", 10)

        result = verify_nfs_mount("192.168.1.100", "/data")
        assert result.success is False
        assert "timed out" in result.message.lower()

    def test_nfs_mount_empty_params(self):
        """Test NFS mount with empty parameters."""
        result = verify_nfs_mount("", "/data")
        assert result.success is False
        assert "required" in result.message.lower()

        result = verify_nfs_mount("192.168.1.100", "")
        assert result.success is False


class TestSmbMount:
    """Tests for verify_smb_mount function."""

    @patch("subprocess.run")
    @patch("tempfile.mkdtemp")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.rmdir")
    def test_smb_mount_success(self, mock_rmdir, mock_exists, mock_mkdtemp, mock_run):
        """Test successful SMB mount test."""
        mock_mkdtemp.return_value = "/tmp/mountrix_test_smb_12345"
        mock_exists.return_value = True

        # First call: mount (success), second call: umount
        mock_run.side_effect = [
            MagicMock(returncode=0, stderr="", stdout=""),
            MagicMock(returncode=0),
        ]

        result = verify_smb_mount("192.168.1.100", "public")
        assert result.success is True
        assert "successful" in result.message.lower()

    @patch("subprocess.run")
    @patch("tempfile.mkdtemp")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.rmdir")
    def test_smb_mount_with_credentials(
        self, mock_rmdir, mock_exists, mock_mkdtemp, mock_run
    ):
        """Test SMB mount with username and password."""
        mock_mkdtemp.return_value = "/tmp/mountrix_test_smb_12345"
        mock_exists.return_value = True
        mock_run.side_effect = [
            MagicMock(returncode=0, stderr="", stdout=""),
            MagicMock(returncode=0),
        ]

        result = verify_smb_mount("192.168.1.100", "public", "user", "pass")
        assert result.success is True

        # Check that credentials were passed
        mount_call = mock_run.call_args_list[0]
        mount_cmd = mount_call[0][0]
        assert any("username=user" in arg for arg in mount_cmd)
        assert any("password=pass" in arg for arg in mount_cmd)

    @patch("subprocess.run")
    @patch("tempfile.mkdtemp")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.rmdir")
    def test_smb_mount_guest(self, mock_rmdir, mock_exists, mock_mkdtemp, mock_run):
        """Test SMB mount with guest access."""
        mock_mkdtemp.return_value = "/tmp/mountrix_test_smb_12345"
        mock_exists.return_value = True
        mock_run.side_effect = [
            MagicMock(returncode=0, stderr="", stdout=""),
            MagicMock(returncode=0),
        ]

        result = verify_smb_mount("192.168.1.100", "public")
        assert result.success is True

        # Check that guest option was used
        mount_call = mock_run.call_args_list[0]
        mount_cmd = mount_call[0][0]
        assert any("guest" in arg for arg in mount_cmd)

    @patch("subprocess.run")
    @patch("tempfile.mkdtemp")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.rmdir")
    def test_smb_mount_failure(self, mock_rmdir, mock_exists, mock_mkdtemp, mock_run):
        """Test failed SMB mount test."""
        mock_mkdtemp.return_value = "/tmp/mountrix_test_smb_12345"
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=13, stderr="mount error(13): Permission denied", stdout=""
        )

        result = verify_smb_mount("192.168.1.100", "private")
        assert result.success is False
        assert "failed" in result.message.lower()


class TestMountTemporary:
    """Tests for verify_mount_temporary function."""

    @patch("mountrix.core.network.verify_nfs_mount")
    def test_mount_temporary_nfs(self, mock_nfs_mount):
        """Test temporary mount for NFS entry."""
        mock_nfs_mount.return_value = MountTestResult(
            success=True, message="Mount successful"
        )

        entry = FstabEntry(
            source="192.168.1.100:/data", mountpoint="/mnt/nas", fstype="nfs"
        )

        result = verify_mount_temporary(entry)
        assert result.success is True
        mock_nfs_mount.assert_called_once_with("192.168.1.100", "/data", 10)

    @patch("mountrix.core.network.verify_nfs_mount")
    def test_mount_temporary_nfs4(self, mock_nfs_mount):
        """Test temporary mount for NFS4 entry."""
        mock_nfs_mount.return_value = MountTestResult(
            success=True, message="Mount successful"
        )

        entry = FstabEntry(
            source="nas.local:/export", mountpoint="/mnt/nas", fstype="nfs4"
        )

        result = verify_mount_temporary(entry)
        assert result.success is True
        mock_nfs_mount.assert_called_once_with("nas.local", "/export", 10)

    @patch("mountrix.core.network.verify_smb_mount")
    def test_mount_temporary_smb(self, mock_smb_mount):
        """Test temporary mount for SMB entry."""
        mock_smb_mount.return_value = MountTestResult(
            success=True, message="Mount successful"
        )

        entry = FstabEntry(
            source="//192.168.1.100/public", mountpoint="/mnt/smb", fstype="cifs"
        )

        result = verify_mount_temporary(entry)
        assert result.success is True
        mock_smb_mount.assert_called_once_with("192.168.1.100", "public", None, None, 10)

    @patch("mountrix.core.network.verify_smb_mount")
    def test_mount_temporary_smb_with_credentials(self, mock_smb_mount):
        """Test temporary mount for SMB with credentials in options."""
        mock_smb_mount.return_value = MountTestResult(
            success=True, message="Mount successful"
        )

        entry = FstabEntry(
            source="//nas/share",
            mountpoint="/mnt/smb",
            fstype="cifs",
            options=["username=testuser", "password=testpass"],
        )

        result = verify_mount_temporary(entry)
        assert result.success is True
        mock_smb_mount.assert_called_once_with(
            "nas", "share", "testuser", "testpass", 10
        )

    def test_mount_temporary_invalid_entry(self):
        """Test with invalid fstab entry."""
        result = verify_mount_temporary(None)
        assert result.success is False
        assert "invalid" in result.message.lower()

    def test_mount_temporary_unsupported_fstype(self):
        """Test with unsupported filesystem type."""
        entry = FstabEntry(
            source="/dev/sda1", mountpoint="/mnt/data", fstype="ext4"
        )

        result = verify_mount_temporary(entry)
        assert result.success is False
        assert "not supported" in result.message.lower()

    def test_mount_temporary_invalid_nfs_source(self):
        """Test with invalid NFS source format."""
        entry = FstabEntry(
            source="invalid-source", mountpoint="/mnt/nas", fstype="nfs"
        )

        result = verify_mount_temporary(entry)
        assert result.success is False
        assert "invalid" in result.message.lower()

    def test_mount_temporary_invalid_smb_source(self):
        """Test with invalid SMB source format."""
        entry = FstabEntry(
            source="invalid-source", mountpoint="/mnt/smb", fstype="cifs"
        )

        result = verify_mount_temporary(entry)
        assert result.success is False
        assert "invalid" in result.message.lower()


class TestCommonNasPorts:
    """Tests for get_common_nas_ports function."""

    def test_get_common_nas_ports(self):
        """Test getting common NAS ports."""
        ports = get_common_nas_ports()
        assert isinstance(ports, dict)
        assert ports["smb"] == 445
        assert ports["cifs"] == 445
        assert ports["nfs"] == 2049
        assert ports["nfs4"] == 2049
        assert ports["ssh"] == 22


class TestDiagnoseConnection:
    """Tests for diagnose_connection function."""

    @patch("mountrix.core.network.check_port")
    @patch("mountrix.core.network.ping_host")
    @patch("mountrix.core.network.resolve_hostname")
    def test_diagnose_connection_all_success(
        self, mock_resolve, mock_ping, mock_check_port
    ):
        """Test connection diagnostics with all checks successful."""
        mock_resolve.return_value = "192.168.1.100"
        mock_ping.return_value = True
        mock_check_port.return_value = True

        result = diagnose_connection("nas.local", "smb")

        assert result["hostname_resolved"] is True
        assert result["ip_address"] == "192.168.1.100"
        assert result["ping_successful"] is True
        assert result["port_open"] is True
        assert result["port_number"] == 445
        assert result["protocol"] == "smb"

    @patch("mountrix.core.network.check_port")
    @patch("mountrix.core.network.ping_host")
    @patch("mountrix.core.network.resolve_hostname")
    def test_diagnose_connection_resolve_failure(
        self, mock_resolve, mock_ping, mock_check_port
    ):
        """Test connection diagnostics with hostname resolution failure."""
        mock_resolve.return_value = None
        mock_ping.return_value = False
        mock_check_port.return_value = False

        result = diagnose_connection("nonexistent.local", "smb")

        assert result["hostname_resolved"] is False
        assert result["ip_address"] is None
        assert result["ping_successful"] is False
        assert result["port_open"] is False

    @patch("mountrix.core.network.check_port")
    @patch("mountrix.core.network.ping_host")
    @patch("mountrix.core.network.resolve_hostname")
    def test_diagnose_connection_nfs(
        self, mock_resolve, mock_ping, mock_check_port
    ):
        """Test connection diagnostics for NFS."""
        mock_resolve.return_value = "192.168.1.100"
        mock_ping.return_value = True
        mock_check_port.return_value = True

        result = diagnose_connection("nas.local", "nfs")

        assert result["port_number"] == 2049
        assert result["protocol"] == "nfs"

    @patch("mountrix.core.network.check_port")
    @patch("mountrix.core.network.ping_host")
    @patch("mountrix.core.network.resolve_hostname")
    def test_diagnose_connection_with_ip(
        self, mock_resolve, mock_ping, mock_check_port
    ):
        """Test connection diagnostics with IP address instead of hostname."""
        mock_resolve.return_value = "192.168.1.100"
        mock_ping.return_value = True
        mock_check_port.return_value = True

        result = diagnose_connection("192.168.1.100", "smb")

        assert result["hostname_resolved"] is True
        assert result["ip_address"] == "192.168.1.100"
