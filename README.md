# ReconAI

🔍 **Automated reconnaissance with AI-powered analysis and prioritization**

ReconAI combines traditional security reconnaissance tools with AI analysis to provide intelligent insights, risk prioritization, and actionable recommendations for security researchers and penetration testers.

## ✨ Features

- **🔧 Multi-tool Integration**: Supports Bbot, Spiderfoot, and custom Google Dorks
- **🧠 AI-Powered Analysis**: Uses GPT-4 to summarize findings and prioritize threats  
- **📊 Multiple Output Formats**: Text, JSON, HTML, and CSV reports
- **⚙️ Flexible Configuration**: YAML config files with environment variable overrides
- **🖥️ Professional CLI**: Rich formatting, progress tracking, and comprehensive logging
- **📈 Extensible Architecture**: Easy to add new tools and analysis modules

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/chirag-dewan/recon-ai.git
cd recon-ai
chmod +x install.sh
./install.sh
```

Or manual installation:
```bash
pip install -r requirements.txt
pip install bbot
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Verify Installation
```bash
python main.py --health
```

### Basic Usage

```bash
# Quick domain scan
python main.py -t example.com

# Full scan with AI analysis  
python main.py -t example.com --analyze --format all

# Scan IP range with verbose output
python main.py -t 192.168.1.0/24 --tool bbot --analyze -v

# Scan with custom output format
python main.py -t target.com --format html --analyze
```

## 📋 Command Reference

### Core Commands
```bash
# Run reconnaissance
python main.py -t <target> [options]

# Health check
python main.py --health

# Configuration management  
python main.py --config              # Show config status
python main.py --create-config       # Create example config
```

### Options
- `-t, --target`: Target to scan (domain, IP, CIDR, or organization)
- `--tool`: Tool to use (`bbot`, `spiderfoot`, `google-dorks`, `all`)
- `--analyze`: Enable AI analysis of results
- `--format`: Output format (`text`, `json`, `html`, `csv`, `all`)  
- `--output-dir`: Directory for results (default: `output`)
- `-v, --verbose`: Enable verbose logging

## 🎯 Target Types

ReconAI automatically detects and handles different target types:

| Type | Example | Description |
|------|---------|-------------|
| **Domain** | `example.com` | Domain name reconnaissance |
| **IP Address** | `192.168.1.1` | Single IP address scanning |
| **CIDR Range** | `192.168.1.0/24` | Network range scanning |
| **URL** | `https://example.com` | Extract domain from URL |
| **Organization** | `"Acme Corp"` | Organization-based OSINT |

## 📊 Output Formats

### Text Report
```bash
python main.py -t example.com --format text
```
Clean, readable console output with structured sections.

### JSON Export  
```bash
python main.py -t example.com --format json
```
Machine-readable format for integration with other tools.

### HTML Report
```bash
python main.py -t example.com --format html
```
Professional web-based report with styling and tables.

### CSV Summary
```bash
python main.py -t example.com --format csv  
```
Spreadsheet-compatible format for data analysis.

### All Formats
```bash
python main.py -t example.com --format all
```
Generate all format types simultaneously.

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Required for AI analysis
OPENAI_API_KEY=your_openai_api_key_here

# Optional settings
LOG_LEVEL=INFO
OUTPUT_DIR=output
MAX_SCAN_TIMEOUT=300
```

### Configuration File (config/config.yaml)
```yaml
general:
  output_dir: output
  log_level: INFO
  max_scan_timeout: 300

ai:
  model: gpt-4
  temperature: 0.3
  max_tokens: 2000

tools:
  bbot:
    enabled: true
    timeout: 300
    default_flags: ['subdomain-enum']
  
  spiderfoot:
    enabled: false
    timeout: 600
```

## 🛠️ Tool Integration

### Bbot (Default)
- Comprehensive subdomain enumeration
- Technology detection  
- Port scanning
- Web crawling

### Spiderfoot (Coming Soon)
- OSINT automation
- Data correlation
- Threat intelligence

### Google Dorks (Coming Soon)  
- Custom search queries
- Information disclosure detection
- Sensitive file discovery

## 🧠 AI Analysis

When `--analyze` is enabled, ReconAI uses GPT-4 to:

- **Summarize** key findings in plain English
- **Prioritize** findings by risk level (Critical/High/Medium/Low)
- **Identify** potential attack vectors and security concerns  
- **Provide** actionable recommendations for both red and blue teams
- **Highlight** unusual or particularly interesting discoveries

## 📁 Project Structure

```
recon-ai/
├── main.py                 # Main CLI entry point
├── cli/                    # Core application modules
│   ├── core/              # Core orchestration and config
│   ├── tools/             # Tool wrappers (Bbot, etc.)
│   ├── ai/                # AI analysis modules  
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── output/                # Results and reports
├── logs/                  # Application logs
└── docs/                  # Documentation
```

## 🔧 Development

### Running Tests
```bash
python test_installation.py
```

### Adding New Tools
1. Create wrapper in `cli/tools/`
2. Implement standard interface
3. Update orchestrator configuration
4. Add tool-specific parsers

### Code Style
```bash
black .
flake8
```

## 📝 Examples

### Basic Domain Reconnaissance
```bash
python main.py -t example.com --analyze
```

### Multi-target CIDR Scan
```bash  
python main.py -t 10.0.0.0/24 --tool bbot --format html -v
```

### Complete Assessment with All Tools
```bash
python main.py -t target.com --tool all --analyze --format all
```

### Organization OSINT
```bash
python main.py -t "Acme Corporation" --tool spiderfoot --analyze
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)  
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is intended for authorized security testing only. Users are responsible for complying with all applicable laws and regulations. Always obtain proper authorization before testing systems you do not own.

## 🆘 Support

- 📖 **Documentation**: Check the `/docs` folder for detailed guides
- 🐛 **Issues**: Report bugs via GitHub Issues  
- 💬 **Discussions**: Use GitHub Discussions for questions
- 🔧 **Health Check**: Run `python main.py --health` for diagnostics

---
