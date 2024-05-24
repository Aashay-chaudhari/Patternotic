from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import StandardScaler
# from functions.getTickers import fetch_stock_data  # Import the function
import csv
import os
import yfinance as yf
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

us_stocks = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'FB', 'NVDA', 'NFLX', 'ADBE', 'ORCL', 'INTC', 'CSCO', 'IBM', 'AMD', 'QCOM', 'TXN', 'AVGO', 'MU', 'CRM', 'PYPL']
nse_stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "HDFC.NS", "BHARTIARTL.NS", "ITC.NS", "BAJFINANCE.NS", "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "ULTRACEMCO.NS", "M&M.NS", "WIPRO.NS"]

stock_array = [us_stocks, nse_stocks]

# Cache dictionary to store fetched stock data
stock_cache = {}

# Scheduler setup
scheduler = BackgroundScheduler()
timezone_us = pytz.timezone('America/New_York')
timezone_nse = pytz.timezone('Asia/Kolkata')

# Load the saved model
model = load_model('models/stock_price_prediction_model.h5')
model.compile(optimizer='adam', loss='mean_squared_error')

def get_ltp(ticker):
    ticker_data = yf.Ticker(ticker)
    ltp = ticker_data.info['currentPrice']
    return ltp

def ensure_headers(file_path, headers):
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

# Ensure headers for all trade files
trade_headers = ['ticker', 'predictedClose', 'lastClosePrice', 'positionType', 'entryPrice', 'closePrice', 'profit', 'date']
ensure_headers('nse_daily_user_trades.csv', trade_headers)
ensure_headers('us_daily_user_trades.csv', trade_headers)
ensure_headers('nse_user_trades.csv', trade_headers)
ensure_headers('us_user_trades.csv', trade_headers)
ensure_headers('nse_daily_bot_trades.csv', trade_headers)
ensure_headers('us_daily_bot_trades.csv', trade_headers)
ensure_headers('nse_bot_trades.csv', trade_headers)
ensure_headers('us_bot_trades.csv', trade_headers)





def get_date_in_timezone(timezone):
    return datetime.now(timezone).strftime('%Y-%m-%d')

# Function to prepare the data
def prepare_data(data):
    scaler = StandardScaler()
    scaler_close = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    _ = scaler_close.fit_transform(pd.DataFrame(data['Close']))
    return scaled_data, scaler_close, scaler

# Function to scale and predictions
def make_predictions(model, data, ticker):
    ltp = get_ltp(ticker)
    prepared_data, scaler_close, scaler = prepare_data(data)
    prepared_data = prepared_data.reshape((1, prepared_data.shape[0], prepared_data.shape[1]))
    prediction = model.predict(prepared_data)
    prediction = scaler_close.inverse_transform(prediction)
    return prediction, ltp

def fetch_stock_data(tickers):
    print("Inside fetch_stock_data")
    feature_columns = ['Close', 'Open', 'High', 'Low', 'Volume']
    data_dict = {}
    for ticker in tickers:
        data = yf.download(ticker)
        # Drop rows with NaN values
        feature_data = data[feature_columns].copy()
        feature_data.dropna(inplace=True)
        data_dict[ticker] = feature_data[-30:]

    return data_dict

@app.route('/data', methods=['POST'])
def get_data():
    request_data = request.get_json()
    tickers = request_data.get('stocks', [])
    market = request_data.get('market', '')
    if market == 'NSE':
        current_date = get_date_in_timezone(timezone_nse)
    else:
        current_date = get_date_in_timezone(timezone_us)

    cache_key = f"{current_date}_{market}"
    print("cache key is: ", cache_key)

    if cache_key in stock_cache:
        print("returning data dict from cache")
        data_dict = stock_cache[cache_key]
    else:
        data_dict = fetch_stock_data(tickers)
        stock_cache[cache_key] = data_dict
    
    if tickers:
        predictions = []
        for key, data in data_dict.items():
            if data.shape[0] == 0:
                continue

            prediction, ltp = make_predictions(model, data[-30:], key)
            prediction_tup = (key, prediction.flatten().tolist(), ltp)
            predictions.append(prediction_tup)

        response_data = {
            "received_stocks": tickers,
            "message": "Stocks received successfully!",
            "predicted_close": predictions
        }
    else:
        response_data = {
            "message": "No tickers provided"
        }

    return jsonify(response_data)


def trade_helper(trade_file: str):
    if not os.path.exists(trade_file):
        return []

    trades = []
    with open(trade_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            trades.append(row)

    return trades

@app.route('/getTrades', methods=['POST'])
def get_trades():
    request_data = request.get_json()
    market = request_data.get('market', '')
    user = request_data.get('user', '')
    freq = request_data.get('freq', '')

    if market == 'NSE':
        if user == 'user':
            if freq == 'daily':
                trade_file = 'nse_daily_user_trades.csv'
            else:
                trade_file = 'nse_user_trades.csv'
        else:
            if freq == 'daily':
                trade_file = 'nse_daily_bot_trades.csv'
            else:
                trade_file = 'nse_bot_trades.csv'
    else:
        if user == 'user':
            if freq == 'daily':
                trade_file = 'us_daily_user_trades.csv'
            else:
                trade_file = 'us_user_trades.csv'
        else:
            if freq == 'daily':
                trade_file = 'us_daily_bot_trades.csv'
            else:
                trade_file = 'us_bot_trades.csv'

    trades = trade_helper(trade_file)
    return jsonify(trades)

@app.route('/trade', methods=['POST'])
def trade():
    request_data = request.get_json()
    trade_data = request_data.get('trade', [])
    market = request_data.get('market', '')

    if market == 'NSE':
        trade_file = 'nse_daily_user_trades.csv'
    else:
        trade_file = 'us_daily_user_trades.csv'

    ensure_headers(trade_file, trade_headers)

    with open(trade_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([trade_data['ticker'], trade_data['predictedClose'], trade_data['lastClosePrice'], trade_data['positionType'], '-', '-', '-', '-'])

    return jsonify({"message": "Trade saved successfully!"}), 200

def bot_trades_us():
    for stock_list, market in zip([us_stocks], ['us']):
        data_dict = fetch_stock_data(stock_list)
        
        if stock_list:
            predictions = []
            for key, data in data_dict.items():
                if data.shape[0] == 0:
                    continue
                prediction, ltp = make_predictions(model, data[-30:], key)
                position_type = 'Long' if prediction > ltp else 'Short'
                prediction_tup = [key, prediction.flatten().item(), ltp, position_type, '-', '-', '-', '-']
                predictions.append(prediction_tup)
                
                daily_trade_file = f'{market}_daily_bot_trades.csv'
                ensure_headers(daily_trade_file, trade_headers)
                with open(daily_trade_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(prediction_tup)

def bot_trades_nse():
    for stock_list, market in zip([nse_stocks], ['nse']):
        data_dict = fetch_stock_data(stock_list)
        
        if stock_list:
            predictions = []
            for key, data in data_dict.items():
                if data.shape[0] == 0:
                    continue
                prediction, ltp = make_predictions(model, data[-30:], key)
                position_type = 'Long' if prediction > ltp else 'Short'
                prediction_tup = [key, prediction.flatten().item(), ltp, position_type, '-', '-', '-', '-']
                predictions.append(prediction_tup)
                
                daily_trade_file = f'{market}_daily_bot_trades.csv'
                ensure_headers(daily_trade_file, trade_headers)
                with open(daily_trade_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(prediction_tup)

def update_entry_prices_nse():
    trade_files = ['nse_daily_bot_trades.csv', 'nse_daily_user_trades.csv']

    for trade_file in trade_files:
        if not os.path.exists(trade_file):
            continue

        trades = pd.read_csv(trade_file)
        for index, trade in trades.iterrows():
            ticker = trade['ticker']
            opening_price = get_ltp(ticker)
            trades.at[index, 'entryPrice'] = opening_price

        trades.to_csv(trade_file, index=False)
        ensure_headers(trade_file, trade_headers)

def update_entry_prices_us():
    trade_files = ['us_daily_bot_trades.csv', 'us_daily_user_trades.csv']

    for trade_file in trade_files:
        if not os.path.exists(trade_file):
            continue

        trades = pd.read_csv(trade_file)
        for index, trade in trades.iterrows():
            ticker = trade['ticker']
            opening_price = get_ltp(ticker)
            trades.at[index, 'entryPrice'] = opening_price

        trades.to_csv(trade_file, index=False)
        ensure_headers(trade_file, trade_headers)

def update_close_prices_and_profit_us():
    trade_files = ['us_daily_user_trades.csv', 'us_daily_bot_trades.csv']
    target_files = ['us_user_trades.csv', 'us_bot_trades.csv']

    for trade_file, target_file in zip(trade_files, target_files):
        if not os.path.exists(trade_file):
            continue

        trades = pd.read_csv(trade_file)
        if trades.empty:
            continue

        for index, trade in trades.iterrows():
            current_date = datetime.now().strftime('%Y-%m-%d')
            ticker = trade['ticker']
            closing_price = get_ltp(ticker)
            entry_price = trades.at[index, 'entryPrice']
            position_type = trades.at[index, 'positionType']
            
            if pd.isna(entry_price) or pd.isna(closing_price):
                continue
            
            entry_price = float(entry_price)
            closing_price = float(closing_price)
            
            if position_type == 'Long':
                profit = (closing_price - entry_price + 1) * 100 / entry_price
            else:
                profit = (entry_price - closing_price + 1) * 100 / entry_price
            
            trades.at[index, 'closePrice'] = closing_price
            trades.at[index, 'profit'] = profit
            trades.at[index, 'date'] = str(current_date)

        ensure_headers(target_file, trade_headers)

        with open(target_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(trades.values.tolist())
        
        trades.drop(trades.index, inplace=True)
        trades.to_csv(trade_file, index=False)
        ensure_headers(trade_file, trade_headers)

def update_close_prices_and_profit_nse():
    trade_files = ['nse_daily_user_trades.csv', 'nse_daily_bot_trades.csv']
    target_files = ['nse_user_trades.csv', 'nse_bot_trades.csv']

    for trade_file, target_file in zip(trade_files, target_files):
        if not os.path.exists(trade_file):
            continue

        trades = pd.read_csv(trade_file)
        if trades.empty:
            continue

        for index, trade in trades.iterrows():
            current_date = datetime.now().strftime('%Y-%m-%d')
            ticker = trade['ticker']
            closing_price = get_ltp(ticker)
            entry_price = trades.at[index, 'entryPrice']
            position_type = trades.at[index, 'positionType']
            
            if pd.isna(entry_price) or pd.isna(closing_price):
                continue
            
            entry_price = float(entry_price)
            closing_price = float(closing_price)
            
            if position_type == 'Long':
                profit = (closing_price - entry_price + 1) * 100 / entry_price
            else:
                profit = (entry_price - closing_price + 1) * 100 / entry_price
            
            trades.at[index, 'closePrice'] = closing_price
            trades.at[index, 'profit'] = profit
            trades.at[index, 'date'] = str(current_date)

        ensure_headers(target_file, trade_headers)

        with open(target_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(trades.values.tolist())
        
        trades.drop(trades.index, inplace=True)
        trades.to_csv(trade_file, index=False)
        ensure_headers(trade_file, trade_headers)



if __name__ == "__main__":
    scheduler.add_job(bot_trades_us, CronTrigger(day_of_week='mon-fri', hour=15, minute=30, timezone=timezone_us))
    scheduler.add_job(update_entry_prices_us, CronTrigger(day_of_week='mon-fri', hour=9, minute=31, timezone=timezone_us))
    scheduler.add_job(update_close_prices_and_profit_us, CronTrigger(day_of_week='mon-fri', hour=16, minute=0, timezone=timezone_us))

    scheduler.add_job(bot_trades_nse, CronTrigger(day_of_week='mon-fri', hour=15, minute=30, timezone=timezone_nse))
    scheduler.add_job(update_entry_prices_nse, CronTrigger(day_of_week='mon-fri', hour=9, minute=16, timezone=timezone_nse))
    scheduler.add_job(update_close_prices_and_profit_nse, CronTrigger(day_of_week='mon-fri', hour=15, minute=30, timezone=timezone_nse))

    scheduler.start()

    app.run(debug=True)
