# -*- coding: utf-8 -*-
"""
NAS Template Management for Mountrix.

This module handles loading and applying NAS configuration templates
for common NAS systems (FritzNAS, Synology, QNAP, etc.).
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from mountrix.core.fstab import FstabEntry


@dataclass
class NASTemplate:
    """Represents a NAS configuration template."""

    id: str  # Template ID (e.g., "fritznas")
    name: str  # Display name
    protocol: str  # nfs, cifs, smb
    default_port: int
    default_share_path: str  # Template path with placeholders
    default_options: List[str]
    auth_method: str  # credentials, none, key
    description: str
    help_url: str
    notes: Optional[str] = None
    nfs_support: bool = False
    nfs_options: Optional[List[str]] = None
    legacy_smb: bool = False


def get_templates_path() -> Path:
    """
    Get path to nas_templates.json file.

    Returns:
        Path: Path to templates file

    Raises:
        FileNotFoundError: If templates file not found
    """
    # Try multiple locations
    locations = [
        # Relative to this file (development)
        Path(__file__).parent.parent.parent / "data" / "nas_templates.json",
        # Current working directory
        Path.cwd() / "data" / "nas_templates.json",
        # Installed package
        Path(__file__).parent.parent / "data" / "nas_templates.json",
    ]

    for path in locations:
        if path.exists():
            return path

    raise FileNotFoundError(
        f"nas_templates.json not found. Tried: {', '.join(str(p) for p in locations)}"
    )


def load_templates() -> Dict[str, NASTemplate]:
    """
    Load all NAS templates from JSON file.

    Returns:
        Dict[str, NASTemplate]: Dictionary of template_id -> NASTemplate

    Raises:
        FileNotFoundError: If templates file not found
        json.JSONDecodeError: If JSON is invalid

    Example:
        >>> templates = load_templates()
        >>> print(f"Loaded {len(templates)} templates")
    """
    templates_path = get_templates_path()

    with open(templates_path, "r") as f:
        data = json.load(f)

    templates: Dict[str, NASTemplate] = {}

    for template_id, template_data in data.items():
        template = NASTemplate(
            id=template_id,
            name=template_data["name"],
            protocol=template_data["protocol"],
            default_port=template_data["default_port"],
            default_share_path=template_data["default_share_path"],
            default_options=template_data["default_options"],
            auth_method=template_data["auth_method"],
            description=template_data["description"],
            help_url=template_data["help_url"],
            notes=template_data.get("notes"),
            nfs_support=template_data.get("nfs_support", False),
            nfs_options=template_data.get("nfs_options"),
            legacy_smb=template_data.get("legacy_smb", False),
        )
        templates[template_id] = template

    return templates


def get_template(template_id: str) -> Optional[NASTemplate]:
    """
    Get a specific template by ID.

    Args:
        template_id: Template identifier (e.g., "fritznas", "synology")

    Returns:
        NASTemplate or None if not found

    Example:
        >>> template = get_template("fritznas")
        >>> if template:
        ...     print(f"Found: {template.name}")
    """
    templates = load_templates()
    return templates.get(template_id)


def list_templates() -> List[NASTemplate]:
    """
    Get list of all available templates.

    Returns:
        List[NASTemplate]: List of all templates

    Example:
        >>> templates = list_templates()
        >>> for t in templates:
        ...     print(f"{t.name}: {t.protocol}")
    """
    templates = load_templates()
    return list(templates.values())


def apply_template(
    template: NASTemplate, user_input: Dict[str, str], use_nfs: bool = False
) -> FstabEntry:
    """
    Apply a template with user-specific values.

    Args:
        template: NAS template to use
        user_input: Dictionary with user values:
            - host: Hostname or IP
            - share: Share name/path
            - mountpoint: Where to mount
            - username: (optional) Username
            - password: (optional) Password
            - credentials_file: (optional) Path to credentials file
        use_nfs: Use NFS instead of SMB/CIFS (if supported)

    Returns:
        FstabEntry: Configured fstab entry

    Raises:
        ValueError: If required fields missing or NFS not supported

    Example:
        >>> template = get_template("fritznas")
        >>> user_input = {
        ...     "host": "fritz.box",
        ...     "share": "USB-Storage",
        ...     "mountpoint": "/mnt/nas"
        ... }
        >>> entry = apply_template(template, user_input)
    """
    # Validate required fields
    required = ["host", "mountpoint"]
    missing = [f for f in required if f not in user_input]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Check NFS support
    if use_nfs and not template.nfs_support:
        raise ValueError(f"{template.name} does not support NFS")

    # Determine protocol and options
    if use_nfs:
        protocol = "nfs" if "nfs" in template.protocol else "nfs4"
        options = template.nfs_options or ["defaults"]
    else:
        protocol = template.protocol
        options = template.default_options.copy()

    # Build source path
    if protocol in ("cifs", "smb"):
        # SMB/CIFS format: //host/share
        share = user_input.get("share", "")
        source = f"//{user_input['host']}/{share}"
    elif protocol in ("nfs", "nfs4"):
        # NFS format: host:/export/path
        export = user_input.get("share", user_input.get("export", ""))
        source = f"{user_input['host']}:{export}"
    else:
        source = template.default_share_path.format(**user_input)

    # Add credentials if needed
    if template.auth_method == "credentials":
        if "credentials_file" in user_input:
            options.append(f"credentials={user_input['credentials_file']}")
        elif "username" in user_input:
            # Note: For security, credentials file is preferred
            options.append(f"username={user_input['username']}")
            if "password" in user_input:
                options.append(f"password={user_input['password']}")

    # Add UID/GID if provided (and not already in options)
    uid_str = f"uid={user_input.get('uid')}"
    gid_str = f"gid={user_input.get('gid')}"

    if "uid" in user_input and uid_str not in ",".join(options):
        options.append(uid_str)
    if "gid" in user_input and gid_str not in ",".join(options):
        options.append(gid_str)

    # Create fstab entry
    entry = FstabEntry(
        source=source,
        mountpoint=user_input["mountpoint"],
        fstype=protocol,
        options=options,
        dump=0,
        pass_num=0,
        comment=f"{template.name} - {template.description}",
    )

    return entry


def get_template_help(template_id: str) -> Optional[str]:
    """
    Get help information for a template.

    Args:
        template_id: Template identifier

    Returns:
        str: Help text with notes and URL, or None if not found

    Example:
        >>> help_text = get_template_help("fritznas")
        >>> print(help_text)
    """
    template = get_template(template_id)
    if not template:
        return None

    help_text = f"{template.name}\n"
    help_text += "=" * len(template.name) + "\n\n"
    help_text += f"{template.description}\n\n"

    if template.notes:
        help_text += f"Notes:\n{template.notes}\n\n"

    help_text += f"Protocol: {template.protocol.upper()}\n"
    help_text += f"Default Port: {template.default_port}\n"

    if template.nfs_support:
        help_text += "NFS Support: Yes\n"

    help_text += f"\nHelp: {template.help_url}\n"

    return help_text


if __name__ == "__main__":
    # Test code
    print("=== Mountrix NAS Templates ===\n")

    try:
        # List all templates
        templates = list_templates()
        print(f"Available Templates: {len(templates)}\n")

        for template in templates:
            nfs_marker = " [NFS]" if template.nfs_support else ""
            legacy_marker = " [Legacy SMB]" if template.legacy_smb else ""
            print(
                f"  - {template.name} ({template.id}): "
                f"{template.protocol.upper()}{nfs_marker}{legacy_marker}"
            )

        # Test applying a template
        print("\n--- Test: Applying FritzNAS Template ---")
        fritz_template = get_template("fritznas")
        if fritz_template:
            user_input = {
                "host": "fritz.box",
                "share": "USB-Storage",
                "mountpoint": "/mnt/fritznas",
                "uid": "1000",
                "gid": "1000",
            }
            entry = apply_template(fritz_template, user_input)
            print(f"Generated fstab entry:")
            print(f"  {entry}")

    except Exception as e:
        print(f"Error: {e}")
