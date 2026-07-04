# 🏃 Pace Tracker

**Running performance analysis web app** — analytics dashboard, interactive charts, automatic insights and AI-powered chatbot.

Built with Python, Streamlit, Pandas and Plotly.

<br>

<div align="center">

### 🔗 [**Open Live Demo →**](https://pace-tracker-2znkmjtmhpfwghywql9fq5.streamlit.app)

*No installation needed — runs in your browser.*

</div>

<br>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-6.8-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-3.0-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Development-00D4AA?style=for-the-badge)
![Tests](https://github.com/cauafdev/pace-tracker/actions/workflows/tests.yml/badge.svg)

---

## About

Pace Tracker started as a simple terminal pace calculator and has been progressively refactored into a full-featured web application with an analytics dashboard, interactive charts and AI integration.

**What this project demonstrates:**

- **Software engineering** — modular architecture, separation of concerns, progressive refactoring across versions, automated test suite with CI
- **Data analysis** — time-based aggregations, trend calculations, automatic insight generation with Pandas
- **Data visualization** — 10 interactive chart types with Plotly, dynamic KPIs, responsive layout
- **Web development** — modern Streamlit interface, custom dark theme, professional UI/UX design
- **AI integration** — hybrid chatbot combining regex-based routing, JSON knowledge base and local LLM (Ollama)

---

## Features

### 📊 Analytics Dashboard
- Real-time KPIs: total distance, runs, average pace, best pace, training streak
- 4 interactive charts: weekly mileage, pace evolution, cumulative distance and training frequency
- Recent activity table with formatted data

### ➕ Run Logging
- Form-based input with date, distance, time, run type and notes
- **Natural language input:** type `ran 10km in 50min` and the app parses it automatically
- Built-in pace and time calculator
- Auto-calculated pace on every submission

### 📈 Performance Analysis
- Mileage evolution — weekly, monthly and cumulative views
- Pace evolution with moving average trend line
- Pace vs distance scatter plot (colored by duration)
- Distance distribution histogram and run type breakdown
- Weekly and monthly summary tables
- Top performances ranking

### 🏁 Race Time Predictor
- Predicts finish times for 5K, 10K, half marathon and marathon from your best recorded pace
- Based on Riegel's exponential formula (T2 = T1 × (D2/D1)^1.06), a model used in sports science to project performance across distances
- Visualizes the predicted pacing curve with Plotly

### 💡 Automatic Insights
Engine that reads your data and generates findings like:
- *"Your weekly volume increased 32%"*
- *"Your pace improved from 5:40 to 5:12 min/km"*
- *"Your favorite training day is Tuesday"*
- *"Best month: June — 71 km in 7 runs"*
- Personalized recommendations based on your patterns

### 🤖 AI Chatbot
- Intelligent message router that classifies intent via regex
- Local knowledge base covering 10 running topics
- Ollama integration for open-ended conversations (local LLM, 100% offline)
- Log runs and query stats directly through chat

### 📚 Educational Content
- Running knowledge base with expert answers
- 10 detailed tips for runners (hydration, nutrition, injury prevention, etc.)
- Embedded training videos on technique, pacing and race preparation

---

## Architecture

```
pace-tracker/
│
├── app.py                      # Streamlit web application (UI + routing)
│
├── utils/
│   ├── data_manager.py         # Data I/O, JSON persistence, formatters
│   ├── analytics.py            # Analytics engine — metrics, trends, insights
│   └── charts.py               # Plotly chart generators (10 chart types)
│
├── router.py                   # Message intent classifier (regex patterns)
├── ai_client.py                # Ollama LLM client (local AI)
│
├── tests/                      # Pytest suite (router, analytics, data I/O, AI client)
├── .github/workflows/          # CI — runs the test suite on every push/PR
│
├── .streamlit/config.toml      # Custom dark theme configuration
├── conhecimento.json           # Knowledge base (10 running topics)
├── historico.json              # Run history (JSON persistence)
├── conversas.json              # Chatbot conversation log
└── requirements.txt
```

**Data flow:**

```
User → Streamlit UI → data_manager.py → historico.json
                            ↓
                      analytics.py → metrics, trends, insights
                            ↓
                       charts.py → interactive Plotly charts
```

**Chatbot message routing:**

```
User message
      │
  [router.py] ── classifies intent
      │
 ┌────┼───────────┼────────────┼───────────┐
 │              │            │              │
Calculation  Command    Knowledge     Conversation
 (regex)     (stats)     (JSON)       (Ollama AI)
 │              │            │              │
 └────────── Response to user ─────────────┘
```

---

## Project Evolution

This project was built incrementally. Each version introduced new concepts and technologies — the commit history reflects the real progression.

| Version | What changed | Skills added |
|---------|-------------|--------------|
| **v1.0** | Terminal pace calculator with input/print | Python fundamentals, user input validation |
| **v1.1** | Intelligent message router | Regex, intent classification, pattern matching |
| **v1.2** | Chatbot with JSON knowledge base | JSON data structures, keyword search, persistence |
| **v1.3** | Local AI integration via Ollama | REST API consumption, LLM integration, error handling |
| **v2.0** | **Full web app with Streamlit** | Streamlit, Pandas, Plotly, data analysis, UI/UX design |

---

## Testing

The core logic — intent routing, JSON persistence, analytics and the AI client — is covered by a pytest suite (59 tests), running automatically on every push via GitHub Actions.

```bash
pip install -r requirements-dev.txt
pytest -v
```

---

## Running Locally

```bash
# Clone
git clone https://github.com/cauafdev/pace-tracker.git
cd pace-tracker

# Install dependencies
pip install -r requirements.txt

# Start
streamlit run app.py
```

Opens at `http://localhost:8501`.

**Local AI (optional):**

```bash
# Install Ollama → https://ollama.ai
ollama pull llama3.2:1b
# Enable the AI toggle in the chatbot page
```

---

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python** | Core logic, data processing |
| **Streamlit** | Web framework, interactive UI |
| **Pandas** | Data manipulation, aggregation |
| **Plotly** | Interactive charts and visualizations |
| **JSON** | Lightweight data persistence |
| **Regex** | Natural language parsing |
| **Ollama** | Local LLM for AI chatbot (optional) |

---

## Author

**Cauã F.** — [@cauafdev](https://github.com/cauafdev)
