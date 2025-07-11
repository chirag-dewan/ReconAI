"""
Utility functions for ReconAI
"""

import os
import re
import ipaddress
from pathlib import Path
from typing import Union, List, Dict, Optional
from urllib.parse import urlparse

def validate_target(target: str) -> Dict[str, Union[str, bool]]:
    """
    Validate and categorize the target input
    
    Args:
        target: Target string (domain, IP, CIDR, org name)
        
    Returns:
        Dict with validation results and target type
    """
    if not target:
        return {
            'valid': False,
            'type': 'unknown',
            'target': '',
            'normalized': '',
            'warnings': ['Target cannot be empty']
        }
    
    target = target.strip()
    
    result = {
        'valid': False,
        'type': 'unknown',
        'target': target,
        'normalized': target,
        'warnings': []
    }
    
    # Check if it's an IP address
    try:
        ip = ipaddress.ip_address(target)
        result['valid'] = True
        result['type'] = 'ip'
        result['normalized'] = str(ip)
        return result
    except ValueError:
        pass
    
    # Check if it's a CIDR range
    try:
        network = ipaddress.ip_network(target, strict=False)
        result['valid'] = True
        result['type'] = 'cidr'
        result['normalized'] = str(network)
        if network.num_addresses > 1000:
            result['warnings'].append(f"Large network ({network.num_addresses} addresses)")
        return result
    except ValueError:
        pass
    
    # Check if it's a domain name
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    
    if domain_pattern.match(target):
        result['valid'] = True
        result['type'] = 'domain'
        result['normalized'] = target.lower()
        
        # Check for common issues
        if target.startswith('www.'):
            result['warnings'].append("Consider scanning root domain without 'www.'")
        
        return result
    
    # Check if it's a URL
    try:
        parsed = urlparse(target)
        if parsed.scheme and parsed.netloc:
            result['valid'] = True
            result['type'] = 'url'
            result['normalized'] = parsed.netloc.lower()
            result['warnings'].append("Using hostname from URL for scanning")
            return result
    except Exception:
        pass
    
    # If none of the above, treat as organization name
    if len(target) > 2 and not any(char in target for char in ['/', '\\', '<', '>', '|']):
        result['valid'] = True
        result['type'] = 'organization'
        result['normalized'] = target
        result['warnings'].append("Organization names may have limited tool support")
        return result
    
    # Invalid target
    result['warnings'].append("Target format not recognized")
    return result

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be safe for use as a filename
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    filename = re.sub(r'_+', '_', filename)  # Replace multiple underscores with single
    filename = filename.strip('_.')  # Remove leading/trailing underscores and dots
    
    # Ensure it's not empty and not too long
    if not filename:
        filename = "unnamed"
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"

def get_file_info(filepath: Union[str, Path]) -> Dict:
    """
    Get information about a file
    
    Args:
        filepath: Path to file
        
    Returns:
        Dict with file information
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return {'exists': False}
    
    stat = filepath.stat()
    
    return {
        'exists': True,
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'modified': stat.st_mtime,
        'is_file': filepath.is_file(),
        'is_dir': filepath.is_dir(),
        'extension': filepath.suffix.lower(),
        'name': filepath.name
    }

def load_wordlist(filepath: Union[str, Path]) -> List[str]:
    """
    Load a wordlist file
    
    Args:
        filepath: Path to wordlist file
        
    Returns:
        List of words/lines
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Wordlist not found: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        return words
    except Exception as e:
        raise RuntimeError(f"Failed to load wordlist: {e}")

def check_disk_space(directory: Union[str, Path], min_space_mb: int = 100) -> Dict:
    """
    Check available disk space
    
    Args:
        directory: Directory to check
        min_space_mb: Minimum required space in MB
        
    Returns:
        Dict with space information
    """
    directory = Path(directory)
    
    try:
        import shutil
        total, used, free = shutil.disk_usage(directory)
        
        free_mb = free / (1024 * 1024)
        
        return {
            'total': total,
            'used': used,
            'free': free,
            'free_mb': free_mb,
            'sufficient': free_mb >= min_space_mb,
            'warning': free_mb < min_space_mb
        }
    except Exception as e:
        return {
            'error': str(e),
            'sufficient': False,
            'warning': True
        }

def create_banner() -> str:
    """
    Create ASCII banner for ReconAI
    
    Returns:
        Banner string
    """
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                        ReconAI                           ║
    ║            Automated Reconnaissance with AI              ║
    ║                                                          ║
    ║    🔍 Multi-tool Integration  🧠 AI-Powered Analysis     ║
    ║    📊 Smart Prioritization   📋 Detailed Reports        ║
    ╚══════════════════════════════════════════════════════════╝
    """
    return banner.strip()

def print_banner():
    """Print the ReconAI banner"""
    print(create_banner())

def validate_api_key(api_key: str) -> bool:
    """
    Basic validation for OpenAI API key format
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if format looks valid
    """
    if not api_key:
        return False
    
    # OpenAI API keys typically start with 'sk-' and are 51 characters long
    if api_key.startswith('sk-') and len(api_key) >= 40:
        return True
    
    return False

def get_terminal_width() -> int:
    """
    Get terminal width, with fallback
    
    Returns:
        Terminal width in characters
    """
    try:
        import shutil
        width = shutil.get_terminal_size().columns
        return max(width, 80)  # Minimum width of 80
    except Exception:
        return 80  # Default fallback