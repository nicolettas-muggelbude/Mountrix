# -*- coding: utf-8 -*-
"""
Tests for templates.py

Tests NAS template loading and application.
"""

import pytest

from mountrix.core.templates import (
    NASTemplate,
    apply_template,
    get_template,
    get_template_help,
    list_templates,
    load_templates,
)


class TestLoadTemplates:
    """Tests for template loading."""

    def test_load_templates_returns_dict(self):
        """Test that load_templates returns a dictionary."""
        templates = load_templates()
        assert isinstance(templates, dict)
        assert len(templates) > 0

    def test_load_templates_has_expected_templates(self):
        """Test that expected templates are present."""
        templates = load_templates()
        expected_ids = ["fritznas", "synology", "qnap", "wd_mycloud", "ugreen"]
        
        for template_id in expected_ids:
            assert template_id in templates

    def test_loaded_template_structure(self):
        """Test that loaded templates have correct structure."""
        templates = load_templates()
        template = templates["fritznas"]
        
        assert isinstance(template, NASTemplate)
        assert template.id == "fritznas"
        assert template.name == "AVM FRITZ!NAS"
        assert template.protocol == "cifs"
        assert template.default_port == 445
        assert isinstance(template.default_options, list)
        assert len(template.default_options) > 0


class TestGetTemplate:
    """Tests for getting specific templates."""

    def test_get_existing_template(self):
        """Test getting an existing template."""
        template = get_template("fritznas")
        assert template is not None
        assert template.name == "AVM FRITZ!NAS"

    def test_get_nonexistent_template(self):
        """Test getting a non-existent template returns None."""
        template = get_template("nonexistent")
        assert template is None

    def test_get_synology_template(self):
        """Test getting Synology template."""
        template = get_template("synology")
        assert template is not None
        assert template.name == "Synology DiskStation"
        assert template.nfs_support == True

    def test_get_wd_template_legacy_smb(self):
        """Test that WD My Cloud has legacy SMB flag."""
        template = get_template("wd_mycloud")
        assert template is not None
        assert template.legacy_smb == True


class TestListTemplates:
    """Tests for listing all templates."""

    def test_list_templates_returns_list(self):
        """Test that list_templates returns a list."""
        templates = list_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0

    def test_list_templates_contains_nastemplate_objects(self):
        """Test that list contains NASTemplate objects."""
        templates = list_templates()
        for template in templates:
            assert isinstance(template, NASTemplate)

    def test_list_templates_count(self):
        """Test that we have expected number of templates."""
        templates = list_templates()
        # We have 7 templates: fritznas, synology, qnap, wd_mycloud, ugreen, generic_nfs, generic_smb
        assert len(templates) >= 7


class TestApplyTemplate:
    """Tests for applying templates."""

    def test_apply_fritznas_template(self):
        """Test applying FritzNAS template."""
        template = get_template("fritznas")
        user_input = {
            "host": "fritz.box",
            "share": "USB-Storage",
            "mountpoint": "/mnt/nas",
        }
        
        entry = apply_template(template, user_input)
        
        assert entry.source == "//fritz.box/USB-Storage"
        assert entry.mountpoint == "/mnt/nas"
        assert entry.fstype == "cifs"
        assert "vers=3.0" in entry.options
        assert "nofail" in entry.options

    def test_apply_template_with_credentials(self):
        """Test applying template with credentials file."""
        template = get_template("synology")
        user_input = {
            "host": "192.168.1.100",
            "share": "data",
            "mountpoint": "/mnt/synology",
            "credentials_file": "/home/user/.smb_creds",
        }
        
        entry = apply_template(template, user_input)
        
        assert "credentials=/home/user/.smb_creds" in entry.options

    def test_apply_template_with_uid_gid(self):
        """Test applying template with UID/GID."""
        template = get_template("fritznas")
        user_input = {
            "host": "fritz.box",
            "share": "data",
            "mountpoint": "/mnt/nas",
            "uid": "1000",
            "gid": "1000",
        }
        
        entry = apply_template(template, user_input)
        
        # Check that uid and gid are in options
        options_str = ",".join(entry.options)
        assert "uid=1000" in options_str
        assert "gid=1000" in options_str

    def test_apply_template_missing_required_fields(self):
        """Test that missing required fields raises error."""
        template = get_template("fritznas")
        user_input = {
            "host": "fritz.box",
            # Missing mountpoint
        }
        
        with pytest.raises(ValueError, match="Missing required fields"):
            apply_template(template, user_input)

    def test_apply_nfs_template(self):
        """Test applying generic NFS template."""
        template = get_template("generic_nfs")
        user_input = {
            "host": "192.168.1.100",
            "share": "/export/data",
            "mountpoint": "/mnt/nfs",
        }
        
        entry = apply_template(template, user_input)
        
        assert entry.source == "192.168.1.100:/export/data"
        assert entry.fstype == "nfs"
        assert "nfsvers=4" in entry.options

    def test_apply_template_with_nfs_option(self):
        """Test applying template with NFS instead of SMB."""
        template = get_template("synology")
        user_input = {
            "host": "synology.local",
            "share": "/volume1/data",
            "mountpoint": "/mnt/synology",
        }
        
        entry = apply_template(template, user_input, use_nfs=True)
        
        assert entry.fstype in ("nfs", "nfs4")
        assert template.nfs_support == True

    def test_apply_template_nfs_not_supported(self):
        """Test that requesting NFS on non-NFS template fails."""
        template = get_template("fritznas")
        user_input = {
            "host": "fritz.box",
            "share": "data",
            "mountpoint": "/mnt/nas",
        }
        
        with pytest.raises(ValueError, match="does not support NFS"):
            apply_template(template, user_input, use_nfs=True)

    def test_apply_template_adds_comment(self):
        """Test that applied template includes comment."""
        template = get_template("qnap")
        user_input = {
            "host": "qnap.local",
            "share": "share1",
            "mountpoint": "/mnt/qnap",
        }
        
        entry = apply_template(template, user_input)
        
        assert entry.comment is not None
        assert "QNAP" in entry.comment


class TestGetTemplateHelp:
    """Tests for template help text."""

    def test_get_help_for_existing_template(self):
        """Test getting help for existing template."""
        help_text = get_template_help("fritznas")
        
        assert help_text is not None
        assert "FRITZ" in help_text
        assert "CIFS" in help_text.upper()
        assert "445" in help_text  # Port

    def test_get_help_for_nonexistent_template(self):
        """Test getting help for non-existent template returns None."""
        help_text = get_template_help("nonexistent")
        assert help_text is None

    def test_help_includes_notes(self):
        """Test that help includes notes if present."""
        help_text = get_template_help("fritznas")
        # FritzNAS template has notes
        assert "fritz.box" in help_text.lower()


class TestNASTemplateDataclass:
    """Tests for NASTemplate dataclass."""

    def test_create_template(self):
        """Test creating a NASTemplate."""
        template = NASTemplate(
            id="test",
            name="Test NAS",
            protocol="cifs",
            default_port=445,
            default_share_path="//test/share",
            default_options=["defaults"],
            auth_method="credentials",
            description="Test template",
            help_url="https://example.com",
        )
        
        assert template.id == "test"
        assert template.name == "Test NAS"
        assert template.nfs_support == False  # Default

    def test_template_with_nfs_support(self):
        """Test template with NFS support."""
        template = NASTemplate(
            id="test",
            name="Test NAS",
            protocol="cifs",
            default_port=445,
            default_share_path="//test/share",
            default_options=["defaults"],
            auth_method="credentials",
            description="Test",
            help_url="https://example.com",
            nfs_support=True,
            nfs_options=["nfsvers=4"],
        )
        
        assert template.nfs_support == True
        assert template.nfs_options == ["nfsvers=4"]
