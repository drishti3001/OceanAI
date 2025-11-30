import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Email Productivity Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css():
    css_path = Path(__file__).parent / "styles" / "global.css"
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# ------------------ HEADER ------------------
st.markdown("""
<div class="page-header">
    <h1>Email Productivity Agent</h1>
    <h3 style="margin-top:-10px; color:#cbd5e1;">Welcome to the Email Productivity Agent</h3>
    <p style="color:#94a3b8; max-width:700px;">
        A prompt-driven email management system that helps you categorize emails,
        extract action items, generate smart drafts, and run inbox-wide AI queries.
    </p>
</div>
""", unsafe_allow_html=True)


st.sidebar.title("Navigation")
st.sidebar.markdown(
    """
- Inbox Viewer  
- Prompt Brain  
- Agent Chat  
- Draft Center  
"""
)

st.markdown("<div style='padding: 1rem;'>", unsafe_allow_html=True)



col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="card">
            <h3>Automated Categorization</h3>
            <p>Classify emails by urgency, type, and context.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="card">
            <h3>Smart Drafts</h3>
            <p>Generate contextual drafts using your custom prompt brain.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <h3>Action Item Extraction</h3>
            <p>Automatically detect tasks, follow-ups, and deadlines.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="card">
            <h3>Agent Insights</h3>
            <p>Query your inbox with intelligent natural-language questions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

