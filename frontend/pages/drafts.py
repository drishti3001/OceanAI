import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.utils.api import draft_email, generate_reply, load_inbox, delete_draft

st.set_page_config(page_title="Draft Center", layout="wide")

def load_css():
    css_path = Path(__file__).parent.parent / "styles" / "global.css"
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# ------------------ PAGE HEADER ------------------
st.markdown(
    """
    <div class="page-header">
        <h1 style="margin:0;">Draft Center</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load inbox
try:
    with st.spinner("Loading drafts..."):
        emails = load_inbox()
        emails_with_drafts = [e for e in emails if e.get("drafts")]

    if not emails_with_drafts:
        st.info("No drafts available. Generate one from Inbox Viewer.")
        st.stop()

    st.success(f"Found {len(emails_with_drafts)} emails with drafts")

    # -------- DRAFT LIST --------
    for email in emails_with_drafts:
        with st.expander(
            f"{email['subject']} — {len(email['drafts'])} draft(s)",
            expanded=True,
        ):
            st.caption(f"From: {email['sender']}")
            st.caption(f"ID: {email['id']}")

            st.markdown("<div class='section'></div>", unsafe_allow_html=True)

            # Drafts
            for i, draft in enumerate(email["drafts"]):
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.subheader(f"Draft {i + 1}")

                st.text_area(
                    "",
                    draft,
                    height=200,
                    key=f"draft_{email['id']}_{i}",
                )

                col1, col2 = st.columns([1, 1])

                with col1:
                    st.button(
                        "Copy Draft",
                        key=f"copy_{email['id']}_{i}",
                        help="Copy text manually (Streamlit limitation)",
                        use_container_width=True,
                    )
                with col2:
                    if st.button(
                        "Delete Draft",
                        key=f"delete_{email['id']}_{i}",
                        use_container_width=True,
                        type="secondary", # Use secondary type to distinguish
                    ):
                        try:
                            with st.spinner(f"Deleting Draft {i + 1}..."):
                                # Call the API helper function
                                delete_draft(email["id"], i)
                            # Success message and page reload to update list
                            st.success(f"✅ Draft {i + 1} successfully deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting draft: {str(e)}")

                st.markdown("</div>", unsafe_allow_html=True)

            # -------- NEW DRAFT SECTION --------
            st.subheader("Create New Draft")

            draft_type = st.radio(
                "Type",
                ["Auto Reply", "Custom Draft"],
                key=f"type_{email['id']}",
            )

            if draft_type == "Auto Reply":
                persona = st.text_input(
                    "Persona (optional)",
                    value="Email Assistant",
                    key=f"persona_{email['id']}",
                )
                if st.button("Generate Auto Reply", key=f"auto_{email['id']}"):
                    try:
                        generate_reply(email["id"], persona)
                        st.success("Draft generated! Refresh to see it.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

            else:
                instructions = st.text_area(
                    "Instructions",
                    height=100,
                    key=f"instructions_{email['id']}",
                )
                if st.button("Create Custom Draft", key=f"custom_{email['id']}"):
                    if not instructions.strip():
                        st.warning("Please provide instructions.")
                    else:
                        try:
                            draft_email(email["id"], instructions)
                            st.success("Draft created!")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

except Exception as e:
    st.error(f"Failed to load drafts: {str(e)}")

# -------- QUICK ACTIONS --------
st.divider()
col1, col2 = st.columns(2)

with col1:
    if st.button("Refresh Drafts"):
        st.rerun()

with col2:
    st.page_link("pages/inbox.py", label="Go to Inbox")
