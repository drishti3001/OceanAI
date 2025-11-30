import streamlit as st
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from frontend.utils.api import list_prompts, update_prompt, delete_prompt 


st.set_page_config(page_title="Prompt Brain", layout="wide")

def load_css():
    css_path = Path(__file__).parent.parent / "styles" / "global.css"
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# --- INITIAL STATE & TRANSIENT MESSAGE HANDLERS ---
if "prompts_data" not in st.session_state:
    st.session_state.prompts_data = []
if 'message' not in st.session_state:
    st.session_state['message'] = None


# --- UTILITY FUNCTIONS ---

def fetch_prompts(clear_cache: bool = False):
    """Fetches prompts and updates session state."""
    try:
        if clear_cache:
            list_prompts.clear() 
        data = list_prompts()
        st.session_state.prompts_data = data
        return data
    except Exception as e:
        st.error(f"Error loading prompts: {str(e)}")
        return []

def handle_save(prompt_id, name, description, template):
    """Handles prompt update and UI refresh."""
    updated = {
        "id": prompt_id,
        "name": name,
        "description": description,
        "template": template,
    }
    try:
        update_prompt(prompt_id, updated) 
        st.session_state['message'] = (f"success", f"Prompt '{name}' saved successfully.")
        fetch_prompts(clear_cache=True) 
        st.rerun()
    except Exception as e:
        st.session_state['message'] = ("error", f"Error saving prompt: {str(e)}")
        st.rerun()

def handle_delete(prompt_id, name):
    """Handles prompt deletion and UI refresh."""
    try:
        # Call the actual delete API function
        delete_prompt(prompt_id) 
        
        st.session_state['message'] = ("success", f"✅ Prompt '{name}' deleted successfully.")
        
        # CRITICAL FIX: Clear cache after deletion to force UI reload
        fetch_prompts(clear_cache=True)
        st.rerun()
    except Exception as e:
        # NOTE: We keep the exception handler here to catch non-404 errors (like API connection errors)
        st.session_state['message'] = ("error", f"Error deleting prompt: {str(e)}")
        st.rerun()


# ------------------ PAGE HEADER ------------------
st.markdown(
    """
    <div class="page-header">
        <h1 style="margin:0;">Prompt Brain</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Display transient messages
if st.session_state['message']:
    msg_type, msg_text = st.session_state['message']
    if msg_type == "success":
        st.success(msg_text)
    elif msg_type == "error":
        st.error(msg_text)
    st.session_state['message'] = None


# ------------------ MAIN LOAD ------------------

if not st.session_state.prompts_data:
    with st.spinner("Loading prompts..."):
        fetch_prompts(clear_cache=False) 

prompts = st.session_state.prompts_data

if not prompts:
    st.warning("No prompts found.")

st.success(f"Loaded {len(prompts)} prompts")

# ------------------ 1. CREATE NEW PROMPT SECTION ------------------

st.divider()
st.subheader("➕ Create New Prompt")

with st.form("new_prompt_form", clear_on_submit=True):
    # Using uuid.uuid4().hex[:4] for a shorter, guaranteed unique ID base
    new_id_default = f"custom_{uuid.uuid4().hex[:4]}"
    new_id = st.text_input("Prompt ID (Required)", value=new_id_default, help="A unique, lowercase identifier for the prompt.")
    new_name = st.text_input("Name", value="New Custom Prompt")
    new_description = st.text_area("Description", height=80)
    new_template = st.text_area("Template", height=200, value="Insert your LLM instructions and placeholders here: {email_body}")

    submitted = st.form_submit_button("Create & Save New Prompt")
    
    if submitted:
        if any(p['id'] == new_id for p in prompts):
            st.error("Error: This Prompt ID already exists. Please choose a unique ID.")
        else:
            handle_save(new_id, new_name, new_description, new_template)


# ------------------ 2. EDIT EXISTING PROMPTS SECTION ------------------
st.divider()
st.subheader("✏️ Edit Existing Prompts")

for prompt in prompts:
    # Use st.form to group inputs for a single submission, improving Streamlit performance
    with st.form(f"edit_form_{prompt['id']}"): 
        with st.expander(f"{prompt['name']} (ID: {prompt['id']})", expanded=False):

            st.caption(f"Prompt ID: **{prompt['id']}** (Cannot be edited)")

            name = st.text_input("Name", value=prompt["name"], key=f"name_{prompt['id']}")
            description = st.text_area(
                "Description",
                value=prompt.get("description", ""),
                key=f"desc_{prompt['id']}",
                height=80,
            )
            template = st.text_area(
                "Template",
                value=prompt["template"],
                height=200,
                key=f"template_{prompt['id']}",
            )

            col_save, col_delete = st.columns([3, 1])

            with col_save:
                if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                    handle_save(prompt["id"], name, description, template)

            with col_delete:
                st.empty() 

    # Place delete button outside the st.form structure for easier functionality
    col_empty, col_delete_outside = st.columns([3, 1])
    with col_delete_outside:
        if st.button("Delete Prompt", key=f"delete_btn_{prompt['id']}", type="secondary", use_container_width=True):
            handle_delete(prompt["id"], prompt["name"])