# ReconAI

Automated reconnaissance with AI-powered analysis and prioritization.

## Overview

ReconAI combines traditional security reconnaissance tools with AI analysis to provide intelligent insights, risk prioritization, and actionable recommendations for security researchers and penetration testers.

## Features

- **Multi-tool Integration**: Supports Bbot, Spiderfoot, and custom Google Dorks
- **AI-Powered Analysis**: Uses GPT-4 to summarize findings and prioritize threats
- **Unified Output**: Consistent JSON output format across all tools
- **CLI Interface**: Fast, automation-friendly command-line interface
- **Web Dashboard**: (Coming soon) Interactive web interface for results visualization

## Installation

```bash
git clone https://github.com/chirag-dewan/recon-ai.git
cd recon-ai
pip install -r requirements.txt
```

## Quick Start

```bash
# Basic domain scan with Bbot
python main.py -t example.com

# Full scan with AI analysis
python main.py -t example.com --tool all --analyze

# Scan IP range
python main.py -t 192.168.1.0/24 --tool bbot --analyze
```

## Project Structure

```
recon-ai/
├── cli/                 # Core CLI modules
│   ├── core/           # Main orchestration logic
│   ├── tools/          # Tool wrappers
│   ├── parsers/        # Output parsing modules
│   └── ai/             # AI integration
├── web/                # Web interface (future)
├── config/             # Configuration files
├── output/             # Results storage
├── logs/               # Application logs
└── docs/               # Documentation
```

## Configuration

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here
BBOT_CONFIG_PATH=/path/to/bbot/config
SPIDERFOOT_CONFIG_PATH=/path/to/spiderfoot/config
```

## Supported Tools

- **Bbot**: Comprehensive subdomain enumeration and reconnaissance
- **Spiderfoot**: OSINT automation and data correlation
- **Google Dorks**: Custom search queries for information gathering
- **Custom Modules**: Extensible framework for additional tools

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for authorized security testing only. Users are responsible for complying with all applicable laws and regulations.