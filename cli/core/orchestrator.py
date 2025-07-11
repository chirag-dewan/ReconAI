"""
Core orchestrator for ReconAI
Manages tool execution and workflow coordination
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

# Import our custom modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools.bbot_wrapper import BbotWrapper
from ai.analyzer import AIAnalyzer
from core.config import Config
from core.logging_setup import StatusLogger, ProgressLogger

class ReconOrchestrator:
    def __init__(self, output_dir: str = None, verbose: bool = False, config: Config = None):
        # Initialize configuration
        self.config = config or Config()
        
        # Use config for output directory if not specified
        self.output_dir = Path(output_dir or self.config.get_output_dir())
        self.verbose = verbose
        
        # Setup loggers
        self.logger = StatusLogger('orchestrator')
        self.progress = ProgressLogger('orchestrator', 10)  # Default 10 steps
        
        # Initialize tool wrappers with config
        bbot_config = self.config.get_tool_config('bbot')
        self.bbot = BbotWrapper(
            output_dir=str(self.output_dir), 
            verbose=verbose,
            timeout=bbot_config.get('timeout', 300)
        )
        
        # Initialize AI analyzer with config
        try:
            ai_config = self.config.get('ai', {})
            self.ai_analyzer = AIAnalyzer(
                api_key=self.config.get_openai_api_key(),
                model=ai_config.get('model', 'gpt-4'),
                verbose=verbose
            )
        except ValueError as e:
            self.logger.warning(f"AI analyzer not available: {e}")
            self.ai_analyzer = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Log initialization
        self.logger.info(f"Orchestrator initialized with output dir: {self.output_dir}")
        if self.ai_analyzer:
            self.logger.info("AI analysis enabled")
        else:
            self.logger.warning("AI analysis disabled")
    
    def run_reconnaissance(self, target: str, tool: str = "bbot", analyze: bool = False) -> Dict:
        """
        Run reconnaissance scan and optionally analyze results
        
        Args:
            target: Target to scan
            tool: Tool to use ('bbot', 'spiderfoot', 'google-dorks', 'all')
            analyze: Whether to run AI analysis
            
        Returns:
            Dict containing all results and analysis
        """
        start_time = time.time()
        
        self.logger.info(f"Starting reconnaissance for target: {target}")
        self.logger.info(f"Tool: {tool}, AI Analysis: {analyze}")
        
        # Check if AI analysis is requested but not available
        if analyze and not self.ai_analyzer:
            self.logger.warning("AI analysis requested but not available")
            analyze = False
        
        # Check if tool is enabled
        if tool != "all" and not self.config.is_tool_enabled(tool):
            self.logger.warning(f"Tool {tool} is disabled in configuration")
        
        # Setup progress tracking
        total_steps = 1  # Scanning
        if analyze:
            total_steps += 1  # AI analysis
        self.progress = ProgressLogger('orchestrator', total_steps)
        
        # Initialize results structure
        results = {
            'target': target,
            'tool': tool,
            'timestamp': self._get_timestamp(),
            'scan_results': {},
            'ai_analysis': None,
            'execution_time': 0,
            'success': False,
            'config_used': {
                'ai_model': self.config.get('ai', 'model', 'N/A'),
                'tool_configs': self.config.get('tools', {})
            }
        }
        
        try:
            # Run the appropriate tool(s)
            if tool == "bbot":
                scan_results = self._run_bbot(target)
            elif tool == "spiderfoot":
                scan_results = self._run_spiderfoot(target)
            elif tool == "google-dorks":
                scan_results = self._run_google_dorks(target)
            elif tool == "all":
                scan_results = self._run_all_tools(target)
            else:
                raise ValueError(f"Unknown tool: {tool}")
            
            results['scan_results'] = scan_results
            
            # Run AI analysis if requested and available
            if analyze and self.ai_analyzer and scan_results.get('success'):
                self.logger.info("Running AI analysis...")
                ai_results = self.ai_analyzer.analyze_reconnaissance_results(
                    scan_results, target
                )
                results['ai_analysis'] = ai_results
            elif analyze and not self.ai_analyzer:
                self.logger.warning("AI analysis requested but not available (missing API key)")
            
            # Calculate execution time
            execution_time = time.time() - start_time
            results['execution_time'] = execution_time
            
            # Mark as successful if scan succeeded
            results['success'] = scan_results.get('success', False)
            
            # Save results to file
            self._save_results(results)
            
            self.logger.info(f"Reconnaissance completed in {execution_time:.2f} seconds")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Reconnaissance failed: {e}")
            results['error'] = str(e)
            results['execution_time'] = time.time() - start_time
            return results
    
    def _run_bbot(self, target: str) -> Dict:
        """Run Bbot scan"""
        self.logger.info("Running Bbot scan...")
        scan_results = self.bbot.run_scan(target)
        scan_results['tool'] = 'bbot'
        return scan_results
    
    def _run_spiderfoot(self, target: str) -> Dict:
        """Run Spiderfoot scan (placeholder)"""
        self.logger.info("Spiderfoot integration not yet implemented")
        return {
            'success': False,
            'tool': 'spiderfoot',
            'error': 'Spiderfoot integration not yet implemented',
            'target': target
        }
    
    def _run_google_dorks(self, target: str) -> Dict:
        """Run Google Dorks search (placeholder)"""
        self.logger.info("Google Dorks integration not yet implemented")
        return {
            'success': False,
            'tool': 'google-dorks',
            'error': 'Google Dorks integration not yet implemented',
            'target': target
        }
    
    def _run_all_tools(self, target: str) -> Dict:
        """Run all available tools"""
        self.logger.info("Running all tools...")
        
        all_results = {
            'success': True,
            'tool': 'all',
            'target': target,
            'results': {}
        }
        
        # Run each tool and collect results
        tools = ['bbot', 'spiderfoot', 'google-dorks']
        
        for tool_name in tools:
            try:
                if tool_name == 'bbot':
                    tool_results = self._run_bbot(target)
                elif tool_name == 'spiderfoot':
                    tool_results = self._run_spiderfoot(target)
                elif tool_name == 'google-dorks':
                    tool_results = self._run_google_dorks(target)
                
                all_results['results'][tool_name] = tool_results
                
                # If any tool fails, mark overall as partial success
                if not tool_results.get('success'):
                    all_results['success'] = 'partial'
                    
            except Exception as e:
                self.logger.error(f"Tool {tool_name} failed: {e}")
                all_results['results'][tool_name] = {
                    'success': False,
                    'tool': tool_name,
                    'error': str(e),
                    'target': target
                }
                all_results['success'] = 'partial'
        
        return all_results
    
    def _save_results(self, results: Dict) -> str:
        """Save results to JSON file"""
        timestamp = results['timestamp'].replace(':', '-').replace(' ', '_')
        target_safe = results['target'].replace('/', '_').replace(':', '_')
        filename = f"recon_{target_safe}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.logger.info(f"Results saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            return ""
    
    def generate_summary_report(self, results: Dict) -> str:
        """Generate a human-readable summary report"""
        target = results['target']
        tool = results['tool']
        success = results['success']
        execution_time = results.get('execution_time', 0)
        
        report = f"""
=== ReconAI Summary Report ===
Target: {target}
Tool(s): {tool}
Status: {'SUCCESS' if success else 'FAILED'}
Execution Time: {execution_time:.2f} seconds
Timestamp: {results['timestamp']}

"""
        
        # Add scan results summary
        scan_results = results.get('scan_results', {})
        if scan_results.get('success'):
            if tool == 'bbot':
                report += self.bbot.get_findings_summary(scan_results)
            elif tool == 'all':
                report += "Multi-tool scan results:\n"
                for tool_name, tool_results in scan_results.get('results', {}).items():
                    status = "✓" if tool_results.get('success') else "✗"
                    report += f"  {status} {tool_name}: "
                    if tool_results.get('success'):
                        if tool_name == 'bbot':
                            summary = tool_results.get('results', {}).get('summary', 'No summary')
                            report += summary
                        else:
                            report += "Completed"
                    else:
                        report += tool_results.get('error', 'Failed')
                    report += "\n"
        else:
            report += f"Scan failed: {scan_results.get('error', 'Unknown error')}\n"
        
        # Add AI analysis if available
        ai_analysis = results.get('ai_analysis')
        if ai_analysis and ai_analysis.get('success'):
            report += "\n=== AI Analysis ===\n"
            report += self.ai_analyzer.generate_report(ai_analysis)
        elif ai_analysis and not ai_analysis.get('success'):
            report += f"\nAI Analysis failed: {ai_analysis.get('error')}\n"
        
        report += "\n=== End of Report ===\n"
        
        return report
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")