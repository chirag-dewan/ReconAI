"""
AI Analysis module for ReconGPT
Handles GPT-4 integration for analyzing reconnaissance results
"""

import json
import os
from typing import Dict, List, Optional
import logging
from openai import OpenAI

class AIAnalyzer:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", verbose: bool = False):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.verbose = verbose
        self.logger = self._setup_logger()
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the AI analyzer"""
        logger = logging.getLogger('ai_analyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(levelname)s] %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        return logger
    
    def analyze_reconnaissance_results(self, scan_results: Dict, target: str) -> Dict:
        """
        Analyze reconnaissance results using GPT-4
        
        Args:
            scan_results: Results from reconnaissance tools
            target: Original target that was scanned
            
        Returns:
            Dict containing AI analysis and recommendations
        """
        self.logger.info(f"Starting AI analysis for target: {target}")
        
        try:
            # Prepare the prompt with scan results
            prompt = self._build_analysis_prompt(scan_results, target)
            
            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the structured response
            analysis = self._parse_ai_response(analysis_text)
            
            self.logger.info("AI analysis completed successfully")
            
            return {
                'success': True,
                'target': target,
                'analysis': analysis,
                'model_used': self.model,
                'raw_response': analysis_text
            }
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return {
                'success': False,
                'target': target,
                'error': str(e)
            }
    
    def analyze_reconnaissance_results_with_style(self, scan_results: Dict, target: str, 
                                                 style: str, style_prompt: str) -> Dict:
        """
        Analyze reconnaissance results with style-specific prompts
        
        Args:
            scan_results: Results from reconnaissance tools
            target: Original target that was scanned
            style: Reconnaissance style used
            style_prompt: Style-specific analysis prompt
            
        Returns:
            Dict containing AI analysis and recommendations
        """
        self.logger.info(f"Starting style-aware AI analysis for target: {target} (style: {style})")
        
        try:
            # Prepare the prompt with scan results
            prompt = self._build_analysis_prompt(scan_results, target, style)
            
            # Combine system prompt with style-specific instructions
            system_prompt = self._get_system_prompt() + "\n\n" + style_prompt
            
            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the structured response
            analysis = self._parse_ai_response(analysis_text)
            
            self.logger.info(f"Style-aware AI analysis completed successfully for {style} style")
            
            return {
                'success': True,
                'target': target,
                'style': style,
                'analysis': analysis,
                'model_used': self.model,
                'raw_response': analysis_text
            }
            
        except Exception as e:
            self.logger.error(f"Style-aware AI analysis failed: {e}")
            # Fallback to standard analysis
            return self.analyze_reconnaissance_results(scan_results, target)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI analysis"""
        return """You are an expert cybersecurity analyst specializing in reconnaissance data analysis. Your job is to:

1. SUMMARIZE the key findings in a clear, concise manner
2. PRIORITIZE findings by risk level (Critical, High, Medium, Low)
3. IDENTIFY potential attack vectors and security concerns
4. PROVIDE actionable recommendations for both attackers (red team) and defenders (blue team)
5. HIGHLIGHT any particularly interesting or unusual findings
6. ASSESS the overall security posture based on the reconnaissance data

Structure your response as follows:
- Executive Summary (2-3 sentences)
- Key Findings (categorized by importance)
- Risk Assessment
- Attack Vectors
- Recommendations
- Notable Discoveries

Be practical, specific, and focus on actionable intelligence. Assume the user is conducting authorized security testing."""
    
    def _build_analysis_prompt(self, scan_results: Dict, target: str, style: str = None) -> str:
        """Build the analysis prompt with scan data"""
        prompt = f"""Please analyze the following reconnaissance scan results for target: {target}

SCAN TOOL: {scan_results.get('tool', 'Unknown')}
SCAN STATUS: {'SUCCESS' if scan_results.get('success') else 'FAILED'}
"""
        
        if style:
            prompt += f"RECONNAISSANCE STYLE: {style}\n"
        
        prompt += "\n"
        
        if not scan_results.get('success'):
            prompt += f"SCAN ERROR: {scan_results.get('error', 'Unknown error')}\n"
            prompt += "Please provide guidance on troubleshooting and alternative reconnaissance approaches."
            return prompt
        
        # Add results summary
        results = scan_results.get('results', {})
        if 'summary' in results:
            prompt += f"SUMMARY: {results['summary']}\n\n"
        
        # Add event types if available (from Bbot)
        if 'event_types' in results:
            prompt += "EVENT TYPES DISCOVERED:\n"
            for event_type, count in results['event_types'].items():
                prompt += f"- {event_type}: {count}\n"
            prompt += "\n"
        
        # Add sample events for context
        events = results.get('events', [])
        if events:
            prompt += "SAMPLE FINDINGS (first 15 events):\n"
            for i, event in enumerate(events[:15]):
                event_summary = self._summarize_event(event)
                prompt += f"{i+1}. {event_summary}\n"
            
            if len(events) > 15:
                prompt += f"... and {len(events) - 15} more events\n"
        
        # Add style-specific context
        if style:
            style_context = {
                'stealth': "Focus on low-profile attack vectors and passive exploitation opportunities.",
                'aggressive': "Provide comprehensive analysis including all potential attack vectors.",
                'phishing': "Emphasize social engineering opportunities and human-targeted attacks.",
                'quick': "Provide rapid assessment focusing on immediate and obvious security issues."
            }
            
            context = style_context.get(style, "")
            if context:
                prompt += f"\nSTYLE CONTEXT: {context}\n"
        
        prompt += "\nPlease provide your analysis focusing on security implications and actionable recommendations."
        
        return prompt
    
    def _summarize_event(self, event: Dict) -> str:
        """Create a brief summary of a single event"""
        event_type = event.get('type', 'unknown')
        data = event.get('data', '')
        
        if event_type == 'DNS_NAME':
            return f"DNS Name: {data}"
        elif event_type == 'URL':
            return f"URL: {data}"
        elif event_type == 'IP_ADDRESS':
            return f"IP Address: {data}"
        elif event_type == 'OPEN_TCP_PORT':
            return f"Open Port: {data}"
        elif event_type == 'TECHNOLOGY':
            return f"Technology: {data}"
        elif event_type == 'EMAIL_ADDRESS':
            return f"Email: {data}"
        elif event_type == 'SOCIAL':
            return f"Social Media: {data}"
        else:
            return f"{event_type}: {str(data)[:50]}{'...' if len(str(data)) > 50 else ''}"
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse the AI response into structured data"""
        lines = response_text.split('\n')
        sections = {}
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            if any(keyword in line.lower() for keyword in ['summary', 'findings', 'risk', 'attack', 'recommendations', 'notable', 'assessment']):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        # Extract priorities and risk levels
        priorities = self._extract_priorities(response_text)
        
        return {
            'raw_text': response_text,
            'sections': sections,
            'priorities': priorities,
            'total_lines': len(lines)
        }
    
    def _extract_priorities(self, text: str) -> Dict:
        """Extract priority information from analysis text"""
        priorities = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Simple extraction based on keywords
        lines = text.split('\n')
        current_priority = None
        
        for line in lines:
            line = line.strip().lower()
            
            if 'critical' in line and ('priority' in line or 'risk' in line):
                current_priority = 'critical'
            elif 'high' in line and ('priority' in line or 'risk' in line):
                current_priority = 'high'
            elif 'medium' in line and ('priority' in line or 'risk' in line):
                current_priority = 'medium'
            elif 'low' in line and ('priority' in line or 'risk' in line):
                current_priority = 'low'
            elif line.startswith('- ') and current_priority:
                priorities[current_priority].append(line[2:])
        
        return priorities
    
    def generate_report(self, analysis_result: Dict) -> str:
        """Generate a formatted report from analysis results"""
        if not analysis_result.get('success'):
            return f"AI Analysis Failed: {analysis_result.get('error', 'Unknown error')}"
        
        target = analysis_result['target']
        analysis = analysis_result['analysis']
        model = analysis_result['model_used']
        style = analysis_result.get('style', 'Standard')
        
        report = f"""
=== ReconGPT AI Analysis Report ===
Target: {target}
Style: {style}
Model: {model}
Generated: {self._get_timestamp()}

{analysis['raw_text']}

--- End of AI Analysis ---
"""
        return report
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")