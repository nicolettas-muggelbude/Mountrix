# -*- coding: utf-8 -*-
"""
Network diagnostics and utilities for Mountrix.

This module provides network-related functions for:
- Host reachability testing (ping)
- Port connectivity checks
- Hostname resolution
- Temporary mount testing
"""

import socket
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from .fstab import FstabEntry


@dataclass
class MountTestResult:
    """Result of a temporary mount test."""

    success: bool
    message: str
    error_code: Optional[int] = None
    mountpoint: Optional[str] = None


def ping_host(host: str, timeout: int = 3, count: int = 1) -> bool:
    """
    Test if a host is reachable via ICMP ping.

    Args:
        host: Hostname or IP address to ping
        timeout: Timeout in seconds (default: 3)
        count: Number of ping packets to send (default: 1)

    Returns:
        bool: True if host responds to ping, False otherwise

    Example:
        >>> ping_host("192.168.1.1")
        True
        >>> ping_host("nonexistent.local")
        False
    """
    if not host:
        return False

    try:
        # Use -c for count, -W for timeout (in seconds)
        result = subprocess.run(
            ["ping", "-c", str(count), "-W", str(timeout), host],
            capture_output=True,
            timeout=timeout + 2,  # Add buffer to timeout
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_port(host: str, port: int, timeout: int = 3) -> bool:
    """
    Check if a specific port is open on a host.

    Args:
        host: Hostname or IP address
        port: Port number to check
        timeout: Connection timeout in seconds (default: 3)

    Returns:
        bool: True if port is open and accepting connections, False otherwise

    Example:
        >>> check_port("192.168.1.100", 445)  # SMB
        True
        >>> check_port("192.168.1.100", 2049)  # NFS
        True
    """
    if not host or not (1 <= port <= 65535):
        return False

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except (socket.error, socket.timeout):
        return False


def resolve_hostname(hostname: str, timeout: int = 3) -> Optional[str]:
    """
    Resolve a hostname to an IP address.

    Args:
        hostname: Hostname to resolve
        timeout: DNS resolution timeout in seconds (default: 3)

    Returns:
        Optional[str]: IP address if resolution successful, None otherwise

    Example:
        >>> resolve_hostname("localhost")
        '127.0.0.1'
        >>> resolve_hostname("fritz.box")
        '192.168.178.1'
        >>> resolve_hostname("nonexistent.invalid")
        None
    """
    if not hostname:
        return None

    # Check if it's already an IP address
    try:
        socket.inet_aton(hostname)
        return hostname  # Already an IP
    except socket.error:
        pass

    # Try to resolve
    try:
        socket.setdefaulttimeout(timeout)
        ip = socket.gethostbyname(hostname)
        return ip
    except (socket.gaierror, socket.timeout):
        return None
    finally:
        socket.setdefaulttimeout(None)


def verify_nfs_mount(host: str, share_path: str, timeout: int = 10) -> MountTestResult:
    """
    Test mounting an NFS share temporarily.

    Args:
        host: NFS server hostname or IP
        share_path: Path to share on server (e.g., "/mnt/data")
        timeout: Mount operation timeout in seconds (default: 10)

    Returns:
        MountTestResult: Result object with success status and message
    """
    if not host or not share_path:
        return MountTestResult(
            success=False, message="Host and share path are required"
        )

    # Create temporary mountpoint
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="mountrix_test_nfs_")
        source = f"{host}:{share_path}"

        # Try to mount
        result = subprocess.run(
            ["mount", "-t", "nfs", "-o", "ro,soft,timeo=5", source, temp_dir],
            capture_output=True,
            timeout=timeout,
            text=True,
        )

        if result.returncode == 0:
            # Successfully mounted, now unmount
            subprocess.run(["umount", temp_dir], capture_output=True, timeout=5)
            return MountTestResult(
                success=True,
                message=f"NFS mount test successful for {source}",
                mountpoint=temp_dir,
            )
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return MountTestResult(
                success=False,
                message=f"Mount failed: {error_msg}",
                error_code=result.returncode,
            )

    except subprocess.TimeoutExpired:
        return MountTestResult(
            success=False, message=f"Mount operation timed out after {timeout}s"
        )
    except PermissionError:
        return MountTestResult(
            success=False,
            message="Permission denied. Root privileges required for mount testing.",
        )
    except Exception as e:
        return MountTestResult(success=False, message=f"Unexpected error: {str(e)}")
    finally:
        # Clean up temp directory
        if temp_dir and Path(temp_dir).exists():
            try:
                # Make sure it's unmounted first
                subprocess.run(
                    ["umount", temp_dir], capture_output=True, timeout=5, check=False
                )
                Path(temp_dir).rmdir()
            except Exception:
                pass


def verify_smb_mount(
    host: str,
    share_path: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    timeout: int = 10,
) -> MountTestResult:
    """
    Test mounting a SMB/CIFS share temporarily.

    Args:
        host: SMB server hostname or IP
        share_path: Share name (e.g., "public" or "data")
        username: Username for authentication (optional for guest access)
        password: Password for authentication (optional)
        timeout: Mount operation timeout in seconds (default: 10)

    Returns:
        MountTestResult: Result object with success status and message
    """
    if not host or not share_path:
        return MountTestResult(
            success=False, message="Host and share path are required"
        )

    # Create temporary mountpoint
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="mountrix_test_smb_")
        source = f"//{host}/{share_path}"

        # Build mount options
        mount_opts = ["ro", "soft"]

        if username:
            mount_opts.append(f"username={username}")
            if password:
                mount_opts.append(f"password={password}")
        else:
            mount_opts.append("guest")

        # Try to mount
        result = subprocess.run(
            ["mount", "-t", "cifs", "-o", ",".join(mount_opts), source, temp_dir],
            capture_output=True,
            timeout=timeout,
            text=True,
        )

        if result.returncode == 0:
            # Successfully mounted, now unmount
            subprocess.run(["umount", temp_dir], capture_output=True, timeout=5)
            return MountTestResult(
                success=True,
                message=f"SMB mount test successful for {source}",
                mountpoint=temp_dir,
            )
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return MountTestResult(
                success=False,
                message=f"Mount failed: {error_msg}",
                error_code=result.returncode,
            )

    except subprocess.TimeoutExpired:
        return MountTestResult(
            success=False, message=f"Mount operation timed out after {timeout}s"
        )
    except PermissionError:
        return MountTestResult(
            success=False,
            message="Permission denied. Root privileges required for mount testing.",
        )
    except Exception as e:
        return MountTestResult(success=False, message=f"Unexpected error: {str(e)}")
    finally:
        # Clean up temp directory
        if temp_dir and Path(temp_dir).exists():
            try:
                # Make sure it's unmounted first
                subprocess.run(
                    ["umount", temp_dir], capture_output=True, timeout=5, check=False
                )
                Path(temp_dir).rmdir()
            except Exception:
                pass


def verify_mount_temporary(entry: FstabEntry, timeout: int = 10) -> MountTestResult:
    """
    Test mounting an fstab entry temporarily.

    This is a high-level function that delegates to protocol-specific
    test functions based on the filesystem type.

    Args:
        entry: FstabEntry to test
        timeout: Mount operation timeout in seconds (default: 10)

    Returns:
        MountTestResult: Result object with success status and message

    Example:
        >>> entry = FstabEntry(
        ...     source="192.168.1.100:/data",
        ...     mountpoint="/mnt/nas",
        ...     fstype="nfs"
        ... )
        >>> result = test_mount_temporary(entry)
        >>> if result.success:
        ...     print("Mount test successful!")
    """
    if not entry or not entry.source or not entry.fstype:
        return MountTestResult(
            success=False, message="Invalid fstab entry: missing source or fstype"
        )

    # NFS mounts
    if entry.fstype in ("nfs", "nfs4"):
        try:
            # Parse NFS source: "host:/path"
            host, share_path = entry.source.split(":", 1)
            return verify_nfs_mount(host, share_path, timeout)
        except ValueError:
            return MountTestResult(
                success=False,
                message=f"Invalid NFS source format: {entry.source}. Expected 'host:/path'",
            )

    # SMB/CIFS mounts
    elif entry.fstype in ("cifs", "smb"):
        try:
            # Parse SMB source: "//host/share"
            if not entry.source.startswith("//"):
                return MountTestResult(
                    success=False,
                    message=f"Invalid SMB source format: {entry.source}. Expected '//host/share'",
                )

            parts = entry.source[2:].split("/", 1)
            if len(parts) != 2:
                return MountTestResult(
                    success=False,
                    message=f"Invalid SMB source format: {entry.source}. Expected '//host/share'",
                )

            host, share_path = parts

            # Extract credentials from options if present
            username = None
            password = None
            for opt in entry.options:
                if opt.startswith("username="):
                    username = opt.split("=", 1)[1]
                elif opt.startswith("password="):
                    password = opt.split("=", 1)[1]

            return verify_smb_mount(host, share_path, username, password, timeout)

        except ValueError as e:
            return MountTestResult(
                success=False, message=f"Error parsing SMB source: {str(e)}"
            )

    else:
        return MountTestResult(
            success=False,
            message=f"Mount testing not supported for filesystem type: {entry.fstype}",
        )


def get_common_nas_ports() -> dict[str, int]:
    """
    Get dictionary of common NAS protocol ports.

    Returns:
        dict[str, int]: Mapping of protocol names to port numbers

    Example:
        >>> ports = get_common_nas_ports()
        >>> ports['smb']
        445
        >>> ports['nfs']
        2049
    """
    return {
        "smb": 445,
        "cifs": 445,
        "nfs": 2049,
        "nfs4": 2049,
        "ssh": 22,
        "ftp": 21,
        "webdav": 80,
        "webdav_ssl": 443,
    }


def diagnose_connection(host: str, protocol: str = "smb") -> dict:
    """
    Perform comprehensive connection diagnostics for a host.

    Args:
        host: Hostname or IP address
        protocol: Protocol to check (smb, nfs, etc.)

    Returns:
        dict: Diagnostic results with keys:
            - hostname_resolved: bool
            - ip_address: str or None
            - ping_successful: bool
            - port_open: bool
            - port_number: int

    Example:
        >>> result = diagnose_connection("192.168.1.100", "smb")
        >>> if result['ping_successful'] and result['port_open']:
        ...     print("Host is reachable and SMB port is open")
    """
    ports = get_common_nas_ports()
    port = ports.get(protocol.lower(), 0)

    # Resolve hostname
    ip_address = resolve_hostname(host)
    hostname_resolved = ip_address is not None

    # Use IP if resolved, otherwise use original host
    target = ip_address if ip_address else host

    # Ping test
    ping_successful = ping_host(target) if hostname_resolved or ip_address else False

    # Port check
    port_open = check_port(target, port) if port > 0 and hostname_resolved else False

    return {
        "hostname_resolved": hostname_resolved,
        "ip_address": ip_address,
        "ping_successful": ping_successful,
        "port_open": port_open,
        "port_number": port,
        "protocol": protocol,
    }
