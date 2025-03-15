# app.py - Main Flask application
from flask import Flask, render_template, request, jsonify
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MSCI ETF tickers and names
ETF_OPTIONS = {
    "IWDA.L": "iShares Core MSCI World UCITS ETF",
    "EMIM.L": "iShares Core MSCI Emerging Markets IMI UCITS ETF",
    "EIMI.L": "iShares Core MSCI EM IMI UCITS ETF USD",
    "SWDA.L": "iShares Core MSCI World UCITS ETF USD",
    "LCWD.L": "SPDR MSCI World UCITS ETF",
    "MXWO.L": "iShares MSCI World ETF"
}

# Function to fetch ETF data
def fetch_etf_data(ticker, period="5y", interval="1wk"):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            return None
        
        # Convert index to string dates for JSON serialization
        data.index = data.index.strftime('%Y-%m-%d')
        
        # Calculate moving averages
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# Function to calculate moving average
def calculate_ma(data, ma_length):
    if data is None or data.empty:
        return None
    
    df = data.copy()
    df['MA'] = df['Close'].rolling(window=ma_length).mean()
    return df

# Function to perform investment simulation
def simulate_investment(etf_data, cash_data, investment_amount, start_date, frequency_months, ma_length, use_ma_strategy):
    if etf_data is None or etf_data.empty:
        return None
    
    df = etf_data.copy()
    df.index = pd.to_datetime(df.index)
    
    # Convert cash data if available
    if cash_data is not None:
        cash_df = cash_data.copy()
        cash_df.index = pd.to_datetime(cash_df.index)
    
    # Sort by date
    df = df.sort_index()
    
    # Calculate moving average if using strategy
    if use_ma_strategy:
        df['MA'] = df['Close'].rolling(window=ma_length).mean()
    
    # Initialize investment tracking
    results = []
    total_investment = 0
    total_shares = 0
    cash_balance = 0
    
    # Start date for investments
    current_date = pd.to_datetime(start_date)
    end_date = df.index.max()
    
    while current_date <= end_date:
        # Find the closest trading day (week)
        investment_date = df.index[df.index >= current_date].min()
        if pd.isna(investment_date):
            break
            
        price = df.loc[investment_date, 'Close']
        
        # Check if we should invest in ETF or cash
        invest_in_etf = True
        if use_ma_strategy:
            ma_value = df.loc[investment_date, 'MA']
            if not pd.isna(ma_value):
                invest_in_etf = price > ma_value
        
        if invest_in_etf:
            # Calculate shares to buy
            shares_to_buy = investment_amount / price
            total_shares += shares_to_buy
            
            results.append({
                'date': investment_date.strftime('%Y-%m-%d'),
                'price': price,
                'investment': investment_amount,
                'shares_bought': shares_to_buy,
                'total_shares': total_shares,
                'portfolio_value': total_shares * price,
                'total_invested': total_investment + investment_amount,
                'cash_balance': cash_balance,
                'total_value': (total_shares * price) + cash_balance
            })
        else:
            # Keep as cash
            cash_balance += investment_amount
            
            results.append({
                'date': investment_date.strftime('%Y-%m-%d'),
                'price': price,
                'investment': investment_amount,
                'shares_bought': 0,
                'total_shares': total_shares,
                'portfolio_value': total_shares * price,
                'total_invested': total_investment + investment_amount,
                'cash_balance': cash_balance,
                'total_value': (total_shares * price) + cash_balance
            })
        
        total_investment += investment_amount
        
        # Move to next investment date
        current_date = current_date + pd.DateOffset(months=frequency_months)
    
    # Also calculate final portfolio value at each historical date
    portfolio_history = []
    for date, row in df.iterrows():
        # Find the last investment before this date
        last_investment = None
        for inv in results:
            inv_date = pd.to_datetime(inv['date'])
            if inv_date <= date:
                last_investment = inv
            else:
                break
                
        if last_investment:
            portfolio_history.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': row['Close'],
                'portfolio_value': last_investment['total_shares'] * row['Close'] + last_investment['cash_balance'],
                'total_invested': last_investment['total_invested']
            })
    
    return {
        'investments': results,
        'history': portfolio_history
    }

@app.route('/')
def index():
    return render_template('index.html', etf_options=ETF_OPTIONS)

@app.route('/fetch_etf_data', methods=['POST'])
def get_etf_data():
    ticker = request.json.get('ticker')
    ma_length = int(request.json.get('ma_length', 10))
    
    data = fetch_etf_data(ticker)
    if data is None:
        return jsonify({'error': 'Failed to fetch ETF data'}), 500
    
    # Calculate moving average
    data_with_ma = calculate_ma(data, ma_length)
    if data_with_ma is None:
        return jsonify({'error': 'Failed to calculate moving average'}), 500
    
    # Convert to dictionary for JSON response
    result = {
        'dates': data_with_ma.index.tolist(),
        'open': data_with_ma['Open'].tolist(),
        'high': data_with_ma['High'].tolist(),
        'low': data_with_ma['Low'].tolist(),
        'close': data_with_ma['Close'].tolist(),
        'volume': data_with_ma['Volume'].tolist(),
        'ma': data_with_ma['MA'].tolist()
    }
    
    return jsonify(result)

@app.route('/simulate', methods=['POST'])
def run_simulation():
    # Get parameters from request
    ticker = request.json.get('ticker')
    investment_amount = float(request.json.get('investment_amount', 100))
    start_date = request.json.get('start_date', '2018-01-01')
    frequency_months = int(request.json.get('frequency_months', 1))
    ma_length = int(request.json.get('ma_length', 10))
    use_ma_strategy = request.json.get('use_ma_strategy', False)
    
    # Fetch ETF data
    etf_data = fetch_etf_data(ticker)
    if etf_data is None:
        return jsonify({'error': f'Failed to fetch data for {ticker}'}), 500
    
    # Calculate moving average
    etf_data = calculate_ma(etf_data, ma_length)
    
    # Fetch cash rate data (placeholder - in real app, get from ECB API)
    cash_data = None  # In a real app, implement ECB rate fetching
    
    # Run simulation
    simulation_results = simulate_investment(
        etf_data, 
        cash_data,
        investment_amount, 
        start_date, 
        frequency_months, 
        ma_length, 
        use_ma_strategy
    )
    
    if simulation_results is None:
        return jsonify({'error': 'Failed to run simulation'}), 500
    
    return jsonify(simulation_results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
