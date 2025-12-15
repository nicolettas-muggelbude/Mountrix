# -*- coding: utf-8 -*-
"""
Mount logic for Mountrix.

This module handles mounting and unmounting operations:
- Creating mountpoints
- Mounting fstab entries
- Unmounting entries
- Verifying mount status
"""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from .fstab import FstabEntry


@dataclass
class MountResult:
    """Result of a mount or unmount operation."""

    success: bool
    message: str
    mountpoint: Optional[str] = None
    error_code: Optional[int] = None


def get_current_username() -> str:
    """
    Get the current user's username.

    Returns:
        str: Current username

    Example:
        >>> get_current_username()
        'nicole'
    """
    return os.environ.get("USER") or os.environ.get("USERNAME") or "user"


def create_mountpoint(path: str, user_only: bool = False) -> MountResult:
    """
    Create a mountpoint directory.

    Args:
        path: Path where to create the mountpoint
        user_only: If True, create in /media/<username>, otherwise in /mnt

    Returns:
        MountResult: Result object with success status and message

    Example:
        >>> result = create_mountpoint("nas_data", user_only=True)
        >>> if result.success:
        ...     print(f"Created: {result.mountpoint}")
    """
    if not path:
        return MountResult(success=False, message="Path cannot be empty")

    # Sanitize path (remove leading/trailing slashes, dangerous characters)
    sanitized = path.strip("/").replace("..", "").replace("//", "/")
    if not sanitized:
        return MountResult(success=False, message="Invalid path after sanitization")

    # Determine full mountpoint path
    if user_only:
        username = get_current_username()
        full_path = Path("/media") / username / sanitized
    else:
        full_path = Path("/mnt") / sanitized

    # Check if already exists
    if full_path.exists():
        if full_path.is_dir():
            return MountResult(
                success=True,
                message=f"Mountpoint already exists: {full_path}",
                mountpoint=str(full_path),
            )
        else:
            return MountResult(
                success=False,
                message=f"Path exists but is not a directory: {full_path}",
            )

    # Create directory
    try:
        full_path.mkdir(parents=True, exist_ok=True)

        # Set appropriate permissions
        if user_only:
            # For user-only mounts, set ownership to current user
            try:
                import pwd

                uid = pwd.getpwnam(get_current_username()).pw_uid
                os.chown(full_path, uid, uid)
                full_path.chmod(0o755)
            except Exception:
                # If setting ownership fails, continue anyway
                pass
        else:
            # For system mounts, keep root ownership
            full_path.chmod(0o755)

        return MountResult(
            success=True,
            message=f"Mountpoint created: {full_path}",
            mountpoint=str(full_path),
        )

    except PermissionError:
        return MountResult(
            success=False,
            message=f"Permission denied creating {full_path}. Root privileges required.",
        )
    except Exception as e:
        return MountResult(
            success=False, message=f"Error creating mountpoint: {str(e)}"
        )


def mount_entry(entry: FstabEntry) -> MountResult:
    """
    Mount a filesystem entry.

    Args:
        entry: FstabEntry to mount

    Returns:
        MountResult: Result object with success status and message

    Example:
        >>> entry = FstabEntry(
        ...     source="//nas/public",
        ...     mountpoint="/mnt/nas",
        ...     fstype="cifs"
        ... )
        >>> result = mount_entry(entry)
        >>> if result.success:
        ...     print("Mount successful!")
    """
    if not entry or not entry.source or not entry.mountpoint or not entry.fstype:
        return MountResult(
            success=False, message="Invalid entry: missing required fields"
        )

    # Check if mountpoint exists
    mountpoint_path = Path(entry.mountpoint)
    if not mountpoint_path.exists():
        return MountResult(
            success=False,
            message=f"Mountpoint does not exist: {entry.mountpoint}. Create it first.",
        )

    if not mountpoint_path.is_dir():
        return MountResult(
            success=False,
            message=f"Mountpoint is not a directory: {entry.mountpoint}",
        )

    # Build mount command
    mount_cmd = ["mount"]

    # Add filesystem type
    mount_cmd.extend(["-t", entry.fstype])

    # Add options
    if entry.options:
        opts = ",".join(entry.options)
        mount_cmd.extend(["-o", opts])

    # Add source and mountpoint
    mount_cmd.append(entry.source)
    mount_cmd.append(entry.mountpoint)

    # Execute mount
    try:
        result = subprocess.run(
            mount_cmd, capture_output=True, text=True, timeout=30, check=False
        )

        if result.returncode == 0:
            return MountResult(
                success=True,
                message=f"Successfully mounted {entry.source} to {entry.mountpoint}",
                mountpoint=entry.mountpoint,
            )
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return MountResult(
                success=False,
                message=f"Mount failed: {error_msg}",
                error_code=result.returncode,
            )

    except subprocess.TimeoutExpired:
        return MountResult(success=False, message="Mount operation timed out")
    except PermissionError:
        return MountResult(
            success=False,
            message="Permission denied. Root privileges required for mounting.",
        )
    except FileNotFoundError:
        return MountResult(
            success=False, message="mount command not found. Install mount utilities."
        )
    except Exception as e:
        return MountResult(success=False, message=f"Unexpected error: {str(e)}")


def unmount_entry(mountpoint: str, force: bool = False) -> MountResult:
    """
    Unmount a filesystem.

    Args:
        mountpoint: Path to unmount
        force: If True, force unmount even if busy

    Returns:
        MountResult: Result object with success status and message

    Example:
        >>> result = unmount_entry("/mnt/nas")
        >>> if result.success:
        ...     print("Unmount successful!")
    """
    if not mountpoint:
        return MountResult(success=False, message="Mountpoint cannot be empty")

    mountpoint_path = Path(mountpoint)
    if not mountpoint_path.exists():
        return MountResult(
            success=False, message=f"Mountpoint does not exist: {mountpoint}"
        )

    # Build umount command
    umount_cmd = ["umount"]

    if force:
        umount_cmd.append("-f")  # Force unmount

    umount_cmd.append(mountpoint)

    # Execute unmount
    try:
        result = subprocess.run(
            umount_cmd, capture_output=True, text=True, timeout=30, check=False
        )

        if result.returncode == 0:
            return MountResult(
                success=True,
                message=f"Successfully unmounted {mountpoint}",
                mountpoint=mountpoint,
            )
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()

            # Check for common errors
            if "not mounted" in error_msg.lower():
                return MountResult(
                    success=True,  # Not an error if already unmounted
                    message=f"{mountpoint} is not mounted",
                    mountpoint=mountpoint,
                )
            elif "busy" in error_msg.lower() or "target is busy" in error_msg.lower():
                suggestion = " Try force unmount or close applications using this mount."
                return MountResult(
                    success=False,
                    message=f"Unmount failed: Device is busy.{suggestion}",
                    error_code=result.returncode,
                )
            else:
                return MountResult(
                    success=False,
                    message=f"Unmount failed: {error_msg}",
                    error_code=result.returncode,
                )

    except subprocess.TimeoutExpired:
        return MountResult(success=False, message="Unmount operation timed out")
    except PermissionError:
        return MountResult(
            success=False,
            message="Permission denied. Root privileges required for unmounting.",
        )
    except FileNotFoundError:
        return MountResult(
            success=False, message="umount command not found. Install mount utilities."
        )
    except Exception as e:
        return MountResult(success=False, message=f"Unexpected error: {str(e)}")


def verify_mount(mountpoint: str) -> bool:
    """
    Verify if a mountpoint is currently mounted.

    Args:
        mountpoint: Path to check

    Returns:
        bool: True if mounted, False otherwise

    Example:
        >>> if verify_mount("/mnt/nas"):
        ...     print("NAS is mounted")
    """
    if not mountpoint:
        return False

    try:
        # Read /proc/mounts to check if mountpoint is mounted
        with open("/proc/mounts", "r") as f:
            mounts = f.read()
            # Normalize paths for comparison
            normalized_mountpoint = str(Path(mountpoint).resolve())
            for line in mounts.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    mounted_path = parts[1]
                    # Handle escaped spaces and special characters
                    mounted_path = mounted_path.replace("\\040", " ")
                    if mounted_path == normalized_mountpoint:
                        return True
        return False

    except FileNotFoundError:
        # /proc/mounts doesn't exist (non-Linux system?)
        # Fallback to checking with mount command
        try:
            result = subprocess.run(
                ["mount"], capture_output=True, text=True, timeout=5, check=False
            )
            if result.returncode == 0:
                normalized_mountpoint = str(Path(mountpoint).resolve())
                for line in result.stdout.splitlines():
                    if f" on {normalized_mountpoint} " in line:
                        return True
            return False
        except Exception:
            return False
    except Exception:
        return False


def get_mount_info(mountpoint: str) -> Optional[dict]:
    """
    Get detailed information about a mounted filesystem.

    Args:
        mountpoint: Path to check

    Returns:
        Optional[dict]: Dictionary with mount info or None if not mounted
            Keys: source, mountpoint, fstype, options

    Example:
        >>> info = get_mount_info("/mnt/nas")
        >>> if info:
        ...     print(f"Type: {info['fstype']}, Source: {info['source']}")
    """
    if not mountpoint or not verify_mount(mountpoint):
        return None

    try:
        with open("/proc/mounts", "r") as f:
            normalized_mountpoint = str(Path(mountpoint).resolve())
            for line in f:
                parts = line.split()
                if len(parts) >= 4:
                    mounted_path = parts[1].replace("\\040", " ")
                    if mounted_path == normalized_mountpoint:
                        return {
                            "source": parts[0],
                            "mountpoint": mounted_path,
                            "fstype": parts[2],
                            "options": parts[3].split(","),
                        }
        return None

    except Exception:
        return None


def remount_entry(entry: FstabEntry) -> MountResult:
    """
    Remount a filesystem (unmount and mount again).

    Args:
        entry: FstabEntry to remount

    Returns:
        MountResult: Result object with success status and message

    Example:
        >>> result = remount_entry(entry)
        >>> if result.success:
        ...     print("Remount successful!")
    """
    if not entry or not entry.mountpoint:
        return MountResult(success=False, message="Invalid entry")

    # First, unmount if currently mounted
    if verify_mount(entry.mountpoint):
        unmount_result = unmount_entry(entry.mountpoint)
        if not unmount_result.success:
            return MountResult(
                success=False,
                message=f"Failed to unmount before remounting: {unmount_result.message}",
            )

    # Then mount
    return mount_entry(entry)
