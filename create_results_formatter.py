#!/usr/bin/env python3
"""
Quick script to create the missing results_formatter.py file
"""

results_formatter_content = '''"""
Results formatting for ReconAI
Handles output formatting in various formats (text, JSON, HTML, etc.)
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import html

class ResultsFormatter:
    """Format reconnaissance results in various output formats"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def format_text_report(self, results: Dict) -> str:
        """Format results as a detailed text report"""
        target = results.get('target', 'Unknown')
        tool = results.get('tool', 'Unknown')
        timestamp = results.get('timestamp', 'Unknown')
        success = results.get('success', False)
        execution_time = results.get('execution_time', 0)
        
        report = []
        report.append("=" * 70)
        report.append("RECONAI RECONNAISSANCE REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Header information
        report.append(f"Target:          {target}")
        report.append(f"Tool(s):         {tool}")
        report.append(f"Status:          {'SUCCESS' if success else 'FAILED'}")
        report.append(f"Execution Time:  {execution_time:.2f} seconds")
        report.append(f"Generated:       {timestamp}")
        report.append("")
        
        # Scan results section
        scan_results = results.get('scan_results', {})
        if scan_results and scan_results.get('success'):
            report.append("-" * 50)
            report.append("SCAN RESULTS")
            report.append("-" * 50)
            
            if tool == 'bbot':
                bbot_results = scan_results.get('results', {})
                total_events = bbot_results.get('total_events', 0)
                event_types = bbot_results.get('event_types', {})
                
                report.append(f"Total Events Found: {total_events}")
                report.append("")
                
                if event_types:
                    report.append("Event Types:")
                    sorted_types = sorted(event_types.items(), key=lambda x: x[1], reverse=True)
                    for event_type, count in sorted_types:
                        report.append(f"  {event_type:<20} : {count:>5}")
                    report.append("")
        
        # AI analysis section
        ai_analysis = results.get('ai_analysis')
        if ai_analysis and ai_analysis.get('success'):
            report.append("-" * 50)
            report.append("AI ANALYSIS")
            report.append("-" * 50)
            
            analysis = ai_analysis.get('analysis', {})
            raw_text = analysis.get('raw_text', '')
            if raw_text:
                report.append(raw_text)
            report.append("")
        
        report.append("=" * 70)
        report.append("END OF REPORT")
        report.append("=" * 70)
        
        return '\\n'.join(report)
    
    def save_text_report(self, results: Dict, filename: Optional[str] = None) -> str:
        """Save results as text report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_safe = self._sanitize_filename(results.get('target', 'unknown'))
            filename = f"report_{target_safe}_{timestamp}.txt"
        
        report_text = self.format_text_report(results)
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(report_text)
        
        return str(filepath)
    
    def save_json_report(self, results: Dict, filename: Optional[str] = None) -> str:
        """Save results as JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_safe = self._sanitize_filename(results.get('target', 'unknown'))
            filename = f"recon_{target_safe}_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return str(filepath)
    
    def save_html_report(self, results: Dict, filename: Optional[str] = None) -> str:
        """Save results as HTML report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_safe = self._sanitize_filename(results.get('target', 'unknown'))
            filename = f"report_{target_safe}_{timestamp}.html"
        
        html_content = self.generate_html_report(results)
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def save_csv_summary(self, results: Dict, filename: Optional[str] = None) -> str:
        """Save a CSV summary of findings"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_safe = self._sanitize_filename(results.get('target', 'unknown'))
            filename = f"summary_{target_safe}_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        # Simple CSV for now
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Target', 'Tool', 'Status', 'Timestamp'])
            writer.writerow([
                results.get('target', ''),
                results.get('tool', ''),
                'SUCCESS' if results.get('success') else 'FAILED',
                results.get('timestamp', '')
            ])
        
        return str(filepath)
    
    def generate_html_report(self, results: Dict) -> str:
        """Generate a basic HTML report"""
        target = html.escape(results.get('target', 'Unknown'))
        tool = html.escape(results.get('tool', 'Unknown'))
        timestamp = html.escape(results.get('timestamp', 'Unknown'))
        success = results.get('success', False)
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ReconAI Report - {target}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ border-bottom: 2px solid #333; padding-bottom: 20px; }}
        .status-success {{ color: green; }}
        .status-failed {{ color: red; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 ReconAI Report</h1>
        <p>Target: {target}</p>
        <p>Tool: {tool}</p>
        <p>Status: <span class="{'status-success' if success else 'status-failed'}">
            {'SUCCESS' if success else 'FAILED'}
        </span></p>
        <p>Generated: {timestamp}</p>
    </div>
    
    <h2>Scan Results</h2>
    <p>Detailed results would appear here...</p>
    
</body>
</html>
        """
        return html_content
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem safety"""
        import re
        filename = re.sub(r'[<>:"/\\\\|?*]', '_', filename)
        filename = re.sub(r'[^\\w\\-_\\.]', '_', filename)
        return filename[:50]
'''

# Write the content to the file
with open('cli/core/results_formatter.py', 'w') as f:
    f.write(results_formatter_content)

print("✅ Created cli/core/results_formatter.py")