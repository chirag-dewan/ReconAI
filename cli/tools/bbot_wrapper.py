"""
Bbot tool wrapper for ReconAI
Handles Bbot execution and output parsing
"""

import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

class BbotWrapper:
    def __init__(self, output_dir: str = "output", verbose: bool = False):
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.logger = self._setup_logger()
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the Bbot wrapper"""
        logger = logging.getLogger('bbot_wrapper')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(levelname)s] %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        return logger
    
    def check_installation(self) -> bool:
        """Check if Bbot is installed and accessible"""
        try:
            result = subprocess.run(
                ['bbot', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info(f"Bbot found: {result.stdout.strip()}")
                return True
            else:
                self.logger.error("Bbot not found or not working")
                return False
        except subprocess.TimeoutExpired:
            self.logger.error("Bbot version check timed out")
            return False
        except FileNotFoundError:
            self.logger.error("Bbot not found in PATH")
            return False
        except Exception as e:
            self.logger.error(f"Error checking Bbot installation: {e}")
            return False
    
    def run_scan(self, target: str, scan_name: Optional[str] = None) -> Dict:
        """
        Run Bbot scan on target
        
        Args:
            target: Target to scan (domain, IP, etc.)
            scan_name: Optional custom scan name
            
        Returns:
            Dict with scan results and metadata
        """
        if not self.check_installation():
            raise RuntimeError("Bbot is not installed or not accessible")
        
        # Generate scan name if not provided
        if not scan_name:
            scan_name = f"bbot_scan_{target.replace('/', '_').replace(':', '_')}"
        
        # Output file paths
        json_output = self.output_dir / f"{scan_name}.json"
        txt_output = self.output_dir / f"{scan_name}.txt"
        
        self.logger.info(f"Starting Bbot scan for target: {target}")
        
        # Build Bbot command
        cmd = [
            'bbot',
            '-t', target,
            '-o', str(self.output_dir),
            '-n', scan_name,
            '--output-modules', 'json,human',
            '-f', 'subdomain-enum',  # Default flag set
        ]
        
        if self.verbose:
            cmd.append('-v')
        
        self.logger.debug(f"Running command: {' '.join(cmd)}")
        
        try:
            # Run Bbot
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                self.logger.error(f"Bbot scan failed: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'target': target,
                    'scan_name': scan_name
                }
            
            self.logger.info("Bbot scan completed successfully")
            
            # Parse JSON output
            scan_results = self._parse_json_output(json_output)
            
            return {
                'success': True,
                'target': target,
                'scan_name': scan_name,
                'results': scan_results,
                'output_files': {
                    'json': str(json_output),
                    'txt': str(txt_output)
                },
                'command': ' '.join(cmd)
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error("Bbot scan timed out")
            return {
                'success': False,
                'error': 'Scan timed out after 5 minutes',
                'target': target,
                'scan_name': scan_name
            }
        except Exception as e:
            self.logger.error(f"Error running Bbot scan: {e}")
            return {
                'success': False,
                'error': str(e),
                'target': target,
                'scan_name': scan_name
            }
    
    def _parse_json_output(self, json_file: Path) -> Dict:
        """Parse Bbot JSON output file"""
        if not json_file.exists():
            self.logger.warning(f"JSON output file not found: {json_file}")
            return {'events': [], 'summary': 'JSON output file not found'}
        
        try:
            events = []
            with open(json_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            event = json.loads(line)
                            events.append(event)
                        except json.JSONDecodeError:
                            continue
            
            self.logger.info(f"Parsed {len(events)} events from Bbot output")
            
            # Create summary
            event_types = {}
            for event in events:
                event_type = event.get('type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            return {
                'events': events,
                'total_events': len(events),
                'event_types': event_types,
                'summary': f"Found {len(events)} total events across {len(event_types)} different types"
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON output: {e}")
            return {
                'events': [],
                'error': f"Failed to parse JSON output: {str(e)}"
            }
    
    def get_findings_summary(self, scan_results: Dict) -> str:
        """Generate a human-readable summary of findings"""
        if not scan_results.get('success'):
            return f"Scan failed: {scan_results.get('error', 'Unknown error')}"
        
        results = scan_results.get('results', {})
        total_events = results.get('total_events', 0)
        event_types = results.get('event_types', {})
        
        summary = f"Bbot Scan Results for {scan_results['target']}:\n"
        summary += f"Total Events: {total_events}\n\n"
        
        if event_types:
            summary += "Event Types:\n"
            for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
                summary += f"  - {event_type}: {count}\n"
        
        return summary