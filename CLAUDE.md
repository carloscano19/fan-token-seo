# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a specialized Micro-SaaS application for SEO content strategy planning, specifically focused on Fan Token trading content. It uses Streamlit for the UI and Claude Haiku via the Anthropic API for AI-powered content strategy generation.

## Quick Start

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Configure API key:**
Edit `.streamlit/secrets.toml` and add your Anthropic API key:
```toml
[anthropic]
api_key = "your-anthropic-api-key-here"
```

**Run the application:**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Application Architecture

### Core Components

**Context Constants** (`app.py` top-level):
- `DEFAULT_GUIDELINES`: Strategic content guidelines focused on trader audience, volatility, and low correlation with crypto markets
- `DEFAULT_TEMPLATE`: Structured template for content briefs including metadata, article structure, outline, keywords, and LLM optimization notes

**Session State Management**:
- `generated_strategies`: List of 10 AI-generated article titles
- `selected_strategies`: User-selected titles for brief generation
- `generated_briefs`: Dictionary mapping titles to full content briefs

### Two-Step Workflow

1. **Strategy Generation** (`generate_strategies`):
   - Takes existing titles and guidelines as input
   - Uses Claude Haiku to generate 10 new, non-repetitive article titles
   - Emphasizes trader-focused, opportunity-driven content
   - Avoids themes from existing content

2. **Brief Generation** (`generate_brief`):
   - Takes selected title, template, and guidelines
   - Uses Claude Haiku to create detailed content brief
   - Follows strict template structure
   - Includes metadata, outline, keywords, and LLM instructions

### UI Structure

**Sidebar**:
- Existing titles input (to avoid repetition)
- Editable strategic guidelines
- Editable brief template

**Main Area** (two columns):
- Left: Strategy generation and selection
- Right: Brief generation trigger

**Results Display**:
- Tabbed interface for multiple briefs
- Download buttons (individual markdown or bulk CSV)

## Model Configuration

The application uses **Claude Haiku 4** (`claude-haiku-4-20250131`) for:
- Fast strategy generation (max_tokens: 1024)
- Detailed brief generation (max_tokens: 4096)

To use a different model, update the `model` parameter in both `generate_strategies` and `generate_brief` functions.

## Strategic Context

The content strategy is built around:
- **Target Audience**: Traders seeking profit, not sports fans
- **Key USP**: Low correlation with crypto market + volatility during matches
- **Narrative**: Infrastructure-ready, adoption-focused future
- **Tone**: Authoritative, financial opportunity language
- **Three Content Levels**: Top (unique asset class), Mid (digital stocks), Tactical (daily setups)

This context is critical for generating appropriate content strategies and must be preserved when modifying guidelines.

## File Structure

```
fan-token-seo-planner/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── secrets.toml               # API key configuration (not in git)
└── CLAUDE.md                      # This file
```

## Common Modifications

**Changing the content focus**: Modify `DEFAULT_GUIDELINES` constant

**Adjusting brief structure**: Modify `DEFAULT_TEMPLATE` constant

**Adding new generation steps**: Follow the pattern of session state + helper function + UI button

**Changing AI behavior**: Adjust prompts in `generate_strategies` and `generate_brief` functions
