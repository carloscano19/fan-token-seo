import streamlit as st
import anthropic
import pandas as pd
import io
import time

# ============================================================================
# CONTEXT CONSTANTS - PRECARGADAS CON TU ESTRATEGIA SEGURA
# ============================================================================

DEFAULT_GUIDELINES = """AUDIENCE: 
Active sports fans who already own tokens or are curious about the tech utility. NOT investors, NOT traders, NOT legal experts.

TONE: 
Practical, "How-To", Comparative, Fun, Journalistic. 

STRICTLY AVOID (Negative Constraints):
1. NO Investment topics: Avoid words like "profit", "bull run", "market cap", "investment", "ROI".
2. NO Legal/Regulatory topics: Do not mention SEC, laws, regulations, or bans.
3. NO General "Beginner Guides": We already have "What is a token", "How to buy", etc. Do not repeat basics.
4. NO Hype words: Avoid "Revolutionizing", "New Era", "Paradigm Shift". Be specific, not vague.

MANDATORY FOCUS ANGLES (Choose from these):
1. "VS" Comparisons: Compare Fan Tokens to things fans already know (e.g., Airline Miles, McDonald's Monopoly, Season Tickets, Patreon).
2. Tech Support/Troubleshooting: Specific problems users face (e.g., "I lost my phone", "Phishing emails", "App glitches").
3. The "Unboxing" Experience: The logistics of redeeming physical items (shipping, sizing, waiting times).
4. Gamification/Fun: AR features, Token Hunts, prediction games within the apps.
5. Community Culture: Discord chats, specific polls that happened recently, fan stories.
6. History: Origin stories of specific tokens (without talking about price history).

GOAL: 
Generate titles that sound like helpful blog posts or tech reviews, NOT financial news or legal analysis."""

DEFAULT_TEMPLATE = """## Metadatos
- Target Audience: [Target specific from guidelines]
- Tone: [Tone from guidelines]
- Goal: [Specific User Intent]

## Article Structure
- H1: [Title]
- Slug URL: [slug]
- Intent: [Informational / Commercial / Navigational]
- Meta Title / Description: [...]

## Content Outline (Detailed)
- H2: [Topic]
  - Key points to cover...
  - Analogies to use (Use real-world comparisons)...
- H2: [Topic]...

## Keywords Table
- Keyword | Volume | Notes

## LLM Optimization Notes
- Instructions on how to write the content (transitions, structure, etc.)."""

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Fan Token Content Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS STYLING
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #ffffff !important; color: #111827 !important; }
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #e5e7eb; }
    [data-testid="stSidebar"] * { color: #111827 !important; }
    .streamlit-expanderHeader { background-color: #ffffff !important; color: #111827 !important; border: 1px solid #e5e7eb !important; border-radius: 6px !important; }
    .stTextInput input, .stTextArea textarea { background-color: #ffffff !important; color: #111827 !important; border: 1px solid #d1d5db !important; }
    .stButton > button { background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
    .strategy-card, .result-card { background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    h1 { color: #111827 !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if "generated_strategies" not in st.session_state:
    st.session_state.generated_strategies = []

if "selected_strategies" not in st.session_state:
    st.session_state.selected_strategies = []

if "generated_briefs" not in st.session_state:
    st.session_state.generated_briefs = {}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_titles_from_file(uploaded_file):
    if uploaded_file is None: return []
    try:
        if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')): df = pd.read_excel(uploaded_file)
        else: return []
        if len(df.columns) > 0: return [str(t).strip() for t in df.iloc[:, 0].dropna().tolist() if str(t).strip()]
        return []
    except: return []

def load_guidelines_from_file(uploaded_file):
    if uploaded_file is None: return ""
    try: return uploaded_file.read().decode('utf-8')
    except: return ""

def combine_titles(file_titles, manual_titles):
    all_titles = file_titles + [t.strip() for t in manual_titles.split('\n') if t.strip()]
    seen = set()
    return [x for x in all_titles if not (x.lower() in seen or seen.add(x.lower()))
