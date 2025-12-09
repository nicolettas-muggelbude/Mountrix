# -*- coding: utf-8 -*-
"""
fstab Management for Mountrix.

This module handles reading, writing, and managing /etc/fstab entries.
Includes backup functionality and validation.
"""

import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class FstabEntry:
    """Represents a single fstab entry."""

    source: str  # Device, UUID=..., LABEL=..., or network path
    mountpoint: str  # Mount destination
    fstype: str  # Filesystem type (ext4, nfs, cifs, etc.)
    options: List[str] = field(default_factory=lambda: ["defaults"])  # Mount options
    dump: int = 0  # Dump frequency (0 = no dump)
    pass_num: int = 0  # fsck pass number (0 = no check)
    comment: Optional[str] = None  # Optional comment for this entry

    def __str__(self) -> str:
        """Convert entry to fstab line format."""
        opts = ",".join(self.options) if self.options else "defaults"
        line = f"{self.source}\t{self.mountpoint}\t{self.fstype}\t{opts}\t{self.dump}\t{self.pass_num}"
        return line

    @property
    def is_network(self) -> bool:
        """Check if this is a network mount."""
        return self.fstype in ("nfs", "nfs4", "cifs", "smb")

    @property
    def is_uuid(self) -> bool:
        """Check if source uses UUID."""
        return self.source.startswith("UUID=")

    @property
    def is_label(self) -> bool:
        """Check if source uses LABEL."""
        return self.source.startswith("LABEL=")


def parse_fstab(fstab_path: str = "/etc/fstab") -> List[FstabEntry]:
    """
    Parse fstab file and return list of entries.

    Args:
        fstab_path: Path to fstab file (default: /etc/fstab)

    Returns:
        List[FstabEntry]: List of parsed fstab entries

    Raises:
        FileNotFoundError: If fstab file doesn't exist
        PermissionError: If no read permission

    Example:
        >>> entries = parse_fstab()
        >>> for entry in entries:
        ...     print(f"{entry.mountpoint}: {entry.fstype}")
    """
    if not Path(fstab_path).exists():
        raise FileNotFoundError(f"fstab not found: {fstab_path}")

    entries: List[FstabEntry] = []
    current_comment: Optional[str] = None

    with open(fstab_path, "r") as f:
        for line in f:
            line = line.strip()

            # Skip empty lines
            if not line:
                current_comment = None
                continue

            # Comment line
            if line.startswith("#"):
                current_comment = line[1:].strip()
                continue

            # Parse entry
            try:
                entry = _parse_fstab_line(line, current_comment)
                if entry:
                    entries.append(entry)
                current_comment = None
            except ValueError:
                # Skip malformed lines
                current_comment = None
                continue

    return entries


def _parse_fstab_line(line: str, comment: Optional[str] = None) -> Optional[FstabEntry]:
    """
    Parse a single fstab line.

    Args:
        line: fstab line to parse
        comment: Optional comment from previous line

    Returns:
        FstabEntry or None if line is invalid
    """
    # Split by whitespace, handling tabs and spaces
    parts = re.split(r"\s+", line.strip())

    if len(parts) < 4:
        return None

    # Extract components
    source = parts[0]
    mountpoint = parts[1]
    fstype = parts[2]
    options = parts[3].split(",") if parts[3] else ["defaults"]
    dump = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    pass_num = int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0

    return FstabEntry(
        source=source,
        mountpoint=mountpoint,
        fstype=fstype,
        options=options,
        dump=dump,
        pass_num=pass_num,
        comment=comment,
    )


def backup_fstab(
    fstab_path: str = "/etc/fstab", backup_dir: str = "/var/backups"
) -> str:
    """
    Create a timestamped backup of fstab.

    Args:
        fstab_path: Path to fstab file
        backup_dir: Directory for backups

    Returns:
        str: Path to created backup file

    Raises:
        FileNotFoundError: If fstab doesn't exist
        PermissionError: If no write permission

    Example:
        >>> backup_path = backup_fstab()
        >>> print(f"Backup created: {backup_path}")
    """
    if not Path(fstab_path).exists():
        raise FileNotFoundError(f"fstab not found: {fstab_path}")

    # Create backup directory if it doesn't exist
    Path(backup_dir).mkdir(parents=True, exist_ok=True)

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"fstab.backup.{timestamp}"
    backup_path = Path(backup_dir) / backup_filename

    # Copy file
    shutil.copy2(fstab_path, backup_path)

    return str(backup_path)


def add_entry(
    entry: FstabEntry, fstab_path: str = "/etc/fstab", create_backup: bool = True
) -> bool:
    """
    Add a new entry to fstab.

    Args:
        entry: FstabEntry to add
        fstab_path: Path to fstab file
        create_backup: Whether to create backup before writing

    Returns:
        bool: True if successful

    Raises:
        PermissionError: If no write permission
        ValueError: If entry validation fails

    Example:
        >>> entry = FstabEntry(
        ...     source="UUID=abc-123",
        ...     mountpoint="/mnt/data",
        ...     fstype="ext4",
        ...     options=["defaults", "nofail"]
        ... )
        >>> add_entry(entry)
    """
    # Validate entry
    is_valid, error_msg = validate_entry(entry)
    if not is_valid:
        raise ValueError(f"Invalid fstab entry: {error_msg}")

    # Create backup
    if create_backup:
        backup_fstab(fstab_path)

    # Check if entry already exists
    existing_entries = parse_fstab(fstab_path)
    for existing in existing_entries:
        if existing.mountpoint == entry.mountpoint:
            raise ValueError(f"Mountpoint {entry.mountpoint} already exists in fstab")

    # Append entry
    with open(fstab_path, "a") as f:
        # Add comment if present
        if entry.comment:
            f.write(f"# {entry.comment}\n")
        f.write(str(entry) + "\n")

    return True


def remove_entry(
    mountpoint: str, fstab_path: str = "/etc/fstab", create_backup: bool = True
) -> bool:
    """
    Remove an entry from fstab by mountpoint.

    Args:
        mountpoint: Mountpoint of entry to remove
        fstab_path: Path to fstab file
        create_backup: Whether to create backup before writing

    Returns:
        bool: True if entry was removed, False if not found

    Raises:
        PermissionError: If no write permission

    Example:
        >>> remove_entry("/mnt/data")
    """
    entries = parse_fstab(fstab_path)

    # Find entry to remove
    found = False
    new_entries = []
    for entry in entries:
        if entry.mountpoint == mountpoint:
            found = True
        else:
            new_entries.append(entry)

    if not found:
        return False

    # Create backup
    if create_backup:
        backup_fstab(fstab_path)

    # Write new fstab
    _write_fstab(new_entries, fstab_path)

    return True


def validate_entry(entry: FstabEntry) -> Tuple[bool, Optional[str]]:
    """
    Validate a fstab entry.

    Args:
        entry: FstabEntry to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)

    Example:
        >>> entry = FstabEntry("UUID=123", "/mnt/test", "ext4")
        >>> is_valid, error = validate_entry(entry)
        >>> if not is_valid:
        ...     print(f"Error: {error}")
    """
    # Check source
    if not entry.source:
        return False, "Source cannot be empty"

    # Check mountpoint
    if not entry.mountpoint:
        return False, "Mountpoint cannot be empty"

    if not entry.mountpoint.startswith("/"):
        return False, "Mountpoint must be absolute path"

    # Special mountpoints
    if entry.mountpoint in ("none", "swap"):
        # Valid for swap entries
        pass
    elif entry.mountpoint == "/":
        # Root partition
        pass
    else:
        # Check if mountpoint path is valid
        try:
            Path(entry.mountpoint)
        except (ValueError, OSError) as e:
            return False, f"Invalid mountpoint path: {e}"

    # Check filesystem type
    if not entry.fstype:
        return False, "Filesystem type cannot be empty"

    # Check options
    if not entry.options:
        return False, "Options cannot be empty (use 'defaults' at minimum)"

    # Check dump and pass numbers
    if entry.dump not in (0, 1, 2):
        return False, "Dump must be 0, 1, or 2"

    if entry.pass_num not in (0, 1, 2):
        return False, "Pass number must be 0, 1, or 2"

    return True, None


def preview_changes(
    entries: List[FstabEntry], fstab_path: str = "/etc/fstab"
) -> str:
    """
    Generate a preview of changes to fstab.

    Args:
        entries: New list of fstab entries
        fstab_path: Path to fstab file

    Returns:
        str: Diff-style preview of changes

    Example:
        >>> new_entries = parse_fstab()
        >>> new_entries.append(FstabEntry(...))
        >>> print(preview_changes(new_entries))
    """
    # Read current fstab
    try:
        with open(fstab_path, "r") as f:
            current_content = f.read()
    except FileNotFoundError:
        current_content = ""

    # Generate new content
    new_content = _generate_fstab_content(entries)

    # Simple diff
    current_lines = current_content.split("\n")
    new_lines = new_content.split("\n")

    preview = "=== fstab Changes Preview ===\n\n"
    preview += f"Current entries: {len(current_lines)} lines\n"
    preview += f"New entries: {len(new_lines)} lines\n\n"
    preview += "--- Current\n"
    preview += "+++ New\n\n"

    # Show differences
    max_lines = max(len(current_lines), len(new_lines))
    for i in range(max_lines):
        current = current_lines[i] if i < len(current_lines) else ""
        new = new_lines[i] if i < len(new_lines) else ""

        if current != new:
            if current:
                preview += f"- {current}\n"
            if new:
                preview += f"+ {new}\n"

    return preview


def _write_fstab(entries: List[FstabEntry], fstab_path: str) -> None:
    """
    Write entries to fstab file.

    Args:
        entries: List of fstab entries
        fstab_path: Path to fstab file
    """
    content = _generate_fstab_content(entries)

    with open(fstab_path, "w") as f:
        f.write(content)


def _generate_fstab_content(entries: List[FstabEntry]) -> str:
    """
    Generate fstab file content from entries.

    Args:
        entries: List of fstab entries

    Returns:
        str: Complete fstab file content
    """
    lines = ["# /etc/fstab: static file system information", ""]

    for entry in entries:
        if entry.comment:
            lines.append(f"# {entry.comment}")
        lines.append(str(entry))

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    # Test code
    print("=== Mountrix fstab Manager ===\n")

    try:
        # Try to parse system fstab
        entries = parse_fstab()
        print(f"Found {len(entries)} fstab entries:\n")

        for entry in entries:
            network_marker = " [NETWORK]" if entry.is_network else ""
            print(
                f"  {entry.mountpoint}: {entry.fstype} "
                f"({entry.source}){network_marker}"
            )
    except (FileNotFoundError, PermissionError) as e:
        print(f"Cannot read fstab: {e}")
        print("\nCreating test entry...")

        # Create test entry
        test_entry = FstabEntry(
            source="UUID=test-123",
            mountpoint="/mnt/test",
            fstype="ext4",
            options=["defaults", "nofail"],
            comment="Test entry created by Mountrix",
        )

        is_valid, error = validate_entry(test_entry)
        if is_valid:
            print("✓ Test entry is valid")
            print(f"  fstab line: {test_entry}")
        else:
            print(f"✗ Test entry invalid: {error}")
