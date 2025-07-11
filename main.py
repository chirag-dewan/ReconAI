#!/usr/bin/env python3
"""
ReconGPT - AI-Powered Reconnaissance Assistant
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
    print("[+] ReconGPT directories initialized")

def main():
    # Import utilities for banner and validation
    try:
        from cli.utils.helpers import print_banner, validate_target
        banner_available = True
    except ImportError:
        banner_available = False
    
    parser = argparse.ArgumentParser(
        description='ReconGPT - AI-Powered Reconnaissance Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Simple target argument (no mutually exclusive group)
    parser.add_argument(
        '-t', '--target',
        help='Target to scan (domain, IP, CIDR, or organization name)'
    )
    
    parser.add_argument(
        '--style',
        choices=['stealth', 'aggressive', 'phishing', 'quick'],
        default='aggressive',
        help='Reconnaissance style (default: aggressive)'
    )
    
    parser.add_argument(
        '--tool',
        choices=['bbot', 'spiderfoot', 'google-dorks', 'all'],
        default='bbot',
        help='Primary reconnaissance tool (default: bbot)'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Enable AI-powered analysis and prioritization'
    )
    
    parser.add_argument(
        '--dorks',
        action='store_true',
        help='Generate custom Google Dorks for target'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'html', 'markdown', 'all'],
        default='text',
        help='Output format for results (default: text)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Directory to store results (default: output)'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Show configuration and validation status'
    )
    
    parser.add_argument(
        '--health',
        action='store_true',
        help='Run comprehensive health check'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='ReconGPT v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Print banner
    if banner_available and not args.verbose:
        print("""
╔══════════════════════════════════════════════════════════╗
║                        ReconGPT                          ║
║        AI-Powered Reconnaissance Assistant               ║
║                                                          ║
║    🤖 GPT-4 Analysis     🎯 Target Prioritization       ║
║    🔍 Custom Dorks       📊 Intelligence Reports        ║
╚══════════════════════════════════════════════════════════╝
        """)
    
    # Setup directories
    setup_directories()
    
    try:
        # Handle utility commands first
        if args.health:
            from cli.utils.project_status import check_project_health, print_health_status
            health_results = check_project_health()
            print_health_status(health_results)
            return 0 if health_results['overall_status'] != 'critical' else 1
        
        if args.config:
            from cli.core.config import Config
            config = Config()
            validation = config.validate()
            print("[+] ReconGPT Configuration Status:")
            print(f"Valid: {'✓' if validation['valid'] else '✗'}")
            print(f"OpenAI API Key: {'✓' if config.get_openai_api_key() else '✗'}")
            return 0
        
        # Check if target is provided
        if not args.target:
            print("[ERROR] No target specified. Use -t <target> or --help for usage.")
            return 1
        
        # Validate target
        if banner_available:
            target_info = validate_target(args.target)
            if not target_info['valid']:
                print(f"[ERROR] Invalid target: {args.target}")
                return 1
            print(f"[+] Target validated: {target_info['normalized']} ({target_info['type']})")
        
        # Initialize and run reconnaissance
        from cli.core.config import Config
        from cli.core.logging_setup import setup_logging
        from cli.core.orchestrator import ReconOrchestrator
        
        config = Config()
        setup_logging(
            log_level=config.get_log_level(),
            log_file='recongpt.log' if args.verbose else None,
            verbose=args.verbose
        )
        
        orchestrator = ReconOrchestrator(
            output_dir=args.output_dir,
            verbose=args.verbose,
            config=config
        )
        
        print(f"[+] Processing target: {args.target}")
        print(f"[+] Style: {args.style}")
        print(f"[+] Tool: {args.tool}")
        print(f"[+] AI Analysis: {'Enabled' if args.analyze else 'Disabled'}")
        print(f"[+] Custom Dorks: {'Enabled' if args.dorks else 'Disabled'}")
        
        # Run reconnaissance
        results = orchestrator.run_reconnaissance(
            target=args.target,
            tool=args.tool,
            analyze=args.analyze,
            style=args.style,
            generate_dorks=args.dorks
        )
        
        # Generate and display summary
        summary = orchestrator.generate_summary_report(results)
        print(summary)
        
        # Save results in requested format
        from cli.core.results_formatter import ResultsFormatter
        formatter = ResultsFormatter(output_dir=args.output_dir)
        
        if args.format == 'all':
            formatter.save_text_report(results)
            formatter.save_json_report(results)
            formatter.save_html_report(results)
        elif args.format == 'json':
            formatter.save_json_report(results)
        elif args.format == 'html':
            formatter.save_html_report(results)
        else:
            formatter.save_text_report(results)
        
        return 0 if results['success'] else 1
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[!] Operation interrupted by user")
        sys.exit(1)
