# -*- coding: utf-8 -*-
"""
Tests for fstab.py

Tests fstab parsing, backup, validation, and manipulation.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mountrix.core.fstab import (
    FstabEntry,
    add_entry,
    backup_fstab,
    parse_fstab,
    preview_changes,
    remove_entry,
    validate_entry,
)


@pytest.fixture
def sample_fstab():
    """Create a temporary fstab file for testing."""
    content = """# /etc/fstab: static file system information
UUID=abc-123	/	ext4	defaults	0	1
UUID=def-456	/boot	ext4	defaults	0	2
UUID=ghi-789	/home	ext4	defaults,noatime	0	2
# My NAS
//nas.local/share	/mnt/nas	cifs	credentials=/home/user/.nascreds,uid=1000	0	0
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fstab") as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_backup_dir():
    """Create temporary backup directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestFstabEntry:
    """Tests for FstabEntry dataclass."""

    def test_entry_creation(self):
        """Test creating a fstab entry."""
        entry = FstabEntry(
            source="UUID=test-123",
            mountpoint="/mnt/data",
            fstype="ext4",
            options=["defaults", "nofail"],
        )
        assert entry.source == "UUID=test-123"
        assert entry.mountpoint == "/mnt/data"
        assert entry.fstype == "ext4"
        assert "defaults" in entry.options

    def test_entry_to_string(self):
        """Test converting entry to fstab line."""
        entry = FstabEntry(
            source="UUID=test-123",
            mountpoint="/mnt/data",
            fstype="ext4",
            options=["defaults", "nofail"],
            dump=0,
            pass_num=2,
        )
        line = str(entry)
        assert "UUID=test-123" in line
        assert "/mnt/data" in line
        assert "ext4" in line
        assert "defaults,nofail" in line

    def test_is_network_property(self):
        """Test is_network property."""
        nfs_entry = FstabEntry("server:/export", "/mnt/nfs", "nfs")
        assert nfs_entry.is_network == True

        cifs_entry = FstabEntry("//server/share", "/mnt/smb", "cifs")
        assert cifs_entry.is_network == True

        local_entry = FstabEntry("UUID=123", "/", "ext4")
        assert local_entry.is_network == False

    def test_is_uuid_property(self):
        """Test is_uuid property."""
        uuid_entry = FstabEntry("UUID=abc-123", "/", "ext4")
        assert uuid_entry.is_uuid == True

        label_entry = FstabEntry("LABEL=ROOT", "/", "ext4")
        assert uuid_entry.is_uuid == True

        device_entry = FstabEntry("/dev/sda1", "/", "ext4")
        assert device_entry.is_uuid == False

    def test_is_label_property(self):
        """Test is_label property."""
        label_entry = FstabEntry("LABEL=ROOT", "/", "ext4")
        assert label_entry.is_label == True

        uuid_entry = FstabEntry("UUID=abc-123", "/", "ext4")
        assert uuid_entry.is_label == False


class TestParseFstab:
    """Tests for fstab parsing."""

    def test_parse_sample_fstab(self, sample_fstab):
        """Test parsing a sample fstab file."""
        entries = parse_fstab(sample_fstab)

        assert len(entries) == 4

        # Check first entry
        assert entries[0].source == "UUID=abc-123"
        assert entries[0].mountpoint == "/"
        assert entries[0].fstype == "ext4"

        # Check network entry
        assert entries[3].mountpoint == "/mnt/nas"
        assert entries[3].is_network == True
        assert entries[3].comment == "My NAS"

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            parse_fstab("/nonexistent/fstab")

    def test_parse_empty_fstab(self):
        """Test parsing empty fstab."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("# Just comments\n\n")
            temp_path = f.name

        try:
            entries = parse_fstab(temp_path)
            assert len(entries) == 0
        finally:
            Path(temp_path).unlink()


class TestBackupFstab:
    """Tests for fstab backup functionality."""

    def test_backup_creates_file(self, sample_fstab, temp_backup_dir):
        """Test that backup creates a file."""
        backup_path = backup_fstab(sample_fstab, temp_backup_dir)

        assert Path(backup_path).exists()
        assert "fstab.backup" in backup_path

    def test_backup_preserves_content(self, sample_fstab, temp_backup_dir):
        """Test that backup preserves file content."""
        backup_path = backup_fstab(sample_fstab, temp_backup_dir)

        with open(sample_fstab, "r") as original:
            original_content = original.read()

        with open(backup_path, "r") as backup:
            backup_content = backup.read()

        assert original_content == backup_content

    def test_backup_nonexistent_file(self, temp_backup_dir):
        """Test backup of non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            backup_fstab("/nonexistent/fstab", temp_backup_dir)


class TestValidateEntry:
    """Tests for entry validation."""

    def test_validate_valid_entry(self):
        """Test validating a valid entry."""
        entry = FstabEntry(
            source="UUID=test-123",
            mountpoint="/mnt/data",
            fstype="ext4",
            options=["defaults"],
        )
        is_valid, error = validate_entry(entry)
        assert is_valid == True
        assert error is None

    def test_validate_empty_source(self):
        """Test validation fails for empty source."""
        entry = FstabEntry(source="", mountpoint="/mnt/data", fstype="ext4")
        is_valid, error = validate_entry(entry)
        assert is_valid == False
        assert "Source" in error

    def test_validate_empty_mountpoint(self):
        """Test validation fails for empty mountpoint."""
        entry = FstabEntry(source="UUID=123", mountpoint="", fstype="ext4")
        is_valid, error = validate_entry(entry)
        assert is_valid == False
        assert "Mountpoint" in error

    def test_validate_relative_mountpoint(self):
        """Test validation fails for relative mountpoint."""
        entry = FstabEntry(
            source="UUID=123", mountpoint="relative/path", fstype="ext4"
        )
        is_valid, error = validate_entry(entry)
        assert is_valid == False
        assert "absolute" in error.lower()

    def test_validate_empty_fstype(self):
        """Test validation fails for empty filesystem type."""
        entry = FstabEntry(source="UUID=123", mountpoint="/mnt/data", fstype="")
        is_valid, error = validate_entry(entry)
        assert is_valid == False
        assert "Filesystem" in error

    def test_validate_invalid_dump(self):
        """Test validation fails for invalid dump value."""
        entry = FstabEntry(
            source="UUID=123", mountpoint="/mnt/data", fstype="ext4", dump=5
        )
        is_valid, error = validate_entry(entry)
        assert is_valid == False
        assert "Dump" in error


class TestAddEntry:
    """Tests for adding entries to fstab."""

    def test_add_entry_success(self, sample_fstab, temp_backup_dir):
        """Test successfully adding an entry."""
        new_entry = FstabEntry(
            source="UUID=new-999",
            mountpoint="/mnt/newdrive",
            fstype="ext4",
            options=["defaults", "nofail"],
        )

        result = add_entry(new_entry, sample_fstab, create_backup=False)
        assert result == True

        # Verify entry was added
        entries = parse_fstab(sample_fstab)
        assert len(entries) == 5
        assert entries[-1].mountpoint == "/mnt/newdrive"

    def test_add_entry_duplicate_mountpoint(self, sample_fstab):
        """Test adding entry with existing mountpoint fails."""
        duplicate_entry = FstabEntry(
            source="UUID=dup-123", mountpoint="/", fstype="ext4"
        )

        with pytest.raises(ValueError, match="already exists"):
            add_entry(duplicate_entry, sample_fstab, create_backup=False)

    def test_add_entry_invalid(self, sample_fstab):
        """Test adding invalid entry fails."""
        invalid_entry = FstabEntry(source="", mountpoint="/mnt/test", fstype="ext4")

        with pytest.raises(ValueError, match="Invalid"):
            add_entry(invalid_entry, sample_fstab, create_backup=False)


class TestRemoveEntry:
    """Tests for removing entries from fstab."""

    def test_remove_entry_success(self, sample_fstab):
        """Test successfully removing an entry."""
        result = remove_entry("/mnt/nas", sample_fstab, create_backup=False)
        assert result == True

        # Verify entry was removed
        entries = parse_fstab(sample_fstab)
        assert len(entries) == 3
        assert not any(e.mountpoint == "/mnt/nas" for e in entries)

    def test_remove_nonexistent_entry(self, sample_fstab):
        """Test removing non-existent entry returns False."""
        result = remove_entry("/nonexistent", sample_fstab, create_backup=False)
        assert result == False


class TestPreviewChanges:
    """Tests for change preview functionality."""

    def test_preview_changes(self, sample_fstab):
        """Test preview of changes."""
        entries = parse_fstab(sample_fstab)
        entries.append(
            FstabEntry(
                source="UUID=new-123",
                mountpoint="/mnt/new",
                fstype="ext4",
                options=["defaults"],
            )
        )

        preview = preview_changes(entries, sample_fstab)

        assert "Preview" in preview
        assert "/mnt/new" in preview
        assert "+" in preview  # Added line marker
