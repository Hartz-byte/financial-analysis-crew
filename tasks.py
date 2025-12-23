# tasks.py
from crewai import Task
from agents import (
    market_researcher,
    technical_analyst,
    fundamental_analyst,
    portfolio_manager
)

def create_tasks(stock_symbol: str):
    """Create tasks for analyzing a stock"""
    
    # Task 1: Market Research
    market_research_task = Task(
        description=f"""
        Analyze the market sentiment and current status of {stock_symbol}.
        
        Research and provide:
        1. Latest news and recent events affecting {stock_symbol}
        2. Company overview and business model
        3. Current stock price and 7-day price movement
        4. Overall market sentiment (bullish/bearish)
        5. Industry trends and competitive position
        
        Be thorough and cite specific data points.
        """,
        expected_output=f"""
        Comprehensive market analysis for {stock_symbol} including:
        - Recent news summary (top 3-5 articles)
        - Company business description
        - Current market sentiment assessment
        - Industry position and competitive advantages
        - Risk factors from market perspective
        """,
        agent=market_researcher,
        async_execution=False,
    )
    
    # Task 2: Technical Analysis
    technical_analysis_task = Task(
        description=f"""
        Perform comprehensive technical analysis on {stock_symbol}.
        
        Analyze and provide:
        1. Price trend (1 month, 3 months, 1 year)
        2. Moving averages (20-day, 50-day, 200-day)
        3. RSI (Relative Strength Index)
        4. Support and resistance levels
        5. Buy/sell signals based on technical indicators
        6. Momentum and trend direction
        
        Identify clear buy, sell, or hold signals.
        """,
        expected_output=f"""
        Detailed technical analysis for {stock_symbol}:
        - Current trend direction and strength
        - Key support and resistance levels
        - Moving average analysis and positioning
        - RSI interpretation (overbought/oversold/neutral)
        - Clear technical signals (BUY/SELL/HOLD)
        - Price momentum assessment
        - Recommended entry/exit points
        """,
        agent=technical_analyst,
        async_execution=False,
    )
    
    # Task 3: Fundamental Analysis
    fundamental_analysis_task = Task(
        description=f"""
        Conduct deep fundamental analysis of {stock_symbol}.
        
        Analyze and evaluate:
        1. P/E ratio and valuation vs industry peers
        2. Profit margins and profitability trends
        3. Revenue growth and earnings quality
        4. Debt levels and financial health
        5. Cash position and capital allocation
        6. ROE (Return on Equity) and efficiency metrics
        7. Intrinsic value estimate
        
        Assess if the company is undervalued or overvalued.
        """,
        expected_output=f"""
        Comprehensive fundamental analysis for {stock_symbol}:
        - Valuation assessment (undervalued/fair/overvalued)
        - Key financial metrics and their trends
        - Profit margin and profitability analysis
        - Financial health and debt assessment
        - Growth prospects and sustainability
        - Comparison with industry peers
        - Intrinsic value estimate
        - Investment quality rating
        """,
        agent=fundamental_analyst,
        async_execution=False,
    )
    
    # Task 4: Portfolio Manager Synthesis
    synthesis_task = Task(
        description=f"""
        You are the Senior Portfolio Manager. Synthesize all research from your three analysts
        about {stock_symbol} into a single, clear investment recommendation.
        
        Integrate:
        1. Market sentiment and news analysis
        2. Technical signals and price action
        3. Fundamental valuation and financial health
        
        Provide:
        - Clear BUY/SELL/HOLD recommendation
        - Price target (6-12 month)
        - Risk assessment
        - Confidence level (0-100%)
        - Key catalysts that could move the stock
        - Position sizing recommendation
        
        Use the context from all three analysts' findings to make a confident decision.
        
        IMPORTANT: Your final action MUST be to call the `format_report` tool.
        You MUST provide ALL the following arguments:
        - `symbol`
        - `recommendation`
        - `price_target`
        - `confidence`
        - `current_price`
        - `rsi`
        - `pe_ratio` // Extract this from the Fundamental Analysis

        Example Tool Input:
        symbol: "NVDA"
        recommendation: "Buy"
        price_target: "$210"
        confidence: "85%"
        current_price: "$180.99"
        rsi: "51.29"
        pe_ratio: "44.8"
        
        CRITICAL: Your 'Final Answer' MUST be the exact raw string returned by this tool.
        Do NOT summarize it. Just return the tool output.
        """,
        expected_output="The exact string returned by the `format_report` tool.",
        agent=portfolio_manager,
        async_execution=False,
    )
    
    return [
        market_research_task,
        technical_analysis_task,
        fundamental_analysis_task,
        synthesis_task,
    ]
