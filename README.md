# 🤖 ReconGPT

> *An AI-powered reconnaissance assistant that transforms raw OSINT into actionable intelligence using GPT-4 and custom automation pipelines.*

## 🎯 What is ReconGPT?

ReconGPT is a modular offensive reconnaissance assistant that automates OSINT collection using **Bbot** and enhances it with **AI-powered analysis** using GPT-4. It doesn't just collect data—it provides **threat insights, prioritization, and actionable intelligence**.

### 🔥 Key Differentiators
- **AI-Enhanced Analysis**: GPT-4 analyzes findings and highlights high-value targets
- **Custom Google Dork Generation**: AI creates tailored search queries for your target
- **Target Prioritization**: Automatic risk scoring and asset categorization
- **Actionable Intelligence**: Get next steps, not just data dumps
- **Multiple Recon Styles**: Stealth, aggressive, or phishing-focused scanning

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/chirag-dewan/recongpt.git
cd recongpt
pip install -r requirements.txt
pip install bbot
```

### Configuration
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### Basic Usage
```bash
# AI-powered domain reconnaissance
python main.py -t example.com --analyze

# Generate custom Google Dorks
python main.py -t example.com --dorks

# Full intelligence gathering with prioritization
python main.py -t example.com --style aggressive --analyze --format html
```

---

## 🧠 Core Features

### 1. **AI-Augmented Recon Pipeline**
- Integrates with [Bbot](https://github.com/blacklanternsecurity/bbot) for comprehensive OSINT
- GPT-4 analyzes findings and identifies:
  - 🎯 Vulnerable subdomains
  - 🔑 Leaked credentials
  - 💎 High-value assets
  - ⚠️ Misconfigurations
  - 🚨 Unusual behaviors

### 2. **Custom Google Dork Generator**
```bash
python main.py -t target.com --dorks
```
AI generates targeted search queries for:
- Admin portals and login pages
- Exposed log files and backups
- Sensitive data indexes
- Technology stack indicators
- Configuration files

### 3. **Target Prioritization Engine**
GPT-4 evaluates findings and assigns:
- **Risk Scores** (0-100)
- **Confidence Levels**
- **Attack Surface Analysis**
- **Prioritized Target Lists**

### 4. **Recon Style Modes**
```bash
--style stealth       # Passive-only reconnaissance
--style aggressive    # Deep scanning with all modules
--style phishing      # Email and social media focused
--style quick         # Fast overview scan
```

### 5. **Intelligence Reports**
Professional reports with:
- Executive summary
- High-value target identification
- Attack vector analysis
- Recommended next steps
- Technical findings breakdown

---

## 💻 Command Examples

### Basic Reconnaissance
```bash
# Standard scan with AI analysis
python main.py -t example.com --analyze

# Quick scan for initial assessment
python main.py -t example.com --style quick --format text
```

### Advanced Intelligence Gathering
```bash
# Comprehensive aggressive scan
python main.py -t target.com --style aggressive --analyze --dorks --format all

# Phishing campaign preparation
python main.py -t company.com --style phishing --analyze --format html

# Stealth reconnaissance
python main.py -t sensitive-target.com --style stealth --analyze
```

### Google Dork Generation
```bash
# Generate custom dorks for target
python main.py -t example.com --dorks-only

# Combine recon with dork generation
python main.py -t example.com --analyze --dorks --format html
```

### Multi-Target Operations
```bash
# Scan multiple targets
python main.py -t target1.com,target2.com,target3.com --analyze

# Scan from file
python main.py --targets-file targets.txt --style aggressive
```

---

## 📊 Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `text` | Clean console output | Quick analysis |
| `json` | Structured data | Automation/parsing |
| `html` | Professional web report | Presentations |
| `markdown` | Documentation format | Documentation |
| `pdf` | Executive summary | Client deliverables |

---

## 🎨 Sample Output

### AI-Generated Target Prioritization
```
🔴 HIGH PRIORITY TARGETS:
- admin.example.com (exposed admin panel, weak auth)
- api.example.com (sensitive endpoints, no rate limiting)
- backup.example.com (database backups accessible)

🟡 MEDIUM PRIORITY:
- dev.example.com (development environment, info disclosure)
- staging.example.com (staging data, potential secrets)

🟢 LOW PRIORITY:
- www.example.com (standard website, limited attack surface)
```

### Custom Generated Dorks
```
🎯 ADMIN PORTALS:
site:example.com inurl:admin
site:example.com inurl:login "admin panel"

🔍 SENSITIVE FILES:
site:example.com filetype:log
site:example.com "index of" confidential
```

---

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo for cost savings
BBOT_CONFIG_PATH=/path/to/bbot/config
LOG_LEVEL=INFO
```

### Advanced Configuration (`config.yaml`)
```yaml
ai:
  model: gpt-4
  temperature: 0.3
  max_tokens: 2000

recon:
  default_style: aggressive
  timeout: 600
  
dorks:
  categories:
    - admin_portals
    - sensitive_files
    - tech_stack
    - backups

output:
  auto_open_html: true
  save_dorks: true
```

---

## 🏗️ Architecture

```
ReconGPT/
├── main.py                    # CLI entry point
├── core/
│   ├── orchestrator.py        # Main workflow coordination
│   ├── config.py              # Configuration management
│   └── styles.py              # Recon style definitions
├── tools/
│   ├── bbot_wrapper.py        # Enhanced Bbot integration
│   └── dork_generator.py      # AI-powered dork creation
├── ai/
│   ├── analyzer.py            # GPT-4 analysis engine
│   ├── prioritizer.py         # Target prioritization
│   └── prompts.py             # AI prompt templates
├── reporting/
│   ├── formatter.py           # Multi-format output
│   └── templates/             # Report templates
└── utils/
    ├── helpers.py             # Utility functions
    └── validators.py          # Input validation
```

---

## 🎯 Use Cases

### 🔴 Red Team Operations
- Pre-engagement reconnaissance
- Attack surface mapping
- Target prioritization
- Intelligence gathering

### 🛡️ Blue Team Defense
- Asset discovery and inventory
- Security posture assessment
- Threat landscape analysis
- Vulnerability identification

### 🕵️ OSINT Research
- Corporate intelligence
- Digital footprint analysis
- Supply chain reconnaissance
- Competitive analysis

### 📱 Social Engineering
- Phishing campaign preparation
- Employee information gathering
- Technology stack identification
- Communication platform discovery

---

## 🔮 Roadmap

### Phase 1: Core Intelligence (Current)
- [x] AI-powered analysis
- [x] Custom dork generation
- [x] Target prioritization
- [x] Multiple output formats

### Phase 2: Advanced Features
- [ ] LangChain RAG integration
- [ ] Memory and learning capabilities
- [ ] Streamlit web interface
- [ ] Automated task planning

### Phase 3: Enterprise Features
- [ ] Team collaboration
- [ ] Campaign management
- [ ] Threat intelligence feeds
- [ ] API integrations (Shodan, Censys)

### Phase 4: AI Evolution
- [ ] GPT Agent-style autonomous operation
- [ ] Threat heatmap generation
- [ ] CVE correlation and analysis
- [ ] Predictive threat modeling

---

## 🛡️ Ethical Use

ReconGPT is designed for **authorized security testing only**. Users must:
- Obtain proper authorization before scanning
- Comply with all applicable laws and regulations
- Respect target systems and rate limits
- Use findings responsibly

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://github.com/yourusername/recongpt.git
cd recongpt
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Bbot](https://github.com/blacklanternsecurity/bbot) by Black Lantern Security
- [OpenAI](https://openai.com/) for GPT-4 API
- The OSINT and security research community

---

**Made with ❤️ for the security community**

*Transform your reconnaissance from data collection to intelligence generation.*