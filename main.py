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
    # Import utilities for banner and validation
    try:
        from cli.utils.helpers import print_banner, validate_target
        banner_available = True
    except ImportError:
        banner_available = False
    
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
        # Make target optional for config commands
        '-t', '--target',
        required=not any(arg in sys.argv for arg in ['--config', '--create-config', '--health', '--version', '--help']),
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
        '--format',
        choices=['text', 'json', 'html', 'csv', 'all'],
        default='text',
        help='Output format for results (default: text)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Show configuration and validation status'
    )
    
    parser.add_argument(
        '--health',
        action='store_true',
        help='Run comprehensive health check of the installation'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create example configuration files'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='ReconAI v0.1.0'
    )
    
    args = parser.parse_args()
    
    # Print banner if available
    if banner_available and not args.verbose:
        print_banner()
        print()
    
    # Setup project structure
    setup_directories()
    
    # Validate target if utilities are available and target is provided
    if banner_available and args.target:
        target_info = validate_target(args.target)
        if not target_info['valid']:
            print(f"[ERROR] Invalid target: {args.target}")
            for warning in target_info['warnings']:
                print(f"[WARNING] {warning}")
            return 1
        
        if target_info['warnings']:
            for warning in target_info['warnings']:
                print(f"[WARNING] {warning}")
        
        print(f"[+] Target validated: {target_info['normalized']} ({target_info['type']})")
    
    # Only show target info if target is provided
    if args.target:
        print(f"[+] ReconAI v0.1.0")
        print(f"[+] Target: {args.target}")
        print(f"[+] Tool: {args.tool}")
        print(f"[+] AI Analysis: {'Enabled' if args.analyze else 'Disabled'}")
        print(f"[+] Output Directory: {args.output_dir}")
        
        if args.verbose:
            print(f"[DEBUG] Verbose mode enabled")
    
    # Import and initialize configuration and logging
    from cli.core.config import Config
    from cli.core.logging_setup import setup_logging
    from cli.core.orchestrator import ReconOrchestrator
    
    try:
        # Initialize configuration
        config = Config()
        
        # Handle config-related commands first
        if args.create_config:
            config_file = config.create_example_config()
            if config_file:
                print(f"[+] Created example configuration file: {config_file}")
                print("[!] Edit the file and copy to config.yaml to activate")
            return 0
        
        if args.health:
            from cli.utils.project_status import check_project_health, print_health_status
            health_results = check_project_health()
            print_health_status(health_results)
            return 0 if health_results['overall_status'] != 'critical' else 1
        
        if args.config:
            print("[+] Configuration Status:")
            validation = config.validate()
            
            print(f"Valid: {'✓' if validation['valid'] else '✗'}")
            print(f"OpenAI API Key: {'✓' if config.get_openai_api_key() else '✗'}")
            print(f"Output Directory: {config.get_output_dir()}")
            print(f"Log Level: {config.get_log_level()}")
            
            if validation['warnings']:
                print("\nWarnings:")
                for warning in validation['warnings']:
                    print(f"  ⚠ {warning}")
            
            if validation['errors']:
                print("\nErrors:")
                for error in validation['errors']:
                    print(f"  ✗ {error}")
            
            return 0 if validation['valid'] else 1
        
        # Setup logging with config
        setup_logging(
            log_level=config.get_log_level(),
            log_file='reconai.log' if args.verbose else None,
            verbose=args.verbose
        )
        
        # Only initialize orchestrator if we're going to run a scan
        if args.target:
            # Initialize orchestrator with config
            orchestrator = ReconOrchestrator(
                output_dir=args.output_dir,
                verbose=args.verbose,
                config=config
            )
        
        # Only run reconnaissance if target is provided
        if not args.target:
            print("[ERROR] No target specified for reconnaissance")
            print("Use --help for usage information")
            return 1
        
        # Import results formatter
        from cli.core.results_formatter import ResultsFormatter
        
        # Run reconnaissance
        results = orchestrator.run_reconnaissance(
            target=args.target,
            tool=args.tool,
            analyze=args.analyze
        )
        
        # Format and save results
        formatter = ResultsFormatter(output_dir=args.output_dir)
        
        # Generate outputs based on format selection
        output_files = []
        
        if args.format == 'all':
            # Generate all formats
            output_files.append(formatter.save_text_report(results))
            output_files.append(formatter.save_json_report(results))
            output_files.append(formatter.save_html_report(results))
            output_files.append(formatter.save_csv_summary(results))
        elif args.format == 'text':
            output_files.append(formatter.save_text_report(results))
        elif args.format == 'json':
            output_files.append(formatter.save_json_report(results))
        elif args.format == 'html':
            output_files.append(formatter.save_html_report(results))
        elif args.format == 'csv':
            output_files.append(formatter.save_csv_summary(results))
        
        # Display summary
        if args.format in ['text', 'all']:
            # Show text summary on console
            summary = formatter.format_text_report(results)
            print(summary)
        else:
            # Show brief summary for other formats
            summary = orchestrator.generate_summary_report(results)
            print(summary)
        
        # Show output files
        if output_files:
            print(f"\n[+] Results saved to:")
            for file_path in output_files:
                print(f"    📄 {file_path}")
        
        # Return appropriate exit code
        if results['success']:
            print(f"\n[+] Reconnaissance completed successfully!")
            return 0
        else:
            print(f"\n[!] Reconnaissance failed: {results.get('error', 'Unknown error')}")
            return 1
            
    except ImportError as e:
        print(f"[ERROR] Failed to import modules: {e}")
        print("[!] Make sure you're running from the project root directory")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)