#!/usr/bin/env python3
"""
ReconAI - Automated Reconnaissance with AI Analysis
A tool for running security reconnaissance and getting AI-powered insights
"""

import argparse
import sys
import os
from pathlib import Path

def setup_directories():
    """Create necessary directories for the project"""
    dirs = ['output', 'config', 'logs']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("[+] Project directories initialized")

def main():
    parser = argparse.ArgumentParser(
        description='ReconAI - Automated Reconnaissance with AI Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -t example.com --tool bbot
  %(prog)s -t 192.168.1.0/24 --tool spiderfoot
  %(prog)s -t "Acme Corp" --tool all --analyze
        """
    )
    
    parser.add_argument(
        '-t', '--target',
        required=True,
        help='Target to scan (domain, IP, CIDR, or organization name)'
    )
    
    parser.add_argument(
        '--tool',
        choices=['bbot', 'spiderfoot', 'google-dorks', 'all'],
        default='bbot',
        help='Reconnaissance tool to use (default: bbot)'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Enable AI analysis of results'
    )
    
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Directory to store results (default: output)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='ReconAI v0.1.0'
    )
    
    args = parser.parse_args()
    
    # Setup project structure
    setup_directories()
    
    print(f"[+] ReconAI v0.1.0")
    print(f"[+] Target: {args.target}")
    print(f"[+] Tool: {args.tool}")
    print(f"[+] AI Analysis: {'Enabled' if args.analyze else 'Disabled'}")
    print(f"[+] Output Directory: {args.output_dir}")
    
    if args.verbose:
        print(f"[DEBUG] Verbose mode enabled")
    
    # TODO: Implement tool execution
    print("[!] Tool execution not yet implemented")
    print("[!] This is the initial CLI structure")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)