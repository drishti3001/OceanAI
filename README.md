# Prompt-Driven Email Productivity Agent

A full-stack productivity assistant that streams your inbox data through user-defined prompts to automate categorization, action-item extraction, agent insights, and reply drafting.

## ✨ Features
- **Inbox Viewer**: Browse mock emails with sender, subject, timestamp, category tags, action items, and drafts.
- **Prompt Brain Panel**: Create, Edit, and Delete the "Agent Brain." All LLM operations (categorization, drafting, chat) are dynamically guided by these stored prompts.
- **Automated Categorization & Action Extraction**: Triggered per email via backend FastAPI endpoints; results persist to the mock inbox.
- **Draft Center**: Generate polite reply drafts or custom responses. **Drafts are saved only—no outbound email.**
- **Agent Chat**: A context-aware agent that can summarize the whole inbox or analyze specific emails based on user selection.
- **Gemini AI Integration**: Uses Google's Gemini Flash model for intelligent, fast, and prompt-driven responses.

## 🏗 Architecture Overview
```text
Email_productivity/
├── backend/        # FastAPI app, domain models, services, routers
│   ├── models/     # Email + Prompt dataclasses
│   ├── services/   # Inbox, PromptBrain, Agent Logic, LLM Wrapper
│   ├── routes/     # /api endpoints
│   └── main.py     # Application Entry Point
├── frontend/       # Streamlit multipage UI
│   ├── pages/      # Inbox, Prompts, Chat, Drafts
│   └── utils/      # API client
├── data/           # inbox.json (Mock Database)
├── prompts.json    # The "Agent Brain" (User Prompts)
├── requirements.txt
└── README.md
```

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key

### 2. Installation
The project uses a single virtual environment for simplicity.
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Email_productivity
```

# 2. Create and activate virtual environment
python -m venv venv

Windows:
```
venv\Scripts\activate
```
Mac/Linux:
```
source venv/bin/activate
```

# 3. Install dependencies
```
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory to store your API key:
```env
# .env file content
Email_key=YOUR_GEMINI_API_KEY_HERE
```

## 🚀 How to Run the UI and Backend
You need two terminal windows (both with the `venv` activated).

### Terminal 1: Backend (FastAPI)
Run this command from the **root** directory:
```bash
python -m uvicorn backend.main:app
# API will be served at [http://127.0.0.1:8000](http://127.0.0.1:8000)
```

### Terminal 2: Frontend (Streamlit)
Run this command from the root directory:
```bash
streamlit run frontend/app.py
# UI will open at http://localhost:8501
```

## 📥 How to Load the Mock Inbox
The Mock Inbox is located at data/inbox.json.

Automatic Loading: The system automatically loads this file on startup.

Resetting Data: To reset the inbox to its initial state (uncategorized), simply replace the content of data/inbox.json with the provided "Fresh Inbox" JSON assets.

Persistence: Any changes made in the UI (Categories, Action Items, Drafts) are automatically saved back to data/inbox.json.

## 🧠 How to Configure Prompts
Navigate to the Prompt Brain page in the UI.

Create: Use the form to define a new prompt with a unique ID.

Edit: Expand any existing prompt to modify its template.

Delete: Remove prompts you no longer need (Note: Default prompts like agent are protected from permanent deletion to ensure system stability)

Dynamic Behavior: Changes take effect immediately. For example, editing the agent prompt to "Speak like a pirate" will instantly change the Chat Agent's persona without restarting the server.

## 🕹 Usage Examples
1. Categorization:
Go to Inbox Viewer.
The system attempts to auto-categorize emails on load using the categorize prompt.
You can manually refresh categorization by reloading the page.
2. Action Item Extraction:
Click on an email in the Inbox Viewer.
Click the "Extract Actions" button.
The LLM will parse the body using the actions prompt and list tasks with deadlines.
3. Agent Chat:
Go to Agent Chat.
Inbox Query: Select "None" in the context dropdown and ask "Summarize my inbox."
Specific Email: Select an email from the dropdown and ask "What is the tone of this email?"

## 🔐 Safety & Robustness
No Auto-Send: The backend has no SMTP integration. All outputs are saved to the drafts array in inbox.json.

Error Handling: If the LLM fails or the API key is invalid, the UI displays a clear error message rather than crashing.
