# -*- coding: utf-8 -*-
"""
Desktop environment and drive detection for Mountrix.

This module contains functions for detecting:
- Desktop environment (GNOME, KDE, XFCE, etc.)
- Local drives (SATA, NVMe, USB)
- Filesystems (ext4, NTFS, exFAT, etc.)
- Network shares (NFS, SMB)
"""

import json
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

import psutil


class DesktopEnvironment(Enum):
    """Supported desktop environments."""

    GNOME = "GNOME"
    KDE = "KDE"
    XFCE = "XFCE"
    CINNAMON = "Cinnamon"
    LXQT = "LXQt"
    MATE = "MATE"
    UNKNOWN = "Unknown"


class DriveType(Enum):
    """Type of drive."""

    SATA = "SATA"
    NVME = "NVMe"
    USB = "USB"
    ESATA = "eSATA"
    UNKNOWN = "Unknown"


@dataclass
class Drive:
    """Represents a local drive."""

    device: str  # e.g. /dev/sda1
    name: str  # e.g. "Kingston SSD"
    drive_type: DriveType
    filesystem: str  # e.g. ext4, ntfs, exfat
    size_bytes: int
    mountpoint: Optional[str] = None  # Current mountpoint if mounted
    label: Optional[str] = None  # Filesystem label
    uuid: Optional[str] = None  # Filesystem UUID

    @property
    def size_gb(self) -> float:
        """Size in GB."""
        return self.size_bytes / (1024**3)

    @property
    def is_mounted(self) -> bool:
        """Is the drive currently mounted?"""
        return self.mountpoint is not None


@dataclass
class NetworkShare:
    """Represents a network share."""

    protocol: str  # nfs, smb, cifs
    host: str  # Hostname or IP
    share_path: str  # Path to share
    name: Optional[str] = None  # Display name


def detect_desktop_environment() -> DesktopEnvironment:
    """
    Detects the current desktop environment.

    Uses XDG_CURRENT_DESKTOP environment variable and other heuristics.

    Returns:
        DesktopEnvironment: The detected desktop environment
    """
    # Check XDG_CURRENT_DESKTOP (standard method)
    xdg_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()

    if "GNOME" in xdg_desktop:
        return DesktopEnvironment.GNOME
    elif "KDE" in xdg_desktop:
        return DesktopEnvironment.KDE
    elif "XFCE" in xdg_desktop:
        return DesktopEnvironment.XFCE
    elif "CINNAMON" in xdg_desktop or "X-CINNAMON" in xdg_desktop:
        return DesktopEnvironment.CINNAMON
    elif "LXQT" in xdg_desktop:
        return DesktopEnvironment.LXQT
    elif "MATE" in xdg_desktop:
        return DesktopEnvironment.MATE

    # Fallback: check DESKTOP_SESSION
    desktop_session = os.environ.get("DESKTOP_SESSION", "").lower()
    if "gnome" in desktop_session:
        return DesktopEnvironment.GNOME
    elif "kde" in desktop_session or "plasma" in desktop_session:
        return DesktopEnvironment.KDE
    elif "xfce" in desktop_session:
        return DesktopEnvironment.XFCE
    elif "cinnamon" in desktop_session:
        return DesktopEnvironment.CINNAMON
    elif "lxqt" in desktop_session:
        return DesktopEnvironment.LXQT

    return DesktopEnvironment.UNKNOWN


def get_filesystem_type(device: str) -> str:
    """
    Determines the filesystem type of a device.

    Args:
        device: Device path (e.g. /dev/sda1)

    Returns:
        str: Filesystem type (e.g. "ext4", "ntfs", "exfat") or "unknown"
    """
    try:
        # Use lsblk for filesystem info
        result = subprocess.run(
            ["lsblk", "-no", "FSTYPE", device],
            capture_output=True,
            text=True,
            check=True,
        )
        fstype = result.stdout.strip()
        return fstype if fstype else "unknown"
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: try blkid
        try:
            result = subprocess.run(
                ["blkid", "-s", "TYPE", "-o", "value", device],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip() or "unknown"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"


def _get_drive_type(device_name: str) -> DriveType:
    """
    Determines the type of drive based on device name.

    Args:
        device_name: Name of device (e.g. sda, nvme0n1)

    Returns:
        DriveType: Type of drive
    """
    device_name = device_name.lower()

    # NVMe drives
    if device_name.startswith("nvme"):
        return DriveType.NVME

    # Check USB devices via /sys/block
    sys_block_path = Path(f"/sys/block/{device_name}")
    if sys_block_path.exists():
        # Check if USB device
        device_path = sys_block_path.resolve()
        if "usb" in str(device_path):
            return DriveType.USB

    # Standard SATA/SCSI
    if device_name.startswith(("sd", "hd")):
        return DriveType.SATA

    return DriveType.UNKNOWN


def detect_local_drives() -> List[Drive]:
    """
    Detects all local drives (internal and external).

    Uses psutil and lsblk to find all available block devices.

    Returns:
        List[Drive]: List of all detected drives
    """
    drives: List[Drive] = []

    try:
        # Use lsblk for detailed info
        result = subprocess.run(
            [
                "lsblk",
                "-J",  # JSON output
                "-o",
                "NAME,TYPE,SIZE,FSTYPE,MOUNTPOINT,LABEL,UUID",
                "-b",  # Bytes
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        lsblk_data = json.loads(result.stdout)

        for device in lsblk_data.get("blockdevices", []):
            _process_device(device, drives)

    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        # Fallback: psutil.disk_partitions()
        for partition in psutil.disk_partitions(all=False):
            device_name = Path(partition.device).name
            drive_type = _get_drive_type(device_name)

            try:
                usage = psutil.disk_usage(partition.mountpoint)
                size_bytes = usage.total
            except (PermissionError, OSError):
                size_bytes = 0

            drive = Drive(
                device=partition.device,
                name=device_name,
                drive_type=drive_type,
                filesystem=partition.fstype,
                size_bytes=size_bytes,
                mountpoint=partition.mountpoint if partition.mountpoint else None,
            )
            drives.append(drive)

    return drives


def _process_device(device: dict, drives: List[Drive]) -> None:
    """
    Processes an lsblk device and adds it to the list.

    Args:
        device: lsblk device dict
        drives: List to add to
    """
    # Main device (disk)
    if device.get("type") == "disk":
        # Check if disk has partitions
        children = device.get("children", [])
        if children:
            # Process partitions
            for child in children:
                if child.get("type") == "part":
                    _add_drive_from_lsblk(child, drives)
        else:
            # No partitions - disk has filesystem directly (common in WSL/VM)
            if device.get("fstype"):
                _add_drive_from_lsblk(device, drives)
    # Single partition
    elif device.get("type") == "part":
        _add_drive_from_lsblk(device, drives)


def _add_drive_from_lsblk(partition: dict, drives: List[Drive]) -> None:
    """
    Creates a Drive object from lsblk data.

    Args:
        partition: lsblk partition dict
        drives: List to add to
    """
    device_name = partition.get("name", "")
    device_path = f"/dev/{device_name}"

    # Determine type
    drive_type = _get_drive_type(device_name)

    # Size
    size_bytes = int(partition.get("size", 0))

    # Filesystem
    filesystem = partition.get("fstype") or "unknown"

    # Mountpoint
    mountpoint = (
        partition.get("mountpoints", [None])[0]
        if "mountpoints" in partition
        else partition.get("mountpoint")
    )

    # Label and UUID
    label = partition.get("label")
    uuid = partition.get("uuid")

    # Compose name
    name = label if label else device_name

    drive = Drive(
        device=device_path,
        name=name,
        drive_type=drive_type,
        filesystem=filesystem,
        size_bytes=size_bytes,
        mountpoint=mountpoint,
        label=label,
        uuid=uuid,
    )

    drives.append(drive)


def scan_network_shares() -> List[NetworkShare]:
    """
    Scans the local network for shares (NFS, SMB).

    Uses avahi-browse (for NFS/SMB discovery) and smbtree (for SMB).

    Returns:
        List[NetworkShare]: List of found network shares

    Note:
        Requires avahi-utils and samba-common-bin installed.
        This function can take several seconds.
    """
    shares: List[NetworkShare] = []

    # TODO: Implementation for v1.0
    # - avahi-browse for service discovery
    # - smbtree for SMB shares
    # - showmount for NFS exports

    return shares


def detect_system_theme() -> str:
    """
    Detect system theme preference (dark or light).

    Returns:
        str: "dark", "light", or "unknown"

    Note:
        Checks various desktop environment settings to determine theme.
    """
    desktop = detect_desktop_environment()

    # Try different methods based on desktop environment
    try:
        # KDE Plasma
        if desktop == DesktopEnvironment.KDE:
            try:
                result = subprocess.run(
                    ["kreadconfig5", "--group", "General", "--key", "ColorScheme"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    scheme = result.stdout.strip().lower()
                    if "dark" in scheme or "breeze dark" in scheme:
                        return "dark"
                    return "light"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        # GNOME
        if desktop == DesktopEnvironment.GNOME:
            try:
                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    theme = result.stdout.strip().lower()
                    if "dark" in theme:
                        return "dark"
                    return "light"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

            # Alternative: Check color-scheme setting (GNOME 42+)
            try:
                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    scheme = result.stdout.strip().lower()
                    if "dark" in scheme:
                        return "dark"
                    if "light" in scheme:
                        return "light"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        # XFCE
        if desktop == DesktopEnvironment.XFCE:
            try:
                result = subprocess.run(
                    ["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    theme = result.stdout.strip().lower()
                    if "dark" in theme:
                        return "dark"
                    return "light"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        # Generic: Check GTK theme from environment or config
        gtk_theme = os.environ.get("GTK_THEME", "").lower()
        if "dark" in gtk_theme:
            return "dark"
        if "light" in gtk_theme:
            return "light"

        # Check GTK3 settings file
        gtk3_settings = Path.home() / ".config" / "gtk-3.0" / "settings.ini"
        if gtk3_settings.exists():
            try:
                content = gtk3_settings.read_text()
                for line in content.splitlines():
                    if "gtk-theme-name" in line.lower():
                        if "dark" in line.lower():
                            return "dark"
                        return "light"
            except Exception:
                pass

    except Exception:
        pass

    # Default to light if cannot detect
    return "unknown"


if __name__ == "__main__":
    # Test code
    print("=== Mountrix Detector ===\n")

    # Desktop environment
    desktop = detect_desktop_environment()
    print(f"Desktop Environment: {desktop.value}")

    # Local drives
    print("\nLocal Drives:")
    drives = detect_local_drives()
    for drive in drives:
        mount_info = (
            f" (mounted at {drive.mountpoint})"
            if drive.is_mounted
            else " (not mounted)"
        )
        print(
            f"  - {drive.name} ({drive.device}): "
            f"{drive.size_gb:.1f} GB, {drive.filesystem}, "
            f"{drive.drive_type.value}{mount_info}"
        )
