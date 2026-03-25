# -*- coding: utf-8 -*-
"""
Privilege escalation for Mountrix.

Handles running commands with elevated privileges via pkexec (polkit GUI dialog)
or sudo as fallback. pkexec is preferred for GUI applications as it shows a
native authentication dialog without requiring a terminal.
"""

import os
import shutil
import subprocess
import tempfile
from typing import List, Optional


def is_root() -> bool:
    """Return True if the process is already running as root."""
    return os.geteuid() == 0


def find_privilege_escalator() -> Optional[str]:
    """
    Find an available privilege escalation tool.

    Returns:
        'pkexec', 'sudo', or None if neither is available.
        pkexec is preferred for GUI applications (shows polkit dialog).
    """
    for cmd in ("pkexec", "sudo"):
        if shutil.which(cmd):
            return cmd
    return None


def run_privileged(
    cmd: List[str], timeout: int = 30
) -> subprocess.CompletedProcess:
    """
    Run a command with elevated privileges.

    If already root, runs directly. Otherwise wraps with pkexec or sudo.
    pkexec is preferred as it shows a native polkit authentication dialog.

    Args:
        cmd: Command and arguments to run
        timeout: Timeout in seconds (default: 30)

    Returns:
        CompletedProcess with returncode, stdout, stderr

    Raises:
        PermissionError: If no privilege escalator is available
        subprocess.TimeoutExpired: If the command times out

    Example:
        >>> result = run_privileged(["mount", "-t", "cifs", "//nas/share", "/mnt/nas"])
        >>> if result.returncode == 0:
        ...     print("Erfolgreich gemountet")
    """
    if is_root():
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )

    escalator = find_privilege_escalator()
    if not escalator:
        raise PermissionError(
            "Keine Methode zur Privilegienerweiterung gefunden. "
            "Bitte pkexec oder sudo installieren."
        )

    return subprocess.run(
        [escalator] + cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def write_privileged(content: str, dest_path: str) -> None:
    """
    Write content to a file that requires root privileges.

    Writes to a temporary file first, then copies it to the destination
    using elevated privileges. The temp file is always cleaned up.

    Args:
        content: File content to write
        dest_path: Destination path (e.g. /etc/fstab)

    Raises:
        PermissionError: If privilege escalation fails or is unavailable
        OSError: If the temp file cannot be created

    Example:
        >>> write_privileged("# fstab\\n/dev/sda1 / ext4 defaults 0 1\\n", "/etc/fstab")
    """
    tmp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".mountrix_tmp", delete=False
        ) as f:
            tmp_path = f.name
            f.write(content)

        result = run_privileged(["cp", tmp_path, dest_path])
        if result.returncode != 0:
            error = result.stderr.strip() or result.stdout.strip()
            raise PermissionError(
                f"Fehler beim Schreiben von {dest_path}: {error}"
            )
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def copy_privileged(src_path: str, dest_path: str) -> None:
    """
    Copy a file using elevated privileges.

    Args:
        src_path: Source file path
        dest_path: Destination file path

    Raises:
        PermissionError: If privilege escalation fails or is unavailable
    """
    result = run_privileged(["cp", src_path, dest_path])
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        raise PermissionError(
            f"Fehler beim Kopieren von {src_path} nach {dest_path}: {error}"
        )


def mkdir_privileged(path: str) -> None:
    """
    Create a directory using elevated privileges.

    Args:
        path: Directory path to create

    Raises:
        PermissionError: If privilege escalation fails or is unavailable
    """
    result = run_privileged(["mkdir", "-p", path])
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        raise PermissionError(
            f"Fehler beim Erstellen von {path}: {error}"
        )
