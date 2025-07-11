"""
Configuration management for ReconAI
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

class Config:
    """Configuration manager for ReconAI"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        load_dotenv()
        
        # Default configuration
        self._defaults = {
            'general': {
                'output_dir': 'output',
                'log_level': 'INFO',
                'max_scan_timeout': 300,
                'auto_create_dirs': True
            },
            'ai': {
                'model': 'gpt-4',
                'temperature': 0.3,
                'max_tokens': 2000,
                'enable_analysis': True
            },
            'tools': {
                'bbot': {
                    'enabled': True,
                    'default_flags': ['subdomain-enum'],
                    'timeout': 300,
                    'output_formats': ['json', 'human']
                },
                'spiderfoot': {
                    'enabled': False,
                    'timeout': 600
                },
                'google_dorks': {
                    'enabled': False,
                    'max_results': 100,
                    'delay': 1
                }
            },
            'output': {
                'save_raw': True,
                'save_parsed': True,
                'save_analysis': True,
                'compress_old': True,
                'retention_days': 30
            }
        }
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from files and environment"""
        config = self._defaults.copy()
        
        # Load from config file if it exists
        config_file = self.config_dir / 'config.yaml'
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        config.update(file_config)
            except Exception as e:
                logging.warning(f"Failed to load config file: {e}")
        
        # Override with environment variables
        self._load_env_overrides(config)
        
        return config
    
    def _load_env_overrides(self, config: Dict[str, Any]):
        """Load configuration overrides from environment variables"""
        env_mappings = {
            'OPENAI_API_KEY': ('ai', 'api_key'),
            'OPENAI_MODEL': ('ai', 'model'),
            'LOG_LEVEL': ('general', 'log_level'),
            'OUTPUT_DIR': ('general', 'output_dir'),
            'MAX_SCAN_TIMEOUT': ('general', 'max_scan_timeout'),
            'BBOT_TIMEOUT': ('tools', 'bbot', 'timeout'),
            'AI_TEMPERATURE': ('ai', 'temperature'),
            'AI_MAX_TOKENS': ('ai', 'max_tokens')
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Navigate to the nested config location
                current = config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Convert value to appropriate type
                try:
                    if env_var in ['MAX_SCAN_TIMEOUT', 'BBOT_TIMEOUT', 'AI_MAX_TOKENS']:
                        value = int(value)
                    elif env_var in ['AI_TEMPERATURE']:
                        value = float(value)
                    elif env_var in ['AI_ENABLE_ANALYSIS']:
                        value = value.lower() in ('true', '1', 'yes', 'on')
                except ValueError:
                    logging.warning(f"Invalid value for {env_var}: {value}")
                    continue
                
                current[config_path[-1]] = value
    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            section: Configuration section
            key: Configuration key (optional)
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        if key is None:
            return self.config.get(section, default)
        
        section_config = self.config.get(section, {})
        return section_config.get(key, default)
    
    def set(self, section: str, key: str, value: Any):
        """
        Set configuration value
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def save(self):
        """Save current configuration to file"""
        config_file = self.config_dir / 'config.yaml'
        try:
            with open(config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from config or environment"""
        return self.get('ai', 'api_key') or os.getenv('OPENAI_API_KEY')
    
    def get_output_dir(self) -> str:
        """Get output directory"""
        return self.get('general', 'output_dir', 'output')
    
    def get_log_level(self) -> str:
        """Get logging level"""
        return self.get('general', 'log_level', 'INFO')
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled"""
        return self.get('tools', {}).get(tool_name, {}).get('enabled', False)
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration for a specific tool"""
        return self.get('tools', {}).get(tool_name, {})
    
    def create_example_config(self):
        """Create an example configuration file"""
        example_file = self.config_dir / 'config.example.yaml'
        
        example_config = {
            'general': {
                'output_dir': 'output',
                'log_level': 'INFO',
                'max_scan_timeout': 300
            },
            'ai': {
                'model': 'gpt-4',
                'temperature': 0.3,
                'max_tokens': 2000,
                'api_key': 'your_openai_api_key_here'
            },
            'tools': {
                'bbot': {
                    'enabled': True,
                    'default_flags': ['subdomain-enum'],
                    'timeout': 300
                },
                'spiderfoot': {
                    'enabled': False,
                    'base_url': 'http://localhost:5001',
                    'timeout': 600
                }
            },
            'output': {
                'save_raw': True,
                'save_parsed': True,
                'save_analysis': True,
                'compress_old': True
            }
        }
        
        try:
            with open(example_file, 'w') as f:
                yaml.dump(example_config, f, default_flow_style=False, indent=2)
            return str(example_file)
        except Exception as e:
            logging.error(f"Failed to create example config: {e}")
            return None
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate current configuration
        
        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check required settings
        if not self.get_openai_api_key():
            results['warnings'].append("OpenAI API key not configured (AI analysis will be disabled)")
        
        # Check output directory
        output_dir = Path(self.get_output_dir())
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                results['errors'].append(f"Cannot create output directory: {e}")
                results['valid'] = False
        
        # Validate tool configurations
        for tool_name, tool_config in self.get('tools', {}).items():
            if tool_config.get('enabled'):
                timeout = tool_config.get('timeout', 300)
                if timeout <= 0:
                    results['errors'].append(f"Invalid timeout for {tool_name}: {timeout}")
                    results['valid'] = False
        
        # Validate AI configuration
        ai_config = self.get('ai', {})
        temperature = ai_config.get('temperature', 0.3)
        if not 0 <= temperature <= 2:
            results['warnings'].append(f"AI temperature {temperature} outside recommended range (0-2)")
        
        max_tokens = ai_config.get('max_tokens', 2000)
        if max_tokens <= 0 or max_tokens > 4000:
            results['warnings'].append(f"AI max_tokens {max_tokens} outside reasonable range")
        
        return results