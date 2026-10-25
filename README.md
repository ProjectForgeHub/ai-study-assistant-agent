# 📚 AI Study Assistant

A modern, attractive, and interactive AI web application designed for students and learners.

The system helps students learn academic concepts, summarize lecture notes, generate exam-style practice quizzes with answer keys, and keep an interactive session history.

---

## 🚀 Key Features

1. **💡 Conceptual Problem Solver (Ask a Question)**
   - Breaks down tough academic concepts with clear explanations and intuitive real-world analogies.
   - Tailored specifically for students preparing for exams or understanding complex ideas.
   - Optional subject/course tagging and quick-pick sample prompts.

2. **📝 Note Synthesizer (Summarize Notes)**
   - Condenses raw lecture notes, slide transcripts, or textbook paragraphs.
   - Multiple formatting modes: **Standard Summary**, **Quick Bullets**, or **Key Definitions & Terms**.
   - Word count analysis and sample note loader for testing.

3. **🎯 Interactive Practice Quiz (Generate Quiz)**
   - Automatically generates exam practice questions from any topic or study passage.
   - Supports **Multiple Choice Questions (MCQs)** with explanations and answer keys, or **Conceptual Short-Answer** questions.
   - Configurable question counts (1 to 8 questions).

4. **🕒 Session History & Result Replay**
   - Seamlessly tracks all queries, summaries, and quizzes created during the session in the sidebar.
   - Click any past activity to inspect original inputs and re-render full generated outputs.
   - Download past outputs as Markdown files.
   - One-click **Clear History** with user confirmation.

5. **🎨 Modern & Responsive Design**
   - Custom AI + Book vector logo, subtle gradients, and glassmorphic cards.
   - Fluid button hover animations, clean typography, and a custom pulse loading animation.
   - Responsive layout optimized for both desktop and mobile screens.

6. **🔒 Secure Credential Management**
   - Supports Google Gemini and OpenAI.
   - Masked inputs, environment variable auto-loading via `python-dotenv`, zero hardcoded keys.

---

## 📁 Project Structure

```text
AI_Study_Assistant_Agent/
├── app.py              # Modern Streamlit Web UI with Workspace, History, and custom styling
├── agent.py            # AI Agent Controller, task routing, persona prompts, and LLM handlers
├── requirements.txt    # Project Python dependencies
├── .env.example        # Template for API keys (never commit real keys)
├── .gitignore          # Git ignore rules for virtual environments, secrets, and cache
└── README.md           # Documentation and setup guide
```

---

## ⚙️ Setup and Installation Guide

### Prerequisites
- Python 3.9 or higher.
- An API key for **Google Gemini** (from [Google AI Studio](https://aistudio.google.com/)) or **OpenAI**.

### Step 1: Open Terminal / PowerShell
```powershell
cd c:\Users\aksha\OneDrive\Desktop\AI_Study_Assistant_Agent
```

### Step 2: (Recommended) Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure API Key (Optional)
Copy `.env.example` to `.env` and paste your key:
```powershell
copy .env.example .env
```
*(Alternatively, enter your API key directly in the sidebar during runtime.)*

### Step 5: Launch the Application
```powershell
streamlit run app.py
```
Open `http://localhost:8501` in your browser.
