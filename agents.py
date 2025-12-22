# agents.py
from crewai import Agent, LLM

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL
)
from tools.financial_tools import (
    fetch_stock_price,
    fetch_stock_history,
    fetch_fundamentals,
    fetch_latest_news,
    get_company_info,
    calculate_moving_averages,
    calculate_rsi,
    compare_stocks
)
from tools.analysis_tools import (
    calculate_valuation_metrics,
    assess_financial_health,
    generate_analysis_summary,
    format_report
)

# Initialize LLMs
# Initialize LLMs
ollama_llm = LLM(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.7,
)

gemini_llm = LLM(
    model=GEMINI_MODEL,
    api_key=GEMINI_API_KEY,
    temperature=0.7,
)

# ============= AGENT 1: MARKET RESEARCHER =============
market_researcher = Agent(
    role="Market Research Analyst",
    goal="Gather and analyze current market sentiment, recent news, and market conditions for stocks",
    backstory="""You are an expert market researcher with 15 years of experience in financial analysis.
    You specialize in gathering real-time market data, analyzing news sentiment, and understanding
    market trends. You provide clear, actionable insights about market conditions and investor sentiment.""",
    tools=[
        fetch_latest_news,
        get_company_info,
        fetch_stock_price,
        compare_stocks
    ],
    llm=ollama_llm,
    verbose=True,
    max_iter=5,
)

# ============= AGENT 2: TECHNICAL ANALYST =============
technical_analyst = Agent(
    role="Technical Analysis Expert",
    goal="Analyze price patterns, technical indicators, and chart formations to identify trading signals",
    backstory="""You are a seasoned technical analyst with deep expertise in chart patterns,
    moving averages, RSI, MACD, and other technical indicators. You excel at identifying trends,
    support/resistance levels, and momentum shifts. Your analysis is data-driven and precise.""",
    tools=[
        fetch_stock_history,
        calculate_moving_averages,
        calculate_rsi,
        fetch_stock_price,
    ],
    llm=ollama_llm,
    verbose=True,
    max_iter=5,
)

# ============= AGENT 3: FUNDAMENTAL ANALYST =============
fundamental_analyst = Agent(
    role="Fundamental Analysis Specialist",
    goal="Evaluate company financial health, valuation metrics, and intrinsic value",
    backstory="""You are a value investing expert with strong knowledge of financial statement analysis.
    You evaluate P/E ratios, P/B ratios, debt levels, profitability metrics, and growth potential.
    You compare companies within their industry and provide deep fundamental insights.""",
    tools=[
        fetch_fundamentals,
        calculate_valuation_metrics,
        assess_financial_health,
        get_company_info,
    ],
    llm=ollama_llm,
    verbose=True,
    max_iter=5,
)

# ============= AGENT 4: PORTFOLIO MANAGER (COORDINATOR) =============
portfolio_manager = Agent(
    role="Senior Portfolio Manager",
    goal="Synthesize all analysis into actionable investment recommendations with clear rationale",
    backstory="""You are a senior portfolio manager with 20+ years of experience managing billions.
    You excel at synthesizing technical, fundamental, and sentiment analysis into clear investment
    decisions. You balance risk/reward, consider multiple timeframes, and provide confident
    recommendations backed by strong reasoning. You're known for your pragmatic, data-driven approach.""",
    tools=[
        format_report,
        generate_analysis_summary,
        fetch_stock_price,
    ],
    llm=gemini_llm,  # Use Gemini for complex reasoning in final synthesis
    verbose=True,
    max_iter=8,
)
