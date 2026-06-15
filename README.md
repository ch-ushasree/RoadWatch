# 🛣️ RoadWatch AI

AI-powered chatbot that helps citizens monitor road quality, track public spending, and report issues to responsible authorities.

🌐 Live Demo: https://roadwatch-5n7qolkwwpauhertua6bbm.streamlit.app/

## Features
- 💬 AI chatbot to query road conditions, budgets, and contractors
- 📷 Photo upload — AI assesses damage and drafts complaint automatically
- 📊 Accountability score — tracks budget spent vs road condition
- 📧 Auto-drafted complaint emails to the correct officer

## Setup

1. Clone the repository
```bash
   git clone https://github.com/ch-ushasree/roadwatch.git
   cd roadwatch
```

2. Create virtual environment
```bash
   python -m venv venv
   venv\Scripts\activate
```

3. Install dependencies
```bash
   pip install -r requirements.txt
```

4. Add your Groq API key (free at https://groq.com)
```bash
   cp .env.example .env
   # Edit .env and paste your key
```

5. Run the app
```bash
   streamlit run app.py
```

## Stack
- **LLM**: Llama 3.3 70B via Groq API (free, open model)
- **Vision**: Llama 4 Scout via Groq (photo analysis)
- **Backend**: Python + SQLite
- **Frontend**: Streamlit

## Data Sources
- GHMC public records
- NHAI / OMMS project data
- State PWD Telangana
