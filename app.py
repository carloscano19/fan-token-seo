import streamlit as st
import anthropic
import pandas as pd
import io
import time

# ============================================================================
# CONTEXT CONSTANTS
# ============================================================================

# CAMBIO 1: Guidelines por defecto genéricas para que no te molesten
DEFAULT_GUIDELINES = """AUDIENCE: [Define tu audiencia aquí, ej: Fans casuales, Inversores, Gamers...]
KEY USP: [Puntos de venta clave]
NARRATIVE: [La narrativa principal o ángulo de la historia]
AVOID: [Temas o palabras a evitar]
USE: [Palabras clave o conceptos obligatorios]
TONE: [Ej: Informativo, Divertido, Serio, Urgente...]
GOALS: [Objetivo del contenido]"""

DEFAULT_TEMPLATE = """## Metadatos
- Target Audience: [Target]
- Tone: [Tone]
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
    page_title="SEO Content Strategy Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS STYLING: CLEAN LIGHT THEME
# ============================================================================

st.markdown("""
<style>
    /* 1. FUENTE GLOBAL */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }

    /* 2. FONDO PRINCIPAL (BLANCO PURO) */
    .stApp {
        background-color: #ffffff !important;
        color: #111827 !important;
    }

    /* 3. BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        border-right: 1px solid #e5e7eb;
    }

    /* 4. TEXTOS DE LA BARRA LATERAL */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div {
        color: #111827 !important;
    }

    /* 5. CAJAS DESPLEGABLES */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
    }
    .streamlit-expanderHeader:hover {
        border-color: #cbd5e1 !important;
        color: #000000 !important;
    }
    .streamlit-expanderHeader svg {
        fill: #111827 !important;
    }

    /* 6. INPUTS */
    .stTextInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }

    /* 7. SUBIR ARCHIVOS */
    [data-testid="stFileUploader"] section {
        background-color: #ffffff !important;
        border: 1px dashed #d1d5db !important;
    }
    [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small {
        color: #4b5563 !important;
    }

    /* 8. BOTONES */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    /* 9. TARJETAS */
    .strategy-card, .result-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* 10. TÍTULOS */
    h1 {
        color: #111827 !important;
        font-weight: 800 !important;
    }
    .main h2, .main h3 {
        color: #374151 !important;
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
    if uploaded_file is None:
        return []
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please use CSV or Excel.")
            return []

        if len(df.columns) > 0:
            titles = df.iloc[:, 0].dropna().astype(str).tolist()
            return [title.strip() for title in titles if title.strip()]
        return []
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return []

def load_guidelines_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        content = uploaded_file.read().decode('utf-8')
        return content
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""

def combine_titles(file_titles, manual_titles):
    all_titles = []
    all_titles.extend(file_titles)
    if manual_titles.strip():
        manual_list = [title.strip() for title in manual_titles.split('\n') if title.strip()]
        all_titles.extend(manual_list)
    
    seen = set()
    unique_titles = []
    for title in all_titles:
        title_lower = title.lower()
        if title_lower not in seen:
            seen.add(title_lower)
            unique_titles.append(title)
    return unique_titles

def combine_guidelines(file_content, manual_content):
    combined = []
    if file_content.strip():
        combined.append(file_content.strip())
    if manual_content.strip():
        combined.append(manual_content.strip())
    return "\n\n".join(combined)

# ============================================================================
# HELPER FUNCTIONS - AI CLIENT
# ============================================================================

def get_anthropic_client(api_key_input):
    if api_key_input and api_key_input.strip():
        try:
            return anthropic.Anthropic(api_key=api_key_input.strip())
        except Exception as e:
            st.error(f"Error with provided API key: {e}")
            return None
    try:
        api_key = st.secrets["anthropic"]["api_key"]
        if api_key and api_key != "your-anthropic-api-key-here":
            return anthropic.Anthropic(api_key=api_key)
    except Exception:
        pass
    st.warning("⚠️ Please enter your Anthropic API Key in the Settings section of the sidebar.")
    st.stop()
    return None

# CAMBIO 2: Eliminado el sesgo de inversor. Ahora obedece a 'guidelines'.
def generate_strategies(existing_titles, guidelines, api_key_input):
    """Generate 10 new content strategy titles based strictly on user guidelines."""
    client = get_anthropic_client(api_key_input)
    if not client:
        return []

    prompt = f"""You are an expert SEO strategist.

EXISTING TITLES (to avoid repetition):
{existing_titles if existing_titles.strip() else "None provided"}

STRATEGIC GUIDELINES (Target Audience, Tone, Goals):
{guidelines}

Your task: Generate EXACTLY 10 new article titles based STRICTLY on the "STRATEGIC GUIDELINES" provided above.

Constraints:
1. The titles must appeal specifically to the AUDIENCE defined in the guidelines.
2. Adopt the TONE defined in the guidelines completely.
3. Avoid repeating themes from existing titles.
4. If the guidelines mention specific topics or keywords, prioritize them.

Format your response as a numbered list (1-10) with ONLY the titles, one per line.
Do not include any additional explanation or commentary."""

    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text
        titles = [line.strip() for line in response_text.split('\n') if line.strip() and line.strip()[0].isdigit()]

        cleaned_titles = []
        for title in titles:
            cleaned = title.split('.', 1)[-1].split(')', 1)[-1].strip()
            if cleaned:
                cleaned_titles.append(cleaned)

        return cleaned_titles[:10]

    except Exception as e:
        st.error(f"Error generating strategies: {e}")
        return []

# CAMBIO 3: Eliminado el sesgo en la generación de briefs.
def generate_brief(title, template, guidelines, api_key_input):
    """Generate a full content brief strictly following user guidelines and template."""
    client = get_anthropic_client(api_key_input)
    if not client:
        return ""

    prompt = f"""You are an expert SEO content strategist creating detailed content briefs.

ARTICLE TITLE:
{title}

STRATEGIC GUIDELINES:
{guidelines}

BRIEF TEMPLATE STRUCTURE TO FOLLOW:
{template}

Your task: Create a comprehensive content brief for this article that STRICTLY follows the template structure provided above.

Requirements:
1. Fill in ALL sections from the template.
2. Target Audience & Tone: Must match the STRATEGIC GUIDELINES provided exactly. Do not invent a new audience.
3. Create a detailed content outline with multiple H2 sections.
4. Provide a keywords table relevant to the specific topic.
5. Add LLM optimization notes on how to write this content based on the guidelines.
6. Do NOT assume this is for investors unless the guidelines explicitly say so.

Generate a complete, actionable brief that a writer or LLM can use to create high-quality content."""

    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    except Exception as e:
        st.error(f"Error generating brief: {e}")
        return ""

# ============================================================================
# MAIN APP INTERFACE - HEADER
# ============================================================================

st.markdown("""
<div style='text-align: center; padding: 2rem 0 1rem 0;'>
    <div style='display: inline-flex; align-items: center; gap: 1rem; margin-bottom: 1rem;'>
        <div style='font-size: 3.5rem; filter: drop-shadow(0 4px 12px rgba(102, 126, 234, 0.3));'>
            💎
        </div>
        <h1 style='font-size: 2.8rem; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; letter-spacing: -1px;'>
            SEO Strategy Planner
        </h1>
    </div>
    <p style='font-size: 1.15rem; color: #6b7280; margin-top: 0.5rem; font-weight: 500;'>
        AI-Powered Content Strategy Generator
    </p>
    <div style='display: flex; justify-content: center; gap: 1.5rem; margin-top: 1rem; font-size: 0.9rem; color: #9ca3af;'>
        <span>⚡ Claude Haiku 4</span>
        <span>•</span>
        <span>🎯 SEO Optimized</span>
        <span>•</span>
        <span>📊 Data-Driven</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Configuration Panel")
    st.markdown("")

    with st.expander("⚙️ Settings", expanded=True):
        api_key_input = st.text_input(
            "Anthropic API Key",
            type="password",
            help="Enter your Anthropic API key"
        )

    with st.expander("📂 Source Data", expanded=True):
        st.markdown("**Existing Titles**")
        st.caption("Upload a file or paste titles manually to avoid repetition")

        titles_file = st.file_uploader(
            "Upload Titles (CSV/Excel)",
            type=['csv', 'xlsx', 'xls'],
            key="titles_file"
        )

        manual_titles = st.text_area(
            "Or paste titles here (one per line)",
            height=100,
            placeholder="Paste existing article titles...",
            key="manual_titles"
        )

        file_titles = load_titles_from_file(titles_file) if titles_file else []
        all_titles = combine_titles(file_titles, manual_titles)

        if all_titles:
            st.success(f"✅ {len(all_titles)} unique titles loaded")

    with st.expander("🧠 Strategic Guidelines", expanded=False):
        st.markdown("**Content Strategy Guidelines**")
        st.caption("Upload guidelines or edit the default template")

        guidelines_file = st.file_uploader(
            "Upload Guidelines (TXT/MD)",
            type=['txt', 'md'],
            key="guidelines_file"
        )

        manual_guidelines = st.text_area(
            "Strategic Guidelines",
            value=DEFAULT_GUIDELINES,
            height=250,
            help="These guidelines drive the content strategy generation"
        )

        file_guidelines = load_guidelines_from_file(guidelines_file) if guidelines_file else ""
        final_guidelines = combine_guidelines(file_guidelines, manual_guidelines)

    with st.expander("📝 Brief Template", expanded=False):
        st.markdown("**Content Brief Structure**")

        brief_template = st.text_area(
            "Brief Template",
            value=DEFAULT_TEMPLATE,
            height=250,
            help="This template structure will be used for generating content briefs"
        )

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 🚀 Step 1: Generate Strategy Ideas")
    st.markdown("Generate 10 AI-powered article titles based on your guidelines.")

    if st.button("🎲 Generate 10 New Strategies", use_container_width=True, type="primary"):
        existing_titles_str = "\n".join(all_titles) if all_titles else ""

        with st.status("Generating strategies...", expanded=True) as status:
            st.write("🔍 Analyzing existing content...")
            st.write("🤖 Consulting Claude Haiku...")
            st.write("✨ Generating unique titles based on your custom guidelines...")

            strategies = generate_strategies(existing_titles_str, final_guidelines, api_key_input)

            if strategies:
                st.session_state.generated_strategies = strategies
                st.session_state.selected_strategies = []
                st.session_state.generated_briefs = {}
                status.update(label="✅ Generation complete!", state="complete")
            else:
                status.update(label="❌ Generation failed", state="error")

    if st.session_state.generated_strategies:
        st.markdown("---")
        st.markdown("#### 📋 Generated Titles")
        st.info("Select the titles you want to create detailed briefs for")

        selected = []
        for idx, title in enumerate(st.session_state.generated_strategies):
            st.markdown(f"""
            <div class="strategy-card">
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="font-weight: 700; color: #667eea; font-size: 1.1rem; min-width: 30px;">
                        {idx + 1}.
                    </div>
                    <div style="flex: 1; font-size: 0.95rem; line-height: 1.6; color: #1f2937;">
                        {title}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            is_checked = st.checkbox(f"Select this title", key=f"strategy_{idx}", label_visibility="collapsed")
            if is_checked:
                selected.append(title)

        st.session_state.selected_strategies = selected
        if selected:
            st.success(f"✅ {len(selected)} title(s) selected for brief generation")

with col2:
    st.subheader("📄 Step 2: Generate Content Briefs")
    st.markdown("Create detailed, structured content briefs for selected titles.")

    if st.session_state.selected_strategies:
        if st.button(f"Generate Briefs ({len(st.session_state.selected_strategies)})", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, title in enumerate(st.session_state.selected_strategies):
                status_text.text(f"✍️ Writing brief for: {title}...")
                brief = generate_brief(title, brief_template, final_guidelines, api_key_input)
                
                if brief:
                    st.session_state.generated_briefs[title] = brief
                
                progress_bar.progress((i + 1) / len(st.session_state.selected_strategies))

            status_text.success("✅ All briefs generated successfully!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
            st.rerun()

    if st.session_state.generated_briefs:
        st.markdown("---")
        st.markdown("### 📂 Your Content Briefs")
        for title, content in st.session_state.generated_briefs.items():
            with st.expander(f"📄 {title}", expanded=False):
                st.download_button(
                    label=f"📥 Download '{title[:20]}...'",
                    data=content,
                    file_name=f"{title.replace(' ', '_')}.md",
                    mime="text/markdown",
                    key=f"btn_{title}"
                )
                st.markdown("---")
                st.markdown(content)
    elif not st.session_state.selected_strategies:
        st.info("👈 Select strategies from Step 1 to generate briefs")

# ============================================================================
# RESULTS DISPLAY
# ============================================================================

if st.session_state.generated_briefs:
    st.markdown("---")
    st.markdown("## 📊 Generated Content Briefs")

    col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 2])
    with col_exp1:
        st.metric("Total Briefs", len(st.session_state.generated_briefs))
    with col_exp2:
        if len(st.session_state.generated_briefs) > 0:
            df = pd.DataFrame([
                {"Title": title, "Brief": brief}
                for title, brief in st.session_state.generated_briefs.items()
            ])
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download All (CSV)",
                data=csv,
                file_name="content_briefs.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.markdown("---")

    if len(st.session_state.generated_briefs) == 1:
        title = list(st.session_state.generated_briefs.keys())[0]
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(f"### 📝 {title}")
        st.markdown(st.session_state.generated_briefs[title])
        st.download_button(
            label="💾 Download Brief (Markdown)",
            data=st.session_state.generated_briefs[title],
            file_name=f"{title[:50]}.md",
            mime="text/markdown",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        tab_names = [f"Brief {i+1}" for i in range(len(st.session_state.generated_briefs))]
        tabs = st.tabs(tab_names)
        for idx, (title, brief) in enumerate(st.session_state.generated_briefs.items()):
            with tabs[idx]:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown(f"### 📝 {title}")
                with st.expander("📄 View Full Brief", expanded=True):
                    st.markdown(brief)
                col_dl1, col_dl2 = st.columns([1, 3])
                with col_dl1:
                    st.download_button(
                        label="💾 Download",
                        data=brief,
                        file_name=f"{title[:50]}.md",
                        mime="text/markdown",
                        key=f"download_{idx}",
                        use_container_width=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.9rem; padding: 1rem 0;'>
    <p>
        AI SEO Strategy Planner | Powered by
        <a href='https://www.anthropic.com/' target='_blank' style='color: #666; text-decoration: none;'>
            Claude Haiku 4
        </a>
    </p>
</div>
""", unsafe_allow_html=True)
