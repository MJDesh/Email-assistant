# 📬 AI Email Inbox Assistant

> An AI-powered email productivity assistant that helps you understand, prioritize, and respond to your inbox.

## Overview

**AI Email Inbox Assistant** uses Google Gemini to turn a regular email inbox into an intelligent productivity workspace.

Instead of manually going through every message, users can:

- Analyze emails and understand what needs attention
- Automatically identify priority and action items
- Generate reply drafts
- Ask natural-language questions about their inbox
- See which emails support an AI-generated answer

Built with **Python, Streamlit, Pydantic, and Google Gemini**.

## Features

### 🧠 AI Email Analysis

Select any email and get an AI-generated:

- Summary
- Priority level
- Priority reasoning
- Tasks and deadlines
- Sender sentiment
- Suggested reply tone

### ✍️ AI Reply Drafts

Generate a ready-to-edit response based on the email and its analysis.

Each draft includes:

- Confidence level
- Human-review recommendation
- Confidence reasoning

### 🔎 Ask My Inbox

Ask questions about your emails using natural language.

**Examples:**

```text
What are my upcoming deadlines?
```

```text
Which emails need my attention?
```

```text
Did anyone mention the client meeting?
```

```text
Which emails are related to the contract renewal?
```

The assistant returns an answer along with supporting source emails.

### 📥 Inbox Interface

- Email list and detail view
- Priority indicators
- Inbox health overview
- AI-powered actions directly from the selected email

## Tech Stack

- **Python**
- **Streamlit** — UI
- **Google Gemini** — LLM
- **google-genai** — Gemini API client
- **Pydantic** — structured AI outputs and validation
- **python-dotenv** — environment configuration
- **JSON** — sample email storage

## Project Structure

```text
.
├── main.py
├── llm_logic.py
├── schemas.py
├── data/
│   └── emails.json
├── .env.example
├── .gitignore
└── README.md
```

### Key Files

| File | Description |
|---|---|
| `main.py` | Streamlit application and UI |
| `llm_logic.py` | Gemini API calls and AI logic |
| `schemas.py` | Pydantic models for emails and AI responses |
| `data/emails.json` | Sample inbox data |

## Getting Started

### Prerequisites

- Python 3.10+
- A Google Gemini API key

### 1. Clone the repository

```bash
git clone <repository-url>
cd AI-Email-Inbox-Assistant
```

### 2. Create a virtual environment

**Windows**

```bash
python -m venv emailenv
emailenv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv emailenv
source emailenv/bin/activate
```

### 3. Install dependencies

```bash
pip install streamlit google-genai pydantic python-dotenv
```

Or, if the repository contains a `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

> **Never commit your `.env` file or API key to GitHub.**

### 5. Run the app

```bash
streamlit run main.py
```

The application will open in your browser.

## How It Works

```text
                    ┌──────────────────┐
                    │   Streamlit UI   │
                    │     main.py      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
          Analyze        Draft Reply    Ask Inbox
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌──────────────────┐
                    │   Gemini API     │
                    └──────────────────┘
                             │
                             ▼
                    Structured Response
                             │
                             ▼
                         Pydantic
```

AI responses are requested in structured JSON and validated using Pydantic models before being displayed.

## Safety & Grounding

The application is designed around a **human-in-the-loop** workflow:

- Generated replies are drafts and are not automatically sent.
- Inbox questions are instructed to use only the supplied email context.
- The model is instructed not to invent missing facts.
- Ask My Inbox returns supporting emails for its answers.
- Structured responses are validated before being used by the UI.

## Screenshots

Add screenshots of the application here:

```text
docs/
├── inbox.png
├── email-analysis.png
└── ask-my-inbox.png
```

## Roadmap

- [ ] Semantic email retrieval with embeddings
- [ ] Vector search for larger inboxes
- [ ] SQLite / FTS5 email search
- [ ] Gmail integration
- [ ] Calendar integration
- [ ] Conversation/thread context
- [ ] Persistent Ask My Inbox history
- [ ] Personalized reply style
- [ ] Follow-up and promise tracking
- [ ] AI response evaluation and monitoring

## Contributing

Contributions, suggestions, and improvements are welcome.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Commit your changes
5. Open a pull request

## License

Add your preferred license here.

---

**Built with Python, Streamlit, Google Gemini, and Pydantic.**
