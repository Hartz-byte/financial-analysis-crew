# main.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from datetime import datetime
from crew import create_financial_crew
from config import REPORTS_DIR
import os

def analyze_stock(stock_symbol: str):
    """
    Main function to analyze a stock using the financial crew.
    
    Args:
        stock_symbol (str): Stock ticker symbol (e.g., 'AAPL')
    """
    
    print("\n" + "="*80)
    print(f"🚀 STARTING FINANCIAL ANALYSIS FOR {stock_symbol.upper()}")
    print("="*80 + "\n")
    
    try:
        # Create the crew
        crew = create_financial_crew(stock_symbol.upper())
        
        # Prepare inputs for the crew
        inputs = {
            "stock_symbol": stock_symbol.upper(),
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        }
        
        print(f"📊 Analyzing {stock_symbol.upper()}...")
        print("⏳ This may take 3-5 minutes...\n")
        
        # Run the crew
        result = crew.kickoff(inputs=inputs)
        
        # Save results
        report_filename = os.path.join(
            REPORTS_DIR,
            f"{stock_symbol.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_filename, 'w') as f:
            json.dump({
                "symbol": stock_symbol.upper(),
                "analysis_date": datetime.now().isoformat(),
                "report": str(result),
            }, f, indent=2)
        
        # Print results
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE")
        print("="*80)
        print(f"\n{result}\n")
        print(f"\n📁 Report saved to: {report_filename}")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Ensure Ollama is running: `ollama serve` in another terminal")
        print("2. Check your API keys in .env file")
        print("3. Verify internet connection for financial data APIs")
        sys.exit(1)

def main():
    """Main entry point"""
    
    print("\n" + "="*80)
    print("💰 CREWAI FINANCIAL ANALYSIS SYSTEM")
    print("="*80)
    
    if len(sys.argv) > 1:
        stock_symbol = sys.argv[1].upper()
    else:
        stock_symbol = input("\n📌 Enter stock symbol (e.g., AAPL, GOOGL, MSFT): ").strip().upper()
    
    if not stock_symbol:
        print("❌ No stock symbol provided!")
        sys.exit(1)
    
    analyze_stock(stock_symbol)

if __name__ == "__main__":
    main()
