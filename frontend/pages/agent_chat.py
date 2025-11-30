import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.utils.api import agent_query, load_inbox

st.set_page_config(page_title="Agent Chat", layout="wide")

def load_css():
    css_path = Path(__file__).parent.parent / "styles" / "global.css"
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# ------------------ PAGE HEADER ------------------
st.markdown(
    """
    <div class="page-header">
        <h1 style="margin:0;">Agent Chat</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Load inbox
try:
    emails: List[Dict[str, Any]] = load_inbox()
except Exception as e:
    st.error(f"Failed to load inbox: {str(e)}")
    emails = []

# Map email data for selection
email_id_map = {f"{e['subject']} ({e['id']})": e['id'] for e in emails}
email_options = ["None (Inbox-wide Query)"] + list(email_id_map.keys())

# --- SIDEBAR & CONTEXT SELECTION ---
with st.sidebar:
    st.subheader("Quick Queries")

    # Selectbox returns str or None
    selected_subject = st.selectbox("Select Email", email_options, key="selected_email_subject")
    
    # CRITICAL FIX: Handle the None case safely before dictionary lookup
    selected_email_id: Optional[str] = None
    
    if selected_subject and selected_subject != "None (Inbox-wide Query)":
        # We know selected_subject is a valid string key here
        selected_email_id = email_id_map.get(selected_subject)
        
    st.session_state.selected_email_id_for_chat = selected_email_id

    def handle_quick_query(label: str, qtype: str, message: str):
        if st.button(label):
            try:
                # This call requires the API update in frontend/utils/api.py
                result = agent_query(qtype, email_id=st.session_state.selected_email_id_for_chat) 
                
                st.session_state.chat_history.append({"role": "user", "content": message})
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": result["response"]}
                )
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

    handle_quick_query("Inbox Summary", "summary", "Show me an inbox summary")
    handle_quick_query("Urgent Emails", "urgent", "What are the urgent emails?")
    handle_quick_query("Follow-Ups", "followups", "Show me follow-up emails")
    handle_quick_query("Tasks", "tasks", "What tasks do I have?")

    st.subheader("Email Context")
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# ------------------ CHAT SECTION ------------------
st.subheader("Chat")

chat_container = st.container()

with chat_container:
    for msg in st.session_state.chat_history:
        role_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-assistant"
        st.markdown(
            f"<div class='{role_class}'>{msg['content']}</div>",
            unsafe_allow_html=True,
        )

user_input = st.chat_input("Ask a question about your inbox...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Use a generic query type for free-form input
    query_type = user_input 
    
    # Override query_type for quick actions if detected in free-form input
    txt = user_input.lower()
    if any(x in txt for x in ["urgent", "priority"]):
        query_type = "urgent"
    elif any(x in txt for x in ["follow", "follow-up"]):
        query_type = "followups"
    elif any(x in txt for x in ["task", "todo"]):
        query_type = "tasks"

    try:
        with st.spinner("Thinking..."):
            # This call requires the API update in frontend/utils/api.py
            result = agent_query(query_type, email_id=st.session_state.selected_email_id_for_chat) 
            
            st.session_state.chat_history.append(
                {"role": "assistant", "content": result["response"]}
            )
        st.rerun()
    except Exception as e:
        st.session_state.chat_history.append(
            {"role": "assistant", "content": f"Error: {str(e)}"}
        )
        st.rerun()