# Fan Token SEO Content Strategy Planner

A specialized Micro-SaaS application for generating AI-powered SEO content strategies focused on Fan Token trading.

## Features

- **Strategy Generation**: Generate 10 unique, trader-focused article titles using Claude Haiku
- **Content Brief Creation**: Automatically create detailed content briefs following a structured template
- **Customizable Guidelines**: Edit strategic guidelines and brief templates to fit your needs
- **Export Options**: Download individual briefs as markdown or all briefs as CSV

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Edit `.streamlit/secrets.toml` and add your Anthropic API key:

```toml
[anthropic]
api_key = "your-anthropic-api-key-here"
```

Get your API key from: https://console.anthropic.com/

### 3. Run the Application

```bash
streamlit run app.py
```

Or using Python module syntax:

```bash
python3 -m streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## How to Use

### Step 1: Configure (Sidebar)
1. **Existing Titles**: Enter any existing article titles (one per line) to avoid repetition
2. **Strategic Guidelines**: Review and edit the content strategy guidelines (pre-filled)
3. **Brief Template**: Review and edit the content brief structure (pre-filled)

### Step 2: Generate Strategies
1. Click "Generate 10 Strategies" to create new article title ideas
2. Review the generated titles
3. Select the titles you want to create detailed briefs for

### Step 3: Generate Briefs
1. Click "Generate Briefs for Selected" to create full content briefs
2. Review the generated briefs in tabs
3. Download individual briefs (markdown) or all briefs (CSV)

## Strategic Focus

This tool is specifically designed for Fan Token content with a **trader audience**:

- Target: Traders seeking profit opportunities, not sports fans
- Key USP: Low correlation with crypto markets + match-driven volatility
- Tone: Authoritative, financial opportunity-focused
- Three content levels:
  - **Top**: Unique asset class positioning (Sports x Crypto x Finance)
  - **Mid**: Digital stocks with uncorrelated action
  - **Tactical**: Daily setups and momentum cycles

## Technology Stack

- **Frontend**: Streamlit
- **AI Model**: Claude Haiku 4 (Anthropic)
- **Data Handling**: Pandas
- **Language**: Python 3.9+

## Project Structure

```
fan-token-seo-planner/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── secrets.toml         # API key configuration (not in git)
├── README.md                # This file
└── CLAUDE.md                # Claude Code guidance
```

## Customization

### Modify Content Guidelines
Edit the `DEFAULT_GUIDELINES` constant in `app.py` to change the strategic focus.

### Adjust Brief Structure
Edit the `DEFAULT_TEMPLATE` constant in `app.py` to modify the content brief format.

### Change AI Model
Update the `model` parameter in `generate_strategies()` and `generate_brief()` functions to use a different Claude model.

## Support

For issues or questions, please refer to:
- Anthropic API Documentation: https://docs.anthropic.com/
- Streamlit Documentation: https://docs.streamlit.io/

## License

MIT License - feel free to use and modify for your own projects.
