# crew.py
from crewai import Crew, Process
from agents import (
    market_researcher,
    technical_analyst,
    fundamental_analyst,
    portfolio_manager
)
from tasks import create_tasks

def create_financial_crew(stock_symbol: str) -> Crew:
    """Create and configure the financial analysis crew"""
    
    tasks = create_tasks(stock_symbol)
    
    crew = Crew(
        agents=[
            market_researcher,
            technical_analyst,
            fundamental_analyst,
            portfolio_manager,
        ],
        tasks=tasks,
        process=Process.sequential,  # Tasks run one after another
        verbose=True,
        memory=False,  # Disabled to avoid OpenAI embedding requirement
        max_rpm=100,  # Rate limiting
    )
    
    return crew
