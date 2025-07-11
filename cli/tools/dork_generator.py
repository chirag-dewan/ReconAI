"""
AI-powered Google Dork generator for ReconGPT
Creates custom search queries tailored to specific targets
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

class DorkGenerator:
    """Generates custom Google Dorks using AI for targeted reconnaissance"""
    
    def __init__(self, config=None, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.logger = self._setup_logger()
        self.output_dir = Path("output/dorks")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize AI client if available
        try:
            from openai import OpenAI
            api_key = config.get_openai_api_key() if config else os.getenv('OPENAI_API_KEY')
            if api_key:
                self.ai_client = OpenAI(api_key=api_key)
                self.ai_available = True
            else:
                self.ai_client = None
                self.ai_available = False
                self.logger.warning("OpenAI API key not available - using predefined dorks")
        except ImportError:
            self.ai_client = None
            self.ai_available = False
            self.logger.warning("OpenAI not installed - using predefined dorks")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the dork generator"""
        logger = logging.getLogger('dork_generator')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        return logger
    
    def generate_dorks(self, target: str, style: str = 'aggressive', categories: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Generate custom Google Dorks for a target
        
        Args:
            target: Target domain/organization
            style: Reconnaissance style (affects dork generation)
            categories: Specific dork categories to generate
            
        Returns:
            Dict of categorized Google Dorks
        """
        self.logger.info(f"Generating custom Google Dorks for: {target}")
        
        if self.ai_available:
            return self._generate_ai_dorks(target, style, categories)
        else:
            return self._generate_template_dorks(target, categories)
    
    def _generate_ai_dorks(self, target: str, style: str, categories: Optional[List[str]]) -> Dict[str, List[str]]:
        """Generate dorks using AI"""
        try:
            prompt = self._build_dork_prompt(target, style, categories)
            
            response = self.ai_client.chat.completions.create(
                model=self.config.get('ai', 'model', 'gpt-4') if self.config else 'gpt-4',
                messages=[
                    {
                        "role": "system",
                        "content": self._get_dork_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content
            parsed_dorks = self._parse_ai_dork_response(ai_response)
            
            # Combine AI-generated with template dorks
            template_dorks = self._generate_template_dorks(target, categories)
            
            # Merge the two sets
            combined_dorks = {}
            for category in set(list(parsed_dorks.keys()) + list(template_dorks.keys())):
                combined_dorks[category] = []
                if category in parsed_dorks:
                    combined_dorks[category].extend(parsed_dorks[category])
                if category in template_dorks:
                    combined_dorks[category].extend(template_dorks[category])
                # Remove duplicates
                combined_dorks[category] = list(set(combined_dorks[category]))
            
            self.logger.info(f"Generated {sum(len(dorks) for dorks in combined_dorks.values())} custom dorks")
            return combined_dorks
            
        except Exception as e:
            self.logger.error(f"AI dork generation failed: {e}")
            return self._generate_template_dorks(target, categories)
    
    def _get_dork_system_prompt(self) -> str:
        """Get system prompt for Google Dork generation"""
        return """You are an expert in Google Dorking and OSINT reconnaissance. Your job is to generate highly effective, targeted Google search queries (dorks) for cybersecurity reconnaissance.

Generate Google Dorks that are:
1. Specific to the target domain/organization
2. Designed to find sensitive information, misconfigurations, and security issues
3. Categorized by purpose (admin portals, sensitive files, etc.)
4. Practical and likely to yield results
5. Compliant with responsible disclosure practices

Focus on finding:
- Admin panels and login pages
- Exposed sensitive files (logs, configs, backups)
- Directory listings and file indexes
- Technology stack indicators
- Potential security misconfigurations
- Publicly accessible databases or APIs

Format your response as JSON with categories as keys and arrays of dorks as values."""
    
    def _build_dork_prompt(self, target: str, style: str, categories: Optional[List[str]]) -> str:
        """Build the AI prompt for dork generation"""
        prompt = f"""Generate targeted Google Dorks for reconnaissance of: {target}

Reconnaissance Style: {style}
Target Domain: {target}

"""
        
        if categories:
            prompt += f"Focus on these categories: {', '.join(categories)}\n"
        else:
            prompt += "Generate dorks for all relevant categories.\n"
        
        style_instructions = {
            'stealth': "Focus on passive information gathering that won't trigger alerts. Use generic search terms.",
            'aggressive': "Generate comprehensive dorks for deep reconnaissance. Include advanced operators.",
            'phishing': "Focus on finding employee information, email addresses, and social profiles.",
            'quick': "Generate the most effective dorks for rapid assessment. Focus on high-impact searches."
        }
        
        prompt += f"\nStyle Guidelines: {style_instructions.get(style, 'Generate comprehensive dorks.')}\n"
        
        prompt += """
Generate dorks in these categories:
1. admin_portals - Login pages, admin panels, management interfaces
2. sensitive_files - Config files, logs, backups, databases
3. directory_listings - Open directories, file indexes
4. technology_stack - CMS, frameworks, server technologies
5. employee_info - Staff directories, contact information
6. api_endpoints - API documentation, exposed endpoints
7. development - Test sites, staging environments, debug info
8. credentials - Potential credential leaks, password files

Return results as JSON format:
{
    "admin_portals": ["dork1", "dork2"],
    "sensitive_files": ["dork3", "dork4"],
    ...
}
"""
        
        return prompt
    
    def _parse_ai_dork_response(self, response: str) -> Dict[str, List[str]]:
        """Parse AI response into structured dork categories"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Fallback parsing if JSON is not properly formatted
                return self._fallback_parse_dorks(response)
        except Exception as e:
            self.logger.error(f"Failed to parse AI dork response: {e}")
            return {}
    
    def _fallback_parse_dorks(self, response: str) -> Dict[str, List[str]]:
        """Fallback parsing for non-JSON AI responses"""
        dorks = {}
        current_category = None
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for category headers
            if any(keyword in line.lower() for keyword in ['admin', 'sensitive', 'directory', 'technology', 'employee', 'api', 'development', 'credentials']):
                current_category = line.lower().replace(':', '').replace('-', '_').strip()
                if current_category not in dorks:
                    dorks[current_category] = []
            elif line.startswith('site:') or 'inurl:' in line or 'filetype:' in line:
                # This looks like a dork
                if current_category:
                    dorks[current_category].append(line)
                else:
                    if 'general' not in dorks:
                        dorks['general'] = []
                    dorks['general'].append(line)
        
        return dorks
    
    def _generate_template_dorks(self, target: str, categories: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """Generate dorks using predefined templates"""
        all_dorks = {
            'admin_portals': [
                f'site:{target} inurl:admin',
                f'site:{target} inurl:login',
                f'site:{target} inurl:administrator',
                f'site:{target} inurl:wp-admin',
                f'site:{target} inurl:cpanel',
                f'site:{target} "admin panel"',
                f'site:{target} "management console"',
                f'site:{target} inurl:portal admin'
            ],
            
            'sensitive_files': [
                f'site:{target} filetype:log',
                f'site:{target} filetype:sql',
                f'site:{target} filetype:bak',
                f'site:{target} filetype:config',
                f'site:{target} filetype:env',
                f'site:{target} ".env"',
                f'site:{target} "config.php"',
                f'site:{target} filetype:xml sitemap',
                f'site:{target} filetype:txt robots'
            ],
            
            'directory_listings': [
                f'site:{target} "index of"',
                f'site:{target} "parent directory"',
                f'site:{target} "directory listing"',
                f'site:{target} intitle:"index of"',
                f'site:{target} "index of /" password',
                f'site:{target} "index of /" backup'
            ],
            
            'technology_stack': [
                f'site:{target} "powered by"',
                f'site:{target} "built with"',
                f'site:{target} inurl:wordpress',
                f'site:{target} inurl:drupal',
                f'site:{target} "apache server"',
                f'site:{target} "nginx server"',
                f'site:{target} inurl:phpmyadmin',
                f'site:{target} "server: apache"'
            ],
            
            'employee_info': [
                f'site:{target} "staff" OR "employees" OR "team"',
                f'site:{target} "contact us" email',
                f'site:{target} "@{target.replace("www.", "")}"',
                f'"{target.replace("www.", "")}" email contact',
                f'site:linkedin.com "{target.replace("www.", "").split(".")[0]}"',
                f'site:{target} "directory" employee'
            ],
            
            'api_endpoints': [
                f'site:{target} inurl:api',
                f'site:{target} "api documentation"',
                f'site:{target} inurl:swagger',
                f'site:{target} "rest api"',
                f'site:{target} inurl:v1 OR inurl:v2 OR inurl:v3',
                f'site:{target} filetype:json api'
            ],
            
            'development': [
                f'site:{target} inurl:dev',
                f'site:{target} inurl:test',
                f'site:{target} inurl:staging',
                f'site:{target} inurl:beta',
                f'site:{target} "development" OR "dev server"',
                f'site:{target} inurl:debug',
                f'site:{target} "test environment"'
            ],
            
            'credentials': [
                f'site:{target} "password" filetype:txt',
                f'site:{target} "username" AND "password"',
                f'site:{target} filetype:sql "password"',
                f'site:{target} "login credentials"',
                f'site:{target} ".htpasswd"',
                f'site:{target} "default password"'
            ]
        }
        
        if categories:
            return {cat: all_dorks[cat] for cat in categories if cat in all_dorks}
        
        return all_dorks
    
    def save_dorks(self, target: str, dorks: Dict[str, List[str]]) -> str:
        """Save generated dorks to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_safe = target.replace('/', '_').replace(':', '_')
        filename = f"dorks_{target_safe}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        dork_data = {
            'target': target,
            'timestamp': timestamp,
            'total_dorks': sum(len(category_dorks) for category_dorks in dorks.values()),
            'categories': list(dorks.keys()),
            'dorks': dorks
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(dork_data, f, indent=2)
            
            self.logger.info(f"Dorks saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save dorks: {e}")
            return ""
    
    def display_dorks(self, target: str, dorks: Dict[str, List[str]]):
        """Display generated dorks in a formatted way"""
        total_dorks = sum(len(category_dorks) for category_dorks in dorks.values())
        
        print(f"\n🎯 Custom Google Dorks for {target}")
        print(f"{'='*60}")
        print(f"Total Dorks Generated: {total_dorks}")
        print(f"Categories: {len(dorks)}")
        
        for category, category_dorks in dorks.items():
            if category_dorks:
                print(f"\n📋 {category.replace('_', ' ').title()} ({len(category_dorks)} dorks):")
                for i, dork in enumerate(category_dorks[:5], 1):  # Show first 5 per category
                    print(f"  {i}. {dork}")
                
                if len(category_dorks) > 5:
                    print(f"  ... and {len(category_dorks) - 5} more dorks")
        
        print(f"\n{'='*60}")
        print("💡 Copy and paste these dorks into Google Search")
        print("⚠️  Use responsibly and only for authorized testing")
    
    def export_to_txt(self, target: str, dorks: Dict[str, List[str]]) -> str:
        """Export dorks to a simple text file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_safe = target.replace('/', '_').replace(':', '_')
        filename = f"dorks_{target_safe}_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                f.write(f"Google Dorks for {target}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                for category, category_dorks in dorks.items():
                    if category_dorks:
                        f.write(f"{category.replace('_', ' ').title()}:\n")
                        f.write("-" * 40 + "\n")
                        for dork in category_dorks:
                            f.write(f"{dork}\n")
                        f.write("\n")
            
            self.logger.info(f"Dorks exported to text file: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to export dorks to text: {e}")
            return ""