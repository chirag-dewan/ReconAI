"""
Project status and health check utilities for ReconAI
"""

import subprocess
import importlib
from pathlib import Path
from typing import Dict, List, Tuple
import sys
import os

def check_project_health() -> Dict:
    """
    Comprehensive project health check
    
    Returns:
        Dict with health check results
    """
    results = {
        'overall_status': 'healthy',
        'checks': {},
        'warnings': [],
        'errors': [],
        'recommendations': []
    }
    
    # Check Python version
    python_check = _check_python_version()
    results['checks']['python_version'] = python_check
    if not python_check['status']:
        results['errors'].extend(python_check['messages'])
        results['overall_status'] = 'critical'
    
    # Check dependencies
    deps_check = _check_dependencies()
    results['checks']['dependencies'] = deps_check
    if not deps_check['status']:
        results['errors'].extend(deps_check['messages'])
        results['overall_status'] = 'critical'
    elif deps_check['warnings']:
        results['warnings'].extend(deps_check['messages'])
        if results['overall_status'] == 'healthy':
            results['overall_status'] = 'warning'
    
    # Check file structure
    structure_check = _check_file_structure()
    results['checks']['file_structure'] = structure_check
    if not structure_check['status']:
        results['errors'].extend(structure_check['messages'])
        results['overall_status'] = 'critical'
    
    # Check external tools
    tools_check = _check_external_tools()
    results['checks']['external_tools'] = tools_check
    if tools_check['warnings']:
        results['warnings'].extend(tools_check['messages'])
        if results['overall_status'] == 'healthy':
            results['overall_status'] = 'warning'
    
    # Check configuration
    config_check = _check_configuration()
    results['checks']['configuration'] = config_check
    if config_check['warnings']:
        results['warnings'].extend(config_check['messages'])
        if results['overall_status'] == 'healthy':
            results['overall_status'] = 'warning'
    
    # Generate recommendations based on findings
    results['recommendations'] = _generate_recommendations(results)
    
    return results

def _check_python_version() -> Dict:
    """Check Python version compatibility"""
    version = sys.version_info
    required_major, required_minor = 3, 8
    
    if version.major >= required_major and version.minor >= required_minor:
        return {
            'status': True,
            'messages': [f"✓ Python {version.major}.{version.minor}.{version.micro}"],
            'details': {'version': f"{version.major}.{version.minor}.{version.micro}"}
        }
    else:
        return {
            'status': False,
            'messages': [f"✗ Python {version.major}.{version.minor}.{version.micro} - Requires Python {required_major}.{required_minor}+"],
            'details': {'version': f"{version.major}.{version.minor}.{version.micro}"}
        }

def _check_dependencies() -> Dict:
    """Check if required Python packages are installed"""
    required_packages = [
        ('openai', 'OpenAI API integration'),
        ('requests', 'HTTP requests'),
        ('pyyaml', 'Configuration files'),
        ('python-dotenv', 'Environment variables'),
        ('rich', 'Rich text formatting'),
        ('pandas', 'Data processing'),
        ('beautifulsoup4', 'HTML parsing')
    ]
    
    optional_packages = [
        ('click', 'Enhanced CLI'),
        ('tabulate', 'Table formatting'),
        ('dnspython', 'DNS utilities'),
        ('python-nmap', 'Network scanning')
    ]
    
    missing_required = []
    missing_optional = []
    installed = []
    
    for package, description in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            installed.append(f"✓ {package} - {description}")
        except ImportError:
            missing_required.append(f"✗ {package} - {description}")
    
    for package, description in optional_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            installed.append(f"✓ {package} - {description} (optional)")
        except ImportError:
            missing_optional.append(f"⚠ {package} - {description} (optional)")
    
    messages = installed + missing_required + missing_optional
    
    return {
        'status': len(missing_required) == 0,
        'warnings': len(missing_optional) > 0,
        'messages': messages,
        'details': {
            'missing_required': missing_required,
            'missing_optional': missing_optional
        }
    }

def _check_file_structure() -> Dict:
    """Check if project file structure is intact"""
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        '.gitignore',
        'cli/__init__.py',
        'cli/core/__init__.py',
        'cli/core/orchestrator.py',
        'cli/core/config.py',
        'cli/core/logging_setup.py',
        'cli/core/results_formatter.py',
        'cli/tools/__init__.py',
        'cli/tools/bbot_wrapper.py',
        'cli/ai/__init__.py',
        'cli/ai/analyzer.py',
        'cli/utils/__init__.py',
        'cli/utils/helpers.py'
    ]
    
    optional_files = [
        '.env',
        'config/config.yaml',
        'test_installation.py',
        'install.sh'
    ]
    
    missing_required = []
    missing_optional = []
    present = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            present.append(f"✓ {file_path}")
        else:
            missing_required.append(f"✗ {file_path}")
    
    for file_path in optional_files:
        if Path(file_path).exists():
            present.append(f"✓ {file_path} (optional)")
        else:
            missing_optional.append(f"⚠ {file_path} (recommended)")
    
    messages = present + missing_required + missing_optional
    
    return {
        'status': len(missing_required) == 0,
        'warnings': len(missing_optional) > 0,
        'messages': messages,
        'details': {
            'missing_required': missing_required,
            'missing_optional': missing_optional
        }
    }

def _check_external_tools() -> Dict:
    """Check availability of external reconnaissance tools"""
    tools = {
        'bbot': {
            'command': ['bbot', '--version'],
            'description': 'Bbot reconnaissance framework',
            'required': True
        },
        'nmap': {
            'command': ['nmap', '--version'],
            'description': 'Network mapping tool',
            'required': False
        },
        'git': {
            'command': ['git', '--version'],
            'description': 'Version control system',
            'required': False
        }
    }
    
    available = []
    missing_required = []
    missing_optional = []
    
    for tool_name, tool_info in tools.items():
        try:
            result = subprocess.run(
                tool_info['command'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                available.append(f"✓ {tool_name} - {tool_info['description']} - {version_line}")
            else:
                if tool_info['required']:
                    missing_required.append(f"✗ {tool_name} - {tool_info['description']} - Command failed")
                else:
                    missing_optional.append(f"⚠ {tool_name} - {tool_info['description']} - Command failed")
        
        except (FileNotFoundError, subprocess.TimeoutExpired):
            if tool_info['required']:
                missing_required.append(f"✗ {tool_name} - {tool_info['description']} - Not found")
            else:
                missing_optional.append(f"⚠ {tool_name} - {tool_info['description']} - Not found")
    
    messages = available + missing_required + missing_optional
    
    return {
        'status': len(missing_required) == 0,
        'warnings': len(missing_optional) > 0,
        'messages': messages,
        'details': {
            'available': available,
            'missing_required': missing_required,
            'missing_optional': missing_optional
        }
    }

def _check_configuration() -> Dict:
    """Check configuration status"""
    config_issues = []
    config_ok = []
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        config_ok.append("✓ .env file exists")
        
        # Check for API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            if openai_key.startswith('sk-') and len(openai_key) >= 40:
                config_ok.append("✓ OpenAI API key configured")
            else:
                config_issues.append("⚠ OpenAI API key format looks invalid")
        else:
            config_issues.append("⚠ OpenAI API key not set (AI analysis disabled)")
    else:
        config_issues.append("⚠ .env file not found (copy .env.example)")
    
    # Check config directory
    config_dir = Path('config')
    if config_dir.exists():
        config_ok.append("✓ Config directory exists")
        
        config_file = config_dir / 'config.yaml'
        if config_file.exists():
            config_ok.append("✓ config.yaml found")
        else:
            config_issues.append("⚠ config.yaml not found (optional)")
    else:
        config_issues.append("⚠ Config directory missing (will be created)")
    
    # Check output directories
    for dir_name in ['output', 'logs']:
        if Path(dir_name).exists():
            config_ok.append(f"✓ {dir_name} directory exists")
        else:
            config_issues.append(f"⚠ {dir_name} directory missing (will be created)")
    
    messages = config_ok + config_issues
    
    return {
        'status': True,  # Configuration issues are warnings, not errors
        'warnings': len(config_issues) > 0,
        'messages': messages,
        'details': {'issues': config_issues}
    }

def _generate_recommendations(results: Dict) -> List[str]:
    """Generate recommendations based on health check results"""
    recommendations = []
    
    if results['overall_status'] == 'critical':
        recommendations.append("🚨 Critical issues detected - ReconAI may not function properly")
        recommendations.append("Run: pip install -r requirements.txt")
        recommendations.append("Ensure Python 3.8+ is installed")
    
    if results['overall_status'] == 'warning':
        recommendations.append("⚠ Some optional components are missing")
        
    # Specific recommendations based on checks
    deps_check = results['checks'].get('dependencies', {})
    if deps_check.get('warnings'):
        recommendations.append("Install optional dependencies for enhanced functionality")
    
    tools_check = results['checks'].get('external_tools', {})
    if tools_check.get('warnings'):
        missing_tools = tools_check.get('details', {}).get('missing_optional', [])
        if any('bbot' in tool for tool in missing_tools):
            recommendations.append("Install Bbot: pip install bbot")
        if any('nmap' in tool for tool in missing_tools):
            recommendations.append("Install Nmap for network scanning capabilities")
    
    config_check = results['checks'].get('configuration', {})
    if config_check.get('warnings'):
        recommendations.append("Copy .env.example to .env and configure your API keys")
        recommendations.append("Run: python main.py --create-config")
    
    if not recommendations:
        recommendations.append("✅ Everything looks good! Your ReconAI installation is ready.")
    
    return recommendations

def print_health_status(results: Dict):
    """Print formatted health status"""
    status_colors = {
        'healthy': '🟢',
        'warning': '🟡', 
        'critical': '🔴'
    }
    
    status = results['overall_status']
    print(f"\n{status_colors.get(status, '⚪')} ReconAI Health Status: {status.upper()}")
    print("=" * 60)
    
    # Print each check category
    for check_name, check_results in results['checks'].items():
        print(f"\n{check_name.replace('_', ' ').title()}:")
        for message in check_results['messages']:
            print(f"  {message}")
    
    # Print warnings and errors
    if results['warnings']:
        print(f"\n🟡 Warnings ({len(results['warnings'])}):")
        for warning in results['warnings'][:5]:  # Limit to 5 to avoid spam
            print(f"  {warning}")
        if len(results['warnings']) > 5:
            print(f"  ... and {len(results['warnings']) - 5} more")
    
    if results['errors']:
        print(f"\n🔴 Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  {error}")
    
    # Print recommendations
    if results['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"  {rec}")
    
    print("\n" + "=" * 60)