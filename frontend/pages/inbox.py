import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

params = st.query_params
if "email_id" in params:
    st.session_state.selected_email_id = params["email_id"]


sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.utils.api import (
    categorize_email,
    extract_actions,
    generate_reply,
    load_inbox,
)

st.set_page_config(page_title="Inbox Viewer", layout="wide")

def load_css():
    css_path = Path(__file__).parent.parent / "styles" / "global.css"
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# ------------------ Page Header ------------------
st.markdown(
    """
    <div class="page-header">
        <h1 style="margin:0;">Inbox Viewer</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------ Session State ------------------
if "selected_email_id" not in st.session_state:
    st.session_state.selected_email_id = None


# ------------------ Utility Functions ------------------
def format_timestamp(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


def category_badge(cat: str) -> str:
    """Generate category badge with appropriate color dot."""
    # Normalize category name (handle variations)
    cat_lower = cat.lower().strip()
    dot_map = {
        "to-do": "dot-todo",
        "todo": "dot-todo",
        "to do": "dot-todo",
        "newsletter": "dot-newsletter",
        "spam": "dot-spam",
        "meeting": "dot-meeting",
        "follow-up": "dot-followup",
        "followup": "dot-followup",
        "personal": "dot-personal",
        "other": "dot-other",
    }
    dot_class = dot_map.get(cat_lower, "dot-other")
    # Capitalize first letter of each word for display
    display_name = cat.replace("-", " ").title()
    return f"<span class='badge-dot {dot_class}'></span>{display_name}"


# ------------------ Load Inbox ------------------
@st.cache_data(ttl=1)  # Cache for 1 second to allow refresh
def get_inbox_data():
    """Load inbox with short cache to allow refresh after updates."""
    return load_inbox()

try:
    with st.spinner("Loading inbox..."):
        emails: List[Dict[str, Any]] = get_inbox_data()
        
        # Auto-categorize emails that don't have a category (only once per session)
        if "emails_categorized" not in st.session_state:
            st.session_state.emails_categorized = set()
        
        uncategorized = [
            e for e in emails 
            if (not e.get("category") or e.get("category", "").strip() == "") 
            and e["id"] not in st.session_state.emails_categorized
        ]
        
        if uncategorized:
            # Categorize uncategorized emails in background
            for email in uncategorized:
                try:
                    categorize_email(email["id"])
                    st.session_state.emails_categorized.add(email["id"])
                except Exception:
                    # Silently continue if categorization fails
                    pass
            # Clear cache and reload
            get_inbox_data.clear()
            emails = get_inbox_data()

    if not emails:
        st.info("Your inbox is empty.")
        st.stop()

    col1, col2 = st.columns([1.1, 2])

    # ---------------- LEFT COLUMN ----------------
    with col1:
        st.markdown("<h3 style='margin-bottom: 0.2rem; margin-top: 0;'>Emails</h3>", unsafe_allow_html=True)

        for email in emails:
            email: Dict[str, Any]

            is_selected = (
                "selected" if email["id"] == st.session_state.selected_email_id else ""
            )
            category = email.get("category", "Other")
            badge = category_badge(category)

            # Create a clickable container using button
            button_clicked = st.button(
                f"📧 {email['subject'][:45]}",
                key=f"email_btn_{email['id']}",
                use_container_width=True,
            )
            
            if button_clicked:
                st.session_state.selected_email_id = email["id"]
                st.rerun()

            # Display email info in a card
            if is_selected:
                st.markdown(
                    f"""
                    <div class="email-list-card selected" style="margin-top: 0.1rem; margin-bottom: 0.6rem; padding: 0.8rem;">
                        <div style="color:#444 !important; font-size:0.85rem; margin-bottom: 2px;">From: {email['sender']}</div>
                        <div style="color:#666 !important; font-size:0.75rem; margin-bottom: 4px;">{format_timestamp(email['timestamp'])}</div>
                        <div style="margin-top:4px; font-size:0.8rem; color:#111 !important;">{badge}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="email-list-card" style="margin-top: 0.1rem; margin-bottom: 0.6rem; padding: 0.8rem;">
                        <div style="color:#444 !important; font-size:0.85rem; margin-bottom: 2px;">From: {email['sender']}</div>
                        <div style="color:#666 !important; font-size:0.75rem; margin-bottom: 4px;">{format_timestamp(email['timestamp'])}</div>
                        <div style="margin-top:4px; font-size:0.8rem; color:#111 !important;">{badge}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ---------------- RIGHT COLUMN ----------------
    with col2:
        st.subheader("Email Details")

        selected_email: Optional[Dict[str, Any]] = next(
            (e for e in emails if e["id"] == st.session_state.selected_email_id),
            None,
        )

        if not selected_email:
            st.info("Select an email from the list")
            st.stop()

        # Email Header
        st.markdown(
            f"""
            <div class="card">
                <h3 style="margin-bottom:4px;">{selected_email['subject']}</h3>
                <p><strong>From:</strong> {selected_email['sender']}</p>
                <p><strong>Date:</strong> {format_timestamp(selected_email['timestamp'])}</p>
                <p style="margin-top:6px;">
                    <strong>Category:</strong> {category_badge(selected_email.get('category','Other'))}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Email Body
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("**Body:**")
        st.markdown(
            f"""
            <div style="background-color: #f9fafb; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb; color: #111; line-height: 1.6; white-space: pre-wrap;">
                {selected_email["body"]}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Action items
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Action Items")
        actions = selected_email.get("action_items", [])
        if actions:
            # Use st.markdown to render the whole bulleted list at once
            list_markdown = "\n".join([f"- {a}" for a in actions])
            st.markdown(list_markdown)
        else:
            st.info("No action items extracted.")
        st.markdown("</div>", unsafe_allow_html=True)

        # Buttons
        colA, colB = st.columns(2)

        with colA:
            if st.button("Extract Actions", key="extract_btn"):
                try:
                    with st.spinner("Extracting..."):
                        extract_actions(selected_email["id"])
                    get_inbox_data.clear()
                    st.session_state.selected_email_id = selected_email["id"]
                    st.success("Action items extracted")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        with colB:
            if st.button("Generate Reply", key="reply_btn"):
                try:
                    with st.spinner("Generating..."):
                        generate_reply(selected_email["id"])
                    get_inbox_data.clear()
                    st.session_state.selected_email_id = selected_email["id"]
                    st.success("Draft created in Draft Center")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        # Drafts
        drafts = selected_email.get("drafts", [])
        if drafts:
            st.subheader("Drafts")
            for i, d in enumerate(drafts):
                with st.expander(f"Draft {i+1}"):
                    st.text_area("", d, height=160, key=f"draft_{i}")

except Exception as e:
    st.error(f"Backend error: {e}")
