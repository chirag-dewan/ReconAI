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
        
        self.logger.info(f"Starting Bbot scan for target: {target}")
        
        # Build Bbot command
        cmd = [
            'bbot',
            '-t', target,
            '-o', str(self.output_dir),
            '-n', scan_name,
            '--output-modules', 'json,subdomains', 
            '-f', 'subdomain-enum',
            '-y',  # Auto-confirm
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
            
            # Parse output - Bbot creates a directory with the scan name
            scan_results = self._parse_bbot_output(scan_name)
            
            return {
                'success': True,
                'target': target,
                'scan_name': scan_name,
                'results': scan_results,
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
    
    def _parse_bbot_output(self, scan_name: str) -> Dict:
        """Parse Bbot output files"""
        scan_dir = self.output_dir / scan_name
        
        # Debug: Show what files were actually created
        if self.output_dir.exists():
            all_files = list(self.output_dir.glob("*"))
            self.logger.debug(f"Files in output directory: {[f.name for f in all_files]}")
        
        if scan_dir.exists():
            scan_files = list(scan_dir.glob("*"))
            self.logger.debug(f"Files in scan directory {scan_name}: {[f.name for f in scan_files]}")
        
        # Look for JSON output in multiple possible locations
        possible_json_files = [
            scan_dir / "output.json",
            scan_dir / "output.ndjson", 
            scan_dir / f"{scan_name}.json",
            self.output_dir / f"{scan_name}.json",
            scan_dir / "events.json"
        ]
        
        # Find any JSON files
        json_files = []
        for possible_file in possible_json_files:
            if possible_file.exists():
                json_files.append(possible_file)
                break
        
        # If no specific files found, look for any JSON files
        if not json_files:
            if scan_dir.exists():
                json_files = list(scan_dir.glob("*.json")) + list(scan_dir.glob("*.ndjson"))
            if not json_files:
                json_files = list(self.output_dir.glob(f"*{scan_name}*.json"))
        
        if json_files:
            self.logger.info(f"Found JSON output: {json_files[0]}")
            return self._parse_json_file(json_files[0])
        else:
            self.logger.warning("No JSON output files found")
            
            # Try to get some basic info from text files
            possible_txt_files = [
                scan_dir / "output.txt",
                scan_dir / f"{scan_name}.txt", 
                self.output_dir / f"{scan_name}.txt"
            ]
            
            for txt_file in possible_txt_files:
                if txt_file.exists():
                    self.logger.info(f"Found text output: {txt_file}")
                    return self._parse_text_file(txt_file)
            
            return {
                'events': [],
                'total_events': 0,
                'event_types': {},
                'summary': 'No output files found, but scan completed'
            }
    
    def _parse_json_file(self, json_file: Path) -> Dict:
        """Parse Bbot JSON output file"""
        try:
            events = []
            
            # Bbot can output either regular JSON or NDJSON (newline-delimited JSON)
            with open(json_file, 'r') as f:
                content = f.read().strip()
                
                if not content:
                    self.logger.warning(f"JSON file is empty: {json_file}")
                    return {'events': [], 'total_events': 0, 'event_types': {}, 'summary': 'Empty JSON file'}
                
                # Try to parse as regular JSON first
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        events = data
                    elif isinstance(data, dict):
                        # Single event or wrapped format
                        events = [data] if 'type' in data else data.get('events', [data])
                except json.JSONDecodeError:
                    # Try parsing as NDJSON (line by line)
                    for line in content.split('\n'):
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
            valid_events = []
            
            for event in events:
                if isinstance(event, dict):
                    event_type = event.get('type', 'unknown')
                    event_types[event_type] = event_types.get(event_type, 0) + 1
                    valid_events.append(event)
            
            return {
                'events': valid_events,
                'total_events': len(valid_events),
                'event_types': event_types,
                'summary': f"Found {len(valid_events)} total events across {len(event_types)} different types"
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON output: {e}")
            return {
                'events': [],
                'total_events': 0,
                'event_types': {},
                'error': f"Failed to parse JSON output: {str(e)}"
            }
    
    def _parse_text_file(self, txt_file: Path) -> Dict:
        """Parse Bbot text output as fallback"""
        try:
            with open(txt_file, 'r') as f:
                content = f.read()
            
            # Simple parsing - count lines that look like findings
            lines = content.split('\n')
            findings = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('[') and not line.startswith('#'):
                    # This looks like a finding
                    findings.append({'type': 'text_finding', 'data': line})
            
            return {
                'events': findings,
                'total_events': len(findings),
                'event_types': {'text_finding': len(findings)},
                'summary': f"Parsed {len(findings)} findings from text output"
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing text output: {e}")
            return {
                'events': [],
                'total_events': 0,
                'event_types': {},
                'summary': 'Failed to parse text output'
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