"""
Reconnaissance styles for ReconGPT
Defines different scanning approaches and AI analysis strategies
"""

from typing import Dict, Any

class ReconStyles:
    """Manages different reconnaissance styles and their configurations"""
    
    def __init__(self):
        self.styles = {
            'stealth': {
                'description': 'Passive-only reconnaissance with minimal footprint',
                'tools': ['bbot'],
                'bbot_flags': ['subdomain-enum', 'dns-enum'],
                'aggressive_modules': False,
                'auto_analyze': True,
                'include_dorks': False,
                'timeout': 300,
                'ai_focus': 'stealth_analysis',
                'priority_factors': ['exposure_risk', 'stealth_friendly'],
                'scan_intensity': 'low'
            },
            
            'aggressive': {
                'description': 'Comprehensive deep scanning with all available modules',
                'tools': ['bbot', 'spiderfoot'],
                'bbot_flags': ['subdomain-enum', 'dns-enum', 'port-scan', 'web-enum', 'email-enum'],
                'aggressive_modules': True,
                'auto_analyze': True,
                'include_dorks': True,
                'timeout': 900,
                'ai_focus': 'comprehensive_analysis',
                'priority_factors': ['vulnerability_potential', 'attack_surface', 'asset_value'],
                'scan_intensity': 'high'
            },
            
            'phishing': {
                'description': 'Focused on email addresses, social media, and employee information',
                'tools': ['bbot', 'spiderfoot'],
                'bbot_flags': ['email-enum', 'social-enum', 'employee-enum'],
                'aggressive_modules': False,
                'auto_analyze': True,
                'include_dorks': True,
                'timeout': 600,
                'ai_focus': 'social_engineering',
                'priority_factors': ['employee_exposure', 'social_presence', 'email_security'],
                'scan_intensity': 'medium',
                'special_dorks': ['email_harvesting', 'social_media', 'employee_info']
            },
            
            'quick': {
                'description': 'Fast overview scan for initial assessment',
                'tools': ['bbot'],
                'bbot_flags': ['subdomain-enum'],
                'aggressive_modules': False,
                'auto_analyze': True,
                'include_dorks': False,
                'timeout': 180,
                'ai_focus': 'quick_assessment',
                'priority_factors': ['immediate_threats', 'obvious_vulnerabilities'],
                'scan_intensity': 'low'
            }
        }
    
    def get_style_config(self, style_name: str) -> Dict[str, Any]:
        """Get configuration for a specific reconnaissance style"""
        if style_name not in self.styles:
            raise ValueError(f"Unknown reconnaissance style: {style_name}")
        
        return self.styles[style_name].copy()
    
    def list_styles(self):
        """Display all available reconnaissance styles"""
        print("🎯 Available Reconnaissance Styles:")
        print("=" * 60)
        
        for style_name, config in self.styles.items():
            intensity_emoji = {
                'low': '🟢',
                'medium': '🟡', 
                'high': '🔴'
            }.get(config.get('scan_intensity', 'medium'), '⚪')
            
            print(f"\n{intensity_emoji} {style_name.upper()}")
            print(f"   Description: {config['description']}")
            print(f"   Tools: {', '.join(config['tools'])}")
            print(f"   Intensity: {config.get('scan_intensity', 'medium')}")
            print(f"   Timeout: {config['timeout']}s")
            print(f"   Auto-analyze: {'Yes' if config['auto_analyze'] else 'No'}")
            print(f"   Include Dorks: {'Yes' if config['include_dorks'] else 'No'}")
            
            if config.get('special_dorks'):
                print(f"   Special Dorks: {', '.join(config['special_dorks'])}")
        
        print(f"\n{'='*60}")
        print("Usage: python main.py -t target.com --style [style_name]")
    
    def get_ai_prompt_style(self, style_name: str) -> str:
        """Get AI analysis prompt style for the reconnaissance type"""
        style_config = self.get_style_config(style_name)
        ai_focus = style_config.get('ai_focus', 'general_analysis')
        
        prompts = {
            'stealth_analysis': """
            Analyze this reconnaissance data with a focus on STEALTH and LOW-PROFILE operations.
            Prioritize:
            - Targets with minimal monitoring/logging
            - Passive exploitation opportunities
            - Information that can be gathered without direct interaction
            - Services that are less likely to trigger alerts
            
            Avoid recommending:
            - Active scanning or probing
            - High-noise attack vectors
            - Anything that might trigger security alerts
            """,
            
            'comprehensive_analysis': """
            Perform a COMPREHENSIVE SECURITY ANALYSIS of this reconnaissance data.
            Evaluate all aspects including:
            - Complete attack surface analysis
            - All potential vulnerability vectors
            - Asset value and criticality assessment
            - Risk prioritization across all findings
            - Both passive and active exploitation opportunities
            
            Provide detailed technical analysis and full range of recommendations.
            """,
            
            'social_engineering': """
            Analyze this data with a focus on SOCIAL ENGINEERING and HUMAN-TARGETED attacks.
            Prioritize:
            - Employee information and contact details
            - Social media presence and patterns
            - Email security and phishing opportunities
            - Organizational structure and key personnel
            - Communication platforms and channels
            
            Focus on human-centric attack vectors and social manipulation opportunities.
            """,
            
            'quick_assessment': """
            Provide a RAPID SECURITY ASSESSMENT of this reconnaissance data.
            Focus on:
            - Most critical and immediate security risks
            - Quick wins and obvious vulnerabilities
            - High-impact, low-effort attack vectors
            - Essential security posture overview
            
            Keep analysis concise but actionable. Highlight only the most important findings.
            """
        }
        
        return prompts.get(ai_focus, prompts['comprehensive_analysis'])
    
    def get_priority_factors(self, style_name: str) -> list:
        """Get priority factors for target ranking based on style"""
        style_config = self.get_style_config(style_name)
        return style_config.get('priority_factors', ['vulnerability_potential', 'attack_surface'])
    
    def should_include_module(self, style_name: str, module_name: str) -> bool:
        """Check if a specific module should be included for this style"""
        style_config = self.get_style_config(style_name)
        
        # Check if aggressive modules are enabled
        if not style_config.get('aggressive_modules', True):
            aggressive_modules = ['port-scan', 'web-enum', 'vuln-scan', 'brute-force']
            if module_name in aggressive_modules:
                return False
        
        # Check style-specific module inclusions
        bbot_flags = style_config.get('bbot_flags', [])
        return module_name in bbot_flags
    
    def get_timeout(self, style_name: str) -> int:
        """Get timeout value for the style"""
        style_config = self.get_style_config(style_name)
        return style_config.get('timeout', 600)
    
    def validate_style(self, style_name: str) -> bool:
        """Validate if a style name is valid"""
        return style_name in self.styles