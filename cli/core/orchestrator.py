"""
Core orchestrator for ReconGPT
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
        
        # Initialize tool wrappers - SIMPLE VERSION WITHOUT TIMEOUT
        self.bbot = BbotWrapper(
            output_dir=str(self.output_dir), 
            verbose=verbose
        )
        
        # Initialize AI analyzer
        try:
            ai_config = self.config.get('ai') or {}
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
    
    def run_reconnaissance(self, target: str, tool: str = "bbot", analyze: bool = False, 
                          style: str = "aggressive", generate_dorks: bool = False, 
                          max_targets: int = 50) -> Dict:
        """
        Run reconnaissance scan and optionally analyze results
        
        Args:
            target: Target to scan
            tool: Tool to use ('bbot', 'spiderfoot', 'google-dorks', 'all')
            analyze: Whether to run AI analysis
            style: Reconnaissance style
            generate_dorks: Whether to generate custom Google Dorks
            max_targets: Maximum targets for prioritization
            
        Returns:
            Dict containing all results and analysis
        """
        start_time = time.time()
        
        self.logger.info(f"Starting reconnaissance for target: {target}")
        self.logger.info(f"Tool: {tool}, Style: {style}, AI Analysis: {analyze}")
        
        # Check if AI analysis is requested but not available
        if analyze and not self.ai_analyzer:
            self.logger.warning("AI analysis requested but not available")
            analyze = False
        
        # Initialize results structure
        results = {
            'target': target,
            'tool': tool,
            'style': style,
            'timestamp': self._get_timestamp(),
            'scan_results': {},
            'ai_analysis': None,
            'dorks_generated': None,
            'execution_time': 0,
            'success': False,
            'max_targets': max_targets
        }
        
        try:
            # Generate dorks if requested (before scanning)
            if generate_dorks:
                self.logger.info("Generating custom Google Dorks...")
                dorks_result = self._generate_dorks(target, style)
                results['dorks_generated'] = dorks_result
            
            # Run the appropriate tool(s)
            if tool == "bbot":
                scan_results = self._run_bbot(target, style)
            elif tool == "spiderfoot":
                scan_results = self._run_spiderfoot(target)
            elif tool == "google-dorks":
                scan_results = self._run_google_dorks(target)
            elif tool == "all":
                scan_results = self._run_all_tools(target, style)
            else:
                raise ValueError(f"Unknown tool: {tool}")
            
            results['scan_results'] = scan_results
            
            # Run AI analysis if requested and available
            if analyze and self.ai_analyzer and scan_results.get('success'):
                self.logger.info("Running AI analysis...")
                ai_results = self._analyze_with_style(scan_results, target, style)
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
    
    def _generate_dorks(self, target: str, style: str) -> Dict:
        """Generate custom Google Dorks"""
        try:
            from tools.dork_generator import DorkGenerator
            dork_gen = DorkGenerator(config=self.config, verbose=self.verbose)
            dorks = dork_gen.generate_dorks(target, style)
            
            # Save dorks to file
            dork_gen.save_dorks(target, dorks)
            
            total_dorks = sum(len(category_dorks) for category_dorks in dorks.values())
            self.logger.info(f"Generated {total_dorks} custom dorks across {len(dorks)} categories")
            
            return {
                'success': True,
                'dorks': dorks,
                'total_count': total_dorks,
                'categories': list(dorks.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Dork generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'dorks': {},
                'total_count': 0,
                'categories': []
            }
    
    def _analyze_with_style(self, scan_results: Dict, target: str, style: str) -> Dict:
        """Run AI analysis with style-specific prompts"""
        try:
            from core.styles import ReconStyles
            styles = ReconStyles()
            
            # Get style-specific prompt
            style_prompt = styles.get_ai_prompt_style(style)
            
            # Run analysis with enhanced prompts
            ai_results = self.ai_analyzer.analyze_reconnaissance_results_with_style(
                scan_results, target, style, style_prompt
            )
            
            return ai_results
            
        except Exception as e:
            self.logger.error(f"Style-aware AI analysis failed: {e}")
            # Fallback to standard analysis
            return self.ai_analyzer.analyze_reconnaissance_results(scan_results, target)
    
    def _run_bbot(self, target: str, style: str = "aggressive") -> Dict:
        """Run Bbot scan with style-specific configuration"""
        self.logger.info(f"Running Bbot scan with {style} style...")
        
        # Apply style-specific configurations
        try:
            from core.styles import ReconStyles
            styles = ReconStyles()
            style_config = styles.get_style_config(style)
            
            # Use style-specific timeout
            timeout = style_config.get('timeout', 600)
            self.logger.debug(f"Using timeout: {timeout}s for {style} style")
            
        except Exception as e:
            self.logger.warning(f"Could not load style config: {e}")
        
        scan_results = self.bbot.run_scan(target)
        scan_results['tool'] = 'bbot'
        scan_results['style_used'] = style
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
        self.logger.info("Google Dorks tool integration not yet implemented")
        return {
            'success': False,
            'tool': 'google-dorks',
            'error': 'Google Dorks tool integration not yet implemented',
            'target': target
        }
    
    def _run_all_tools(self, target: str, style: str = "aggressive") -> Dict:
        """Run all available tools"""
        self.logger.info("Running all tools...")
        
        all_results = {
            'success': True,
            'tool': 'all',
            'target': target,
            'style_used': style,
            'results': {}
        }
        
        # Run each tool and collect results
        tools = ['bbot', 'spiderfoot', 'google-dorks']
        
        for tool_name in tools:
            try:
                if tool_name == 'bbot':
                    tool_results = self._run_bbot(target, style)
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
        style = results.get('style', 'unknown')
        filename = f"recongpt_{target_safe}_{style}_{timestamp}.json"
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
        style = results.get('style', 'unknown')
        success = results['success']
        execution_time = results.get('execution_time', 0)
        
        report = f"""
=== ReconGPT Summary Report ===
Target: {target}
Tool(s): {tool}
Style: {style}
Status: {'SUCCESS' if success else 'FAILED'}
Execution Time: {execution_time:.2f} seconds
Timestamp: {results['timestamp']}

"""
        
        # Add dorks summary if generated
        dorks_generated = results.get('dorks_generated')
        if dorks_generated and dorks_generated.get('success'):
            total_dorks = dorks_generated.get('total_count', 0)
            categories = dorks_generated.get('categories', [])
            report += f"Custom Dorks Generated: {total_dorks} across {len(categories)} categories\n"
            if categories:
                report += f"Categories: {', '.join(categories)}\n"
            report += "\n"
        
        # Add scan results summary
        scan_results = results.get('scan_results', {})
        if scan_results.get('success'):
            if tool == 'bbot':
                report += self.bbot.get_findings_summary(scan_results)
            elif tool == 'all':
                report += "Multi-tool scan results:\n"
                tool_results = scan_results.get('results', {})
                for tool_name, tool_data in tool_results.items():
                    status = "✓" if tool_data.get('success') else "✗"
                    report += f"  {status} {tool_name}: "
                    if tool_data.get('success'):
                        if tool_name == 'bbot':
                            summary = tool_data.get('results', {}).get('summary', 'No summary')
                            report += summary
                        else:
                            report += "Completed"
                    else:
                        report += tool_data.get('error', 'Failed')
                    report += "\n"
        else:
            report += f"Scan failed: {scan_results.get('error', 'Unknown error')}\n"
        
        # Add AI analysis if available
        ai_analysis = results.get('ai_analysis')
        if ai_analysis and ai_analysis.get('success'):
            report += "\n=== AI Analysis ===\n"
            if hasattr(self, 'ai_analyzer') and self.ai_analyzer:
                report += self.ai_analyzer.generate_report(ai_analysis)
        elif ai_analysis and not ai_analysis.get('success'):
            report += f"\nAI Analysis failed: {ai_analysis.get('error')}\n"
        
        report += "\n=== End of Report ===\n"
        
        return report
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")