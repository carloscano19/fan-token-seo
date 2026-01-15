import streamlit as st
import anthropic
import pandas as pd
import io

# ============================================================================
# CONTEXT CONSTANTS
# ============================================================================

DEFAULT_GUIDELINES = """AUDIENCE: Traders who want to make money. NOT just fans.
KEY USP: Low correlation with crypto market. Volatility during matches.
NARRATIVE: Sell the future. Infrastructure is built, adoption is next.
AVOID: 'Match results drive price' (mirroring).
USE: 'Matches create volatility/setups'.
TONE: Authority, Financial Opportunity, 'Typically are', 'Tend to be'.
LEVELS:
1. Top: Unique asset class (Sports x Crypto x Finance).
2. Mid: Digital stocks with uncorrelated action.
3. Tactical: Daily setups, momentum cycles.
PROBLEMS TO OVERCOME: Low liquidity history, bad reputation, no organic flow. We must rebuild trust."""

DEFAULT_TEMPLATE = """## Metadatos
- Target Audience: [Developers, Traders, etc.]
- Tone: [Educational, Authoritative, etc.]
- Goal: [Specific SEO Goal]

## Article Structure
- H1: [Title]
- Slug URL: [slug]
- Intent: [Intent]
- Meta Title / Description: [...]

## Content Outline (Detailed)
- H2: [Topic]
  - Key points to cover...
  - Analogies to use...
- H2: [Topic]...

## Keywords Table
- Keyword | Volume | Notes

## LLM Optimization Notes
- Instructions on how to write the content (transitions, structure, etc.)."""

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Fan Token SEO Strategy Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PREMIUM FINTECH/SAAS CSS STYLING (CORREGIDO SIDEBAR + EXPANDERS)
# ============================================================================

st.markdown("""
<style>
    /* Import Inter Font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global Font Application */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main App Background - Subtle Gradient (Light Mode) */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #f9fafb 100%);
        color: #000000 !important; /* Texto principal en negro */
    }

    /* ============================================================ */
    /* SIDEBAR STYLING - ARREGLO DE COLORES */
    /* ============================================================ */
    
    /* 1. Fondo de la barra lateral (Azul Oscuro Elegante) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d29 0%, #252938 100%);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);
        border-right: 1px solid #2d3748;
    }

    /* 2. FORZAR TODOS LOS TEXTOS DE LA SIDEBAR A BLANCO */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }
    
    /* ------------------------------------------------------------ */
    /* ARREGLO CRÍTICO DE DESPLEGABLES (SETTINGS / SOURCE DATA)     */
    /* ESTO SOLUCIONA QUE SE VEAN BLANCOS                         */
    /* ------------------------------------------------------------ */
    
    /* Forzamos que la cabecera del desplegable sea OSCURA */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: #252938 !important; /* Fondo oscuro */
        color: #ffffff !important;             /* Texto blanco */
        border: 1px solid #4b5563 !important;  /* Borde gris */
    }
    
    /* Aseguramos que el texto dentro del header sea blanco */
    [data-testid="stSidebar"] .streamlit-expanderHeader p,
    [data-testid="stSidebar"] .streamlit-expanderHeader span {
        color: #ffffff !important;
    }
    
    /* El icono de la flechita a blanco */
    [data-testid="stSidebar"] .streamlit-expanderHeader svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }
    
    /* El contenido interior del desplegable también oscuro */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background-color: transparent !important;
        border: none !important;
        color: #ffffff !important;
    }
    
    /* ------------------------------------------------------------ */

    /* Inputs dentro de la sidebar (Cajas de texto y API Key) */
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stTextArea textarea {
        background-color: #2c3345 !important; /* Fondo gris azulado oscuro */
        color: #ffffff !important; /* Texto blanco al escribir */
        border: 1px solid #4b5563 !important;
    }
    
    /* Arreglo para la caja de Subir Archivos (File Uploader) */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        background-color: #2c3345 !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] span,
    [data-testid="stSidebar"] [data-testid="stFileUploader"] small {
        color: #e2e8f0 !important;
    }

    /* ============================================================ */
    /* ESTILOS DEL ÁREA PRINCIPAL (MAIN) */
    /* ============================================================ */

    /* Premium Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
    }

    /* Card Styling */
    .strategy-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        border: 1px solid #e5e7eb;
    }

    .result-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e7eb;
    }

    /* Header Styling */
    .main h1, .main h2, .main h3 {
        color: #1a1d29 !important;
        font-family: 'Inter', sans-serif !important;
    }

    h1 {
        font-size: 3rem !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    [data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: white !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px 10px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        border: 1px solid #e5e7eb;
        color: #000000 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
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
# HELPER FUNCTIONS - FILE PROCESSING
# ============================================================================

def load_titles_from_file(uploaded_file):
    """Load titles from CSV or Excel file."""
    if uploaded_file is None:
        return []

    try:
        # Check file type
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please use CSV or Excel.")
            return []

        # Get the first column as titles
        if len(df.columns) > 0:
            titles = df.iloc[:, 0].dropna().astype(str).tolist()
            return [title.strip() for title in titles if title.strip()]
        return []

    except Exception as e:
        st.error(f"Error reading file: {e}")
        return []

def load_guidelines_from_file(uploaded_file):
    """Load guidelines from TXT or MD file."""
    if uploaded_file is None:
        return ""

    try:
        # Read the file content
        content = uploaded_file.read().decode('utf-8')
        return content
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""

def combine_titles(file_titles, manual_titles):
    """Combine titles from file and manual input, removing duplicates."""
    all_titles = []

    # Add file titles
    all_titles.extend(file_titles)

    # Add manual titles (one per line)
    if manual_titles.strip():
        manual_list = [title.strip() for title in manual_titles.split('\n') if title.strip()]
        all_titles.extend(manual_list)

    # Remove duplicates while preserving order
    seen = set()
    unique_titles = []
    for title in all_titles:
        title_lower = title.lower()
        if title_lower not in seen:
            seen.add(title_lower)
            unique_titles.append(title)

    return unique_titles

def combine_guidelines(file_content, manual_content):
    """Combine guidelines from file and manual input."""
    combined = []

    if file_content.strip():
        combined.append(file_content.strip())

    if manual_content.strip():
        combined.append(manual_content.strip())

    return "\
