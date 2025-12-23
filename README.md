# 🏦 AI Financial Analysis Crew

**An intelligent, multi-agent financial analysis system powered by CrewAI, Ollama, and React.**

This application uses a team of autonomous AI agents to research, analyze, and report on stock market data. It runs completely locally using Docker and Ollama, ensuring privacy and control.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)
![Docker](https://img.shields.io/badge/docker-compose-blue.svg)

---

## 🚀 Features

-   **Multi-Agent Workflow**: Orchestrates specialized agents for different tasks:
    -   🕵️ **Market Researcher**: Gathers news, price data, and general company info.
    -   📈 **Technical Analyst**: Analyzes price action, RSI, Moving Averages, and Support/Resistance.
    -   💰 **Fundamental Specialist**: Evaluates financial health, P/E ratios, and valuation metrics.
    -   👔 **Portfolio Manager**: Synthesizes all data into a final investment recommendation (Buy/Sell/Hold).
-   **Local LLM Inference**: Built to run with [Ollama](https://ollama.com/), keeping all analysis local and free of API costs.
-   **Modern UI**: A sleek React (Vite) frontend with real-time progress tracking and professional report formatting.
-   **Dockerized**: One-click setup using Docker Compose.

---

## 🛠️ Architecture

The system is composed of two main services:

1.  **Backend (Python/FastAPI)**:
    -   Hosts the CrewAI agents.
    -   Exposes API endpoints to start analysis and retrieve status.
    -   Tools include: `yfinance` for data, `BeautifulSoup` for scraping, and custom calculators.

2.  **Frontend (React/TypeScript)**:
    -   Provides an interactive dashboard.
    -   Polls the backend for real-time updates.
    -   Renders Markdown reports with financial document styling.

---

## 📋 Prerequisites

Before you start, ensure you have the following installed:

1.  **Docker Desktop**: [Download Here](https://www.docker.com/products/docker-desktop/)
2.  **Ollama**: [Download Here](https://ollama.com/)
    -   You MUST have Ollama running on your host machine.
    -   Pull the model you intend to use (default is `llama3.1`):
        ```bash
        ollama pull llama3.1
        ```

---

## ⚡ Quick Start

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd financial-analysis-crew
    ```

2.  **Configure Environment**:
    -   Create a `.env` file in the root directory (see `.env.example` if available, or just create one):
    ```env
    # Optional API Keys (if you enable paid tools later)
    # SERPER_API_KEY=...
    
    # LLM Configuration (Defaults work for local Ollama)
    OLLAMA_BASE_URL=http://host.docker.internal:11434
    OLLAMA_MODEL=llama3.1
    ```

3.  **Run the Application**:
    -   **Windows**: Double-click `run_app.bat`.
    -   **Terminal**:
        ```bash
        docker-compose up --build
        ```

4.  **Access the Dashboard**:
    -   Open your browser to: [http://localhost:5173](http://localhost:5173)

---

## 🎮 Usage

1.  **Enter Symbol**: Type a stock ticker (e.g., `AAPL`, `NVDA`, `TSLA`) in the search bar.
2.  **Analyze**: Click the "Analyze" button.
3.  **Watch Agents Work**:
    -   You'll see the status change as agents pick up tasks.
    -   Real-time logs can be viewed in your terminal.
4.  **View Report**:
    -   Once complete, a comprehensive report will appear.
    -   Key metrics (RSI, P/E, Recommendation) are highlighted at the top.
    -   A detailed Markdown report follows below.

---

## 🔧 Troubleshooting

-   **"Connection Refused" to Ollama**:
    -   Ensure Ollama is running (`ollama serve`).
    -   The Docker container connects via `host.docker.internal`. If you are on Linux, you might need to add `--add-host=host.docker.internal:host-gateway` to the docker-compose command (already handled in our config for most cases).

-   **Build Errors**:
    -   Try cleaning up docker: `docker-compose down -v` and then rebuild.

---

## 📦 Project Structure

```
financial-analysis-crew/
├── agents.py                 # CrewAI Agent definitions
├── tasks.py                  # Task definitions for each agent
├── main.py                   # FastAPI application entry point
├── config.py                 # Configuration settings
├── docker-compose.yml        # Orchestration
├── run_app.bat               # Windows startup script
├── tools/                    # Custom Python tools
│   ├── financial_tools.py    # yfinance wrappers
│   └── analysis_tools.py     # Math and formatting tools
├── frontend/                 # React Application
│   ├── src/                  # Source code
│   └── Dockerfile            # Frontend build instructions
└── requirements-docker.txt   # Backend dependencies
```

---

## 🛡️ Disclaimer

This tool is for **educational and research purposes only**. It does not constitute financial advice. Always verify information and consult with a qualified financial advisor before making investment decisions.
