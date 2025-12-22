# tools/financial_tools.py
import requests
import json
import os
import pickle
from datetime import datetime, timedelta
from crewai.tools import tool

from config import ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY, CACHE_DIR
import time
import pandas as pd

# Create Cache Dir if not exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_cache_path(symbol, data_type):
    return os.path.join(CACHE_DIR, f"{symbol}_{data_type}.pkl")

def load_cache(symbol, data_type, validity_hours=24):
    try:
        path = get_cache_path(symbol, data_type)
        if os.path.exists(path):
            modified_time = datetime.fromtimestamp(os.path.getmtime(path))
            if datetime.now() - modified_time < timedelta(hours=validity_hours):
                with open(path, 'rb') as f:
                    return pickle.load(f)
    except Exception:
        pass
    return None

def save_cache(symbol, data_type, data):
    try:
        path = get_cache_path(symbol, data_type)
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    except Exception:
        pass

# ============= CORE LOGIC FUNCTIONS (Non-Tools) =============

def _fetch_finnhub_price(symbol):
    """Fetch real-time quote from Finnhub"""
    if not FINNHUB_API_KEY: return None
    headers = {'User-Agent': 'Mozilla/5.0'}
    for i in range(3):
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get('c', 0) == 0 and data.get('pc', 0) == 0: return None
                return {
                    'currentPrice': data['c'],
                    'previousClose': data['pc'],
                    'open': data['o'],
                    'high': data['h'],
                    'low': data['l'],
                    'change': data['d'],
                    'changePercent': data['dp']
                }
            if r.status_code == 429: time.sleep(2)
        except Exception:
            time.sleep(1)
    return None

def _fetch_finnhub_history(symbol, resolution='D', count=100):
    """Fetch candles from Finnhub"""
    if not FINNHUB_API_KEY: return None
    cache_key = f"history_finnhub_{resolution}_{count}"
    cached = load_cache(symbol, cache_key)
    if cached is not None: return cached

    headers = {'User-Agent': 'Mozilla/5.0'}
    for i in range(3):
        try:
            end = int(time.time())
            start = end - (count * 86400 * (1 if resolution=='D' else 7)) 
            
            url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution={resolution}&from={start}&to={end}&token={FINNHUB_API_KEY}"
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get('s') == 'ok':
                    df = pd.DataFrame({
                        'Open': data['o'],
                        'High': data['h'],
                        'Low': data['l'],
                        'Close': data['c'],
                        'Volume': data['v'],
                        'Date': [datetime.fromtimestamp(ts) for ts in data['t']]
                    })
                    df.set_index('Date', inplace=True)
                    save_cache(symbol, cache_key, df)
                    return df
            if r.status_code == 429: time.sleep(2)
        except Exception:
            time.sleep(1)
    return None

def _fetch_av_overview(symbol):
    """Fetch Company Overview from Alpha Vantage"""
    if not ALPHA_VANTAGE_API_KEY: return None
    cached = load_cache(symbol, "av_overview", validity_hours=168)
    if cached: return cached

    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if "Symbol" in data:
                save_cache(symbol, "av_overview", data)
                return data
    except Exception:
        pass
    return None

def _fetch_av_history(symbol):
    """Fetch Daily History from Alpha Vantage (Fallback)"""
    if not ALPHA_VANTAGE_API_KEY: return None
    cached = load_cache(symbol, "av_history_daily")
    if cached is not None: return cached
    
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            ts = data.get("Time Series (Daily)", {})
            if not ts: return None
            
            records = []
            for date_str, values in ts.items():
                records.append({
                    'Date': datetime.strptime(date_str, "%Y-%m-%d"),
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': float(values['5. volume'])
                })
            df = pd.DataFrame(records)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            save_cache(symbol, "av_history_daily", df)
            return df
    except Exception:
        pass
    return None

def _get_hybrid_history(symbol, days):
    """Helper to get history from Finnhub or AV"""
    hist = _fetch_finnhub_history(symbol, count=days)
    if hist is None or hist.empty:
        hist = _fetch_av_history(symbol)
        if hist is not None and not hist.empty:
            hist = hist.tail(days)
    return hist

# Logic Wrappers for Output Formatting
def _logic_fetch_news(symbol):
    try:
        if not FINNHUB_API_KEY: return "Finnhub API key missing."
        url = f"https://finnhub.io/api/v1/company-news"
        params = {
            "symbol": symbol,
            "from": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            "to": datetime.now().strftime('%Y-%m-%d'),
            "token": FINNHUB_API_KEY
        }
        headers = {'User-Agent': 'Mozilla/5.0'}
        for i in range(3):
            try:
                r = requests.get(url, params=params, headers=headers, timeout=10)
                if r.status_code == 200:
                    news = r.json()
                    summary = f"{symbol} - Latest News:\n"
                    # Limit to 5
                    for a in news[:5]:
                        headline = a.get('headline')
                        dt = a.get('datetime')
                        summary += f"- {headline} ({dt})\n"
                    return summary
                time.sleep(1)
            except: time.sleep(1)
        return "Failed to fetch news."
    except Exception as e:
        return f"Error: {str(e)}"

def _logic_get_company_info(symbol):
    try:
        data = _fetch_av_overview(symbol)
        if not data:
             return f"Error: Could not fetch company info for {symbol}"
        
        return f"""
        {data.get('Name', symbol)} ({data.get('Symbol', symbol)})
        
        Sector: {data.get('Sector', 'N/A')}
        Industry: {data.get('Industry', 'N/A')}
        
        Description:
        {data.get('Description', 'N/A')}
        """
    except Exception as e:
        return f"Error fetching company info for {symbol}: {str(e)}"

def _logic_fetch_stock_price(symbol):
    try:
        price_data = _fetch_finnhub_price(symbol)
        av_data = _fetch_av_overview(symbol) or {}
        market_cap = av_data.get('MarketCapitalization', 'N/A')
        if market_cap != 'N/A' and market_cap.isdigit():
            market_cap = f"${int(market_cap):,}"
        
        if not price_data:
            # Fallback to AV last close if needed? No, AV only has historical.
            return f"Error: Could not fetch stock price for {symbol} (Finnhub)"

        return f"""
        Stock: {symbol}
        Current Price: ${price_data['currentPrice']:.2f}
        Day Change: ${price_data['change']:.2f} ({price_data['changePercent']:.2f}%)
        Market Cap: {market_cap}
        High: ${price_data['high']:.2f}
        Low: ${price_data['low']:.2f}
        """
    except Exception as e:
        return f"Error fetching stock price for {symbol}: {str(e)}"

# ============= TOOLS IMPLEMENTATION =============

@tool("fetch_stock_price")
def fetch_stock_price(symbol: str) -> str:
    """Fetch current stock price and basic info."""
    return _logic_fetch_stock_price(symbol)

@tool("fetch_stock_history")
def fetch_stock_history(symbol: str, period: str = "3mo") -> str:
    """Fetch historical stock price data."""
    try:
        days = 90
        if period == '1mo': days = 30
        if period == '1y': days = 365
        
        # Increase buffer for 1y to ensure ample data points
        hist = _get_hybrid_history(symbol, days + 10) 
        
        if hist is None or hist.empty:
            return f"No historical data for {symbol}"
        
        high = hist['High'].max()
        low = hist['Low'].min()
        avg_close = hist['Close'].mean()
        recent_close = hist['Close'].iloc[-1]
        
        if hasattr(high, 'item'): high = high.item()
        if hasattr(low, 'item'): low = low.item()
        if hasattr(avg_close, 'item'): avg_close = avg_close.item()
        if hasattr(recent_close, 'item'): recent_close = recent_close.item()
        
        return f"""
        {symbol} - {period} History:
        Highest: ${high:.2f}
        Lowest: ${low:.2f}
        Average Close: ${avg_close:.2f}
        Recent Close: ${recent_close:.2f}
        """
    except Exception as e:
        return f"Error fetching history for {symbol}: {str(e)}"

@tool("fetch_fundamentals")
def fetch_fundamentals(symbol: str) -> str:
    """Fetch fundamental financial data."""
    try:
        data = _fetch_av_overview(symbol)
        if not data:
            return f"Error: Could not fetch fundamentals for {symbol}"
        
        return f"""
        {symbol} - Fundamentals:
        P/E Ratio: {data.get('PERatio', 'N/A')}
        P/B Ratio: {data.get('PriceToBookRatio', 'N/A')}
        Dividend Yield: {data.get('DividendYield', 'N/A')}
        EPS: {data.get('EPS', 'N/A')}
        Revenue (TTM): ${int(data.get('RevenueTTM', 0)):,}
        Profit Margin: {data.get('ProfitMargin', 'N/A')}
        Building Sector: {data.get('Sector', 'N/A')}
        """
    except Exception as e:
        return f"Error fetching fundamentals for {symbol}: {str(e)}"

@tool("calculate_moving_averages")
def calculate_moving_averages(symbol: str) -> str:
    """Calculate moving averages."""
    try:
        # Increase count to 400 to ensure 200MA has enough data
        hist = _get_hybrid_history(symbol, 400)
        
        if hist is None or hist.empty:
            return f"Error: Could not fetch historical data for {symbol}"

        closes = hist['Close']
        current = closes.iloc[-1]
        
        ma20 = closes.rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else 0
        ma50 = closes.rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else 0
        ma200 = closes.rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else 0
        
        if hasattr(ma20, 'item'): ma20 = ma20.item()
        if hasattr(ma50, 'item'): ma50 = ma50.item()
        if hasattr(ma200, 'item'): ma200 = ma200.item()
        if hasattr(current, 'item'): current = current.item()

        return f"""
        {symbol} - Moving Averages:
        Current Price: ${current:.2f}
        20-Day MA: ${ma20:.2f}
        50-Day MA: ${ma50:.2f}
        200-Day MA: ${ma200:.2f}
        """
    except Exception as e:
        return f"Error calculating MAs for {symbol}: {str(e)}"

@tool("calculate_rsi")
def calculate_rsi(symbol: str, period: int = 14) -> str:
    """Calculate RSI."""
    try:
        hist = _get_hybrid_history(symbol, 90)

        if hist is None or hist.empty: return "Error: No data"

        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        # Handle case where all are NaN at start
        current_rsi = rsi.iloc[-1]
        if hasattr(current_rsi, 'item'): current_rsi = current_rsi.item()
        
        return f"""
        {symbol} - RSI ({period}-period):
        Current RSI: {current_rsi:.2f}
        """
    except Exception as e:
        return f"Error calculating RSI: {str(e)}"

@tool("calculate_support_resistance")
def calculate_support_resistance(symbol: str) -> str:
    """Identify support and resistance levels."""
    try:
        hist = _get_hybrid_history(symbol, 365)
        if hist is None or hist.empty:
            return f"Error: No data for {symbol}"
        
        current = hist['Close'].iloc[-1]
        if hasattr(current, 'item'): current = current.item()
        
        window = hist.tail(90)
        resistance = window['High'].max()
        support = window['Low'].min()
        
        if hasattr(resistance, 'item'): resistance = resistance.item()
        if hasattr(support, 'item'): support = support.item()
        
        return f"""
        {symbol} - Support & Resistance (90-day):
        Current Price: ${current:.2f}
        Resistance (High): ${resistance:.2f}
        Support (Low): ${support:.2f}
        
        Trading Range: ${support:.2f} - ${resistance:.2f}
        """
    except Exception as e:
         return f"Error: {e}"

@tool("get_company_info")
def get_company_info(symbol: str) -> str:
    """Get company info."""
    return _logic_get_company_info(symbol)

@tool("fetch_latest_news")
def fetch_latest_news(symbol: str) -> str:
    """Fetch news."""
    return _logic_fetch_news(symbol)

@tool("fetch_market_summary")
def fetch_market_summary(symbol: str) -> str:
    """
    Fetch comprehensive market data including news, company info, and price.
    Returns: Combined report to update all data at once.
    """
    try:
        # Calls pure functions, NOT tool objects
        news = _logic_fetch_news(symbol)
        info = _logic_get_company_info(symbol)
        price = _logic_fetch_stock_price(symbol)
        
        return f"""
        === MARKET SUMMARY FOR {symbol} ===
        
        {info}
        
        {price}
        
        {news}
        """
    except Exception as e:
        return f"Error fetching market summary: {e}"

@tool("compare_stocks")
def compare_stocks(symbols: str) -> str:
    """Compare multiple stocks."""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        res = "Stock Comparison:\nSymbol | Price | Change | PE Ratio\n"
        
        for sym in symbol_list:
            price_data = _fetch_finnhub_price(sym)
            av_data = _fetch_av_overview(sym)
            
            p = price_data['currentPrice'] if price_data else 0
            c = price_data['changePercent'] if price_data else 0
            pe = av_data.get('PERatio', 'N/A') if av_data else 'N/A'
            
            res += f"{sym:<6} | ${p:<6.2f} | {c:<6.2f}% | {pe}\n"
        return res
    except Exception as e:
        return f"Error: {str(e)}"
