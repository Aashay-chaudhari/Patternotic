from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import StandardScaler
from functions.common_fn import fetch_stock_data, get_date_in_timezone, ensure_headers, get_ltp, get_model_from_str
from functions.scaling import get_predictions
import csv
import time
import os
import yfinance as yf
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
us_stocks = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 'ORCL', 'INTC', 'CSCO', 'IBM', 'AMD', 'QCOM', 'TXN', 'AVGO', 'MU', 'CRM', 'PYPL']
nse_stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "HDFC.NS", "BHARTIARTL.NS", "ITC.NS", "BAJFINANCE.NS", "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS", "ULTRACEMCO.NS", "M&M.NS", "WIPRO.NS"]

stock_array = [us_stocks, nse_stocks]

# Cache dictionary to store fetched stock data
stock_cache = {}

# Scheduler setup
scheduler = BackgroundScheduler()
timezone_us = pytz.timezone('America/New_York')
timezone_nse = pytz.timezone('Asia/Kolkata')

# Load the saved model
model1 = load_model('models/model1.h5')
model1.compile(optimizer='adam', loss='mean_squared_error')

model2 = load_model('models/model2.h5')
model2.compile(optimizer='adam', loss='mean_squared_error')

model3 = load_model('models/model3.h5')
model3.compile(optimizer='adam', loss='mean_squared_error')

# Ensure headers for all trade files
trade_headers = ['ticker', 'predictedClose', 'lastClosePrice', 'positionType', 'entryPrice', 'closePrice', 'profit', 'date']

model_str_list = ['model1', 'model2', 'model3']
model_list = [model1, model2, model3]


for model in model_str_list:
    ensure_headers(f'trade_data/{model}/nse_daily_user_trades.csv', trade_headers)
    ensure_headers(f'trade_data/{model}/us_daily_user_trades.csv', trade_headers)
    ensure_headers(f'trade_data/{model}/nse_user_trades.csv', trade_headers)
    ensure_headers(f'trade_data/{model}/us_user_trades.csv', trade_headers)
    ensure_headers(f'trade_data/{model}/nse_daily_bot_trades.csv', trade_headers)
    ensure_headers(f'trade_data/{model}/us_daily_bot_trades.csv', trade_headers)
    ensure_headers(f'trade_data/{model}/nse_bot_trades.csv', trade_headers)
    ensure_headers(f'trade_data/{model}/us_bot_trades.csv', trade_headers)


@app.route('/api/data', methods=['POST'])
def get_data():
    request_data = request.get_json()
    tickers = request_data.get('stocks', [])
    market = request_data.get('market', '')
    model_str = request_data.get('model', '')
    print("Inside get_data for model: ", model_str)
    model = get_model_from_str(model_str, model1, model2, model3)

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
        prediction_arr, tickers = get_predictions(data_dict, model_str, model)
        print("Prediction tuples from new method: ", prediction_arr)
        response_data = {
            "received_stocks": tickers,
            "message": "Stocks received successfully!",
            "predicted_close": prediction_arr
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

@app.route('/api/getTrades', methods=['POST'])
def get_trades():
    request_data = request.get_json()
    market = request_data.get('market', '')
    user = request_data.get('user', '')
    freq = request_data.get('freq', '')
    model = request_data.get('model', '')

    if market == 'NSE':
        if user == 'user':
            if freq == 'daily':
                trade_file = f'trade_data/{model}/nse_daily_user_trades.csv'
            else:
                trade_file = f'trade_data/{model}/nse_user_trades.csv'
        else:
            if freq == 'daily':
                trade_file = f'trade_data/{model}/nse_daily_bot_trades.csv'
            else:
                trade_file = f'trade_data/{model}/nse_bot_trades.csv'
    else:
        if user == 'user':
            if freq == 'daily':
                trade_file = f'trade_data/{model}/us_daily_user_trades.csv'
            else:
                trade_file = f'trade_data/{model}/us_user_trades.csv'
        else:
            if freq == 'daily':
                trade_file = f'trade_data/{model}/us_daily_bot_trades.csv'
            else:
                trade_file = f'trade_data/{model}/us_bot_trades.csv'

    trades = trade_helper(trade_file)
    return jsonify(trades)

@app.route('/api/trade', methods=['POST'])
def trade():
    request_data = request.get_json()
    trade_data = request_data.get('trade', [])
    market = request_data.get('market', '')
    model = request_data.get('model', '')

    if market == 'NSE':
        trade_file = f'trade_data/{model}/nse_daily_user_trades.csv'
    else:
        trade_file = f'trade_data/{model}/us_daily_user_trades.csv'

    ensure_headers(trade_file, trade_headers)

    with open(trade_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([trade_data['ticker'], trade_data['predictedClose'], trade_data['lastClosePrice'], trade_data['positionType'], '-', '-', '-', '-'])

    return jsonify({"message": "Trade saved successfully!"}), 200

def bot_trades_us():
    for model, model_str in zip(model_list, model_str_list):
        for stock_list, market in zip([us_stocks], ['us']):
            current_date = get_date_in_timezone(timezone_us)
            cache_key = f"{current_date}_{market}"
            print("cache key is: ", cache_key)

            if cache_key in stock_cache:
                print("returning data dict from cache")
                data_dict = stock_cache[cache_key]
            else:
                data_dict = fetch_stock_data(us_stocks)
                stock_cache[cache_key] = data_dict
            
            predictions = []
            if stock_list:
                prediction_arr, tickers = get_predictions(data_dict, model_str, model)
                for pred_tup in prediction_arr:
                    key, prediction, ltp = pred_tup
                    position_type = 'Long' if prediction[0] > ltp else 'Short'
                    prediction_tup = [key, prediction[0], ltp, position_type, '-', '-', '-', '-']
                    predictions.append(prediction_tup)                    
                    daily_trade_file = f'trade_data/{model_str}/{market}_daily_bot_trades.csv'
                    ensure_headers(daily_trade_file, trade_headers)
                    with open(daily_trade_file, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(prediction_tup)                   

def bot_trades_nse():
    for model, model_str in zip(model_list, model_str_list):
        for stock_list, market in zip([nse_stocks], ['nse']):
            current_date = get_date_in_timezone(timezone_nse)
            cache_key = f"{current_date}_{market}"
            print("cache key is: ", cache_key)

            if cache_key in stock_cache:
                print("returning data dict from cache")
                data_dict = stock_cache[cache_key]
            else:
                data_dict = fetch_stock_data(nse_stocks)
                stock_cache[cache_key] = data_dict

            predictions = []
            if stock_list:
                prediction_arr, tickers = get_predictions(data_dict, model_str, model)
                for pred_tup in prediction_arr:
                    key, prediction, ltp = pred_tup
                    position_type = 'Long' if prediction[0] > ltp else 'Short'
                    prediction_tup = [key, prediction[0], ltp, position_type, '-', '-', '-', '-']
                    predictions.append(prediction_tup)                    
                    daily_trade_file = f'trade_data/{model_str}/{market}_daily_bot_trades.csv'
                    ensure_headers(daily_trade_file, trade_headers)
                    with open(daily_trade_file, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(prediction_tup)    

def update_entry_prices_nse():
    for model_str in model_str_list:
        trade_files = [f'trade_data/{model_str}/nse_daily_bot_trades.csv', f'trade_data/{model_str}/nse_daily_user_trades.csv']

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
    for model_str in model_str_list:
        trade_files = [f'trade_data/{model_str}/us_daily_bot_trades.csv', f'trade_data/{model_str}/us_daily_user_trades.csv']

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
    for model_str in model_str_list:
        trade_files = [f'trade_data/{model_str}/us_daily_user_trades.csv', f'trade_data/{model_str}/us_daily_bot_trades.csv']
        target_files = [f'trade_data/{model_str}/us_user_trades.csv', f'trade_data/{model_str}/us_bot_trades.csv']

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
    for model_str in model_str_list:
        trade_files = [f'trade_data/{model_str}/nse_daily_user_trades.csv', f'trade_data/{model_str}/nse_daily_bot_trades.csv']
        target_files = [f'trade_data/{model_str}/nse_user_trades.csv', f'trade_data/{model_str}/nse_bot_trades.csv']

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

    app.run(debug=False)
