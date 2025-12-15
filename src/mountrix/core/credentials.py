# -*- coding: utf-8 -*-
"""
Credentials management for Mountrix.

This module handles secure storage and retrieval of credentials:
- Keyring integration (GNOME Keyring, KWallet)
- Credential file generation for CIFS mounts
- SSH key validation
"""

import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

try:
    import keyring
    import keyring.errors

    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


@dataclass
class CredentialResult:
    """Result of a credential operation."""

    success: bool
    message: str
    file_path: Optional[str] = None
    username: Optional[str] = None


def is_keyring_available() -> bool:
    """
    Check if keyring is available and functional.

    Returns:
        bool: True if keyring can be used, False otherwise

    Example:
        >>> if is_keyring_available():
        ...     save_credentials_keyring("mynas", "user", "pass")
    """
    if not KEYRING_AVAILABLE:
        return False

    try:
        # Test if keyring backend is available
        backend = keyring.get_keyring()
        # Some backends like "fail" keyring are not functional
        return backend is not None and backend.priority > 0
    except Exception:
        return False


def save_credentials_keyring(service: str, username: str, password: str) -> CredentialResult:
    """
    Save credentials to system keyring (GNOME Keyring / KWallet).

    Args:
        service: Service name (e.g., "mountrix-nas1")
        username: Username
        password: Password

    Returns:
        CredentialResult: Result object with success status

    Example:
        >>> result = save_credentials_keyring("nas1", "admin", "secret")
        >>> if result.success:
        ...     print("Credentials saved to keyring")
    """
    if not service or not username:
        return CredentialResult(
            success=False, message="Service and username are required"
        )

    if not is_keyring_available():
        return CredentialResult(
            success=False,
            message="Keyring not available. Install python-keyring and a keyring backend.",
        )

    try:
        # Save password to keyring
        keyring.set_password(service, username, password)

        return CredentialResult(
            success=True,
            message=f"Credentials saved to keyring for {service}/{username}",
            username=username,
        )

    except keyring.errors.PasswordSetError as e:
        return CredentialResult(
            success=False, message=f"Failed to save to keyring: {str(e)}"
        )
    except Exception as e:
        return CredentialResult(
            success=False, message=f"Unexpected error saving credentials: {str(e)}"
        )


def load_credentials_keyring(service: str, username: str) -> Tuple[bool, Optional[str]]:
    """
    Load credentials from system keyring.

    Args:
        service: Service name (e.g., "mountrix-nas1")
        username: Username

    Returns:
        Tuple[bool, Optional[str]]: (success, password)

    Example:
        >>> success, password = load_credentials_keyring("nas1", "admin")
        >>> if success:
        ...     print(f"Password: {password}")
    """
    if not service or not username:
        return False, None

    if not is_keyring_available():
        return False, None

    try:
        password = keyring.get_password(service, username)
        if password is None:
            return False, None
        return True, password

    except Exception:
        return False, None


def delete_credentials_keyring(service: str, username: str) -> CredentialResult:
    """
    Delete credentials from system keyring.

    Args:
        service: Service name
        username: Username

    Returns:
        CredentialResult: Result object with success status

    Example:
        >>> result = delete_credentials_keyring("nas1", "admin")
        >>> if result.success:
        ...     print("Credentials deleted")
    """
    if not service or not username:
        return CredentialResult(
            success=False, message="Service and username are required"
        )

    if not is_keyring_available():
        return CredentialResult(success=False, message="Keyring not available")

    try:
        keyring.delete_password(service, username)
        return CredentialResult(
            success=True, message=f"Credentials deleted from keyring for {service}/{username}"
        )
    except keyring.errors.PasswordDeleteError:
        # Credential doesn't exist - that's fine
        return CredentialResult(
            success=True, message=f"No credentials found for {service}/{username}"
        )
    except Exception as e:
        return CredentialResult(
            success=False, message=f"Error deleting credentials: {str(e)}"
        )


def generate_credentials_file(
    username: str, password: str, domain: Optional[str] = None
) -> CredentialResult:
    """
    Generate a CIFS credentials file for use with mount.cifs.

    Creates a file in ~/.mountrix/credentials/ with format:
    username=<username>
    password=<password>
    domain=<domain>

    File permissions are set to 600 (owner read/write only).

    Args:
        username: Username
        password: Password
        domain: Optional Windows domain

    Returns:
        CredentialResult: Result with file_path on success

    Example:
        >>> result = generate_credentials_file("admin", "secret", "WORKGROUP")
        >>> if result.success:
        ...     print(f"Credential file: {result.file_path}")
    """
    if not username:
        return CredentialResult(success=False, message="Username is required")

    # Create credentials directory
    cred_dir = Path.home() / ".mountrix" / "credentials"

    try:
        cred_dir.mkdir(parents=True, exist_ok=True)
        # Set directory permissions to 700
        cred_dir.chmod(stat.S_IRWXU)  # 700
    except Exception as e:
        return CredentialResult(
            success=False, message=f"Failed to create credentials directory: {str(e)}"
        )

    # Generate unique filename based on hash of username+domain
    hash_input = f"{username}:{domain or ''}"
    file_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    cred_file = cred_dir / f"{file_hash}.cred"

    # Build credentials content
    content = f"username={username}\n"
    if password:
        content += f"password={password}\n"
    if domain:
        content += f"domain={domain}\n"

    try:
        # Write credentials file
        cred_file.write_text(content)

        # Set file permissions to 600 (owner read/write only)
        cred_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600

        return CredentialResult(
            success=True,
            message=f"Credential file created: {cred_file}",
            file_path=str(cred_file),
            username=username,
        )

    except Exception as e:
        return CredentialResult(
            success=False, message=f"Failed to create credential file: {str(e)}"
        )


def delete_credentials_file(file_path: str) -> CredentialResult:
    """
    Delete a credentials file.

    Args:
        file_path: Path to credentials file

    Returns:
        CredentialResult: Result object with success status

    Example:
        >>> result = delete_credentials_file("/home/user/.mountrix/credentials/abc123.cred")
        >>> if result.success:
        ...     print("File deleted")
    """
    if not file_path:
        return CredentialResult(success=False, message="File path is required")

    cred_file = Path(file_path)

    if not cred_file.exists():
        return CredentialResult(
            success=True, message="Credential file does not exist"
        )

    # Security check: ensure file is in .mountrix/credentials/
    try:
        cred_dir = Path.home() / ".mountrix" / "credentials"
        if cred_dir not in cred_file.parents and cred_file.parent != cred_dir:
            return CredentialResult(
                success=False,
                message="Security: File must be in ~/.mountrix/credentials/",
            )
    except Exception:
        return CredentialResult(
            success=False, message="Invalid file path"
        )

    try:
        cred_file.unlink()
        return CredentialResult(
            success=True, message=f"Credential file deleted: {file_path}"
        )
    except Exception as e:
        return CredentialResult(
            success=False, message=f"Failed to delete file: {str(e)}"
        )


def validate_ssh_key(key_path: str) -> Tuple[bool, str]:
    """
    Validate an SSH private key file.

    Checks:
    - File exists
    - File is readable
    - File has secure permissions (600 or 400)
    - File contains valid SSH key header

    Args:
        key_path: Path to SSH private key

    Returns:
        Tuple[bool, str]: (is_valid, error_message)

    Example:
        >>> valid, error = validate_ssh_key("/home/user/.ssh/id_rsa")
        >>> if valid:
        ...     print("SSH key is valid")
        ... else:
        ...     print(f"Invalid: {error}")
    """
    if not key_path:
        return False, "Key path is required"

    key_file = Path(key_path)

    # Check if file exists
    if not key_file.exists():
        return False, f"Key file does not exist: {key_path}"

    # Check if it's a file (not a directory)
    if not key_file.is_file():
        return False, f"Path is not a file: {key_path}"

    # Check file permissions (should be 600 or 400)
    try:
        file_stat = key_file.stat()
        mode = file_stat.st_mode
        # Extract permission bits
        perms = stat.filemode(mode)

        # Check if others or group have any permissions
        if mode & (stat.S_IRWXG | stat.S_IRWXO):
            return False, f"Insecure permissions: {perms}. SSH key must be 600 or 400."

    except Exception as e:
        return False, f"Cannot check permissions: {str(e)}"

    # Try to read and validate key content
    try:
        content = key_file.read_text()

        # Check for common SSH key headers
        valid_headers = [
            "-----BEGIN RSA PRIVATE KEY-----",
            "-----BEGIN DSA PRIVATE KEY-----",
            "-----BEGIN EC PRIVATE KEY-----",
            "-----BEGIN OPENSSH PRIVATE KEY-----",
            "-----BEGIN PRIVATE KEY-----",
            "-----BEGIN ENCRYPTED PRIVATE KEY-----",
        ]

        if not any(header in content for header in valid_headers):
            return False, "File does not appear to be a valid SSH private key"

        return True, "Valid SSH key"

    except UnicodeDecodeError:
        # Binary key file (encrypted) - consider valid if other checks passed
        return True, "Valid SSH key (binary/encrypted)"
    except Exception as e:
        return False, f"Cannot read key file: {str(e)}"


def get_credential_files() -> list[str]:
    """
    List all credential files in ~/.mountrix/credentials/.

    Returns:
        list[str]: List of credential file paths

    Example:
        >>> files = get_credential_files()
        >>> for f in files:
        ...     print(f)
    """
    cred_dir = Path.home() / ".mountrix" / "credentials"

    if not cred_dir.exists():
        return []

    try:
        return [str(f) for f in cred_dir.glob("*.cred") if f.is_file()]
    except Exception:
        return []


def read_credentials_file(file_path: str) -> Tuple[bool, dict]:
    """
    Read and parse a credentials file.

    Args:
        file_path: Path to credentials file

    Returns:
        Tuple[bool, dict]: (success, credentials_dict)
            credentials_dict contains: username, password, domain

    Example:
        >>> success, creds = read_credentials_file("/home/user/.mountrix/credentials/abc.cred")
        >>> if success:
        ...     print(f"Username: {creds.get('username')}")
    """
    if not file_path:
        return False, {}

    cred_file = Path(file_path)

    if not cred_file.exists():
        return False, {}

    try:
        content = cred_file.read_text()
        credentials = {}

        for line in content.splitlines():
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                credentials[key.strip()] = value.strip()

        return True, credentials

    except Exception:
        return False, {}
