from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import StandardScaler
from functions.getTickers import fetch_stock_data  # Import the function
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

# Load the saved model
model = load_model('models/stock_price_prediction_model.h5')
model.compile(optimizer='adam', loss='mean_squared_error')

def get_ltp(ticker):
    print("Inside get ltp for ", ticker)
    ticker_data = yf.Ticker(ticker)
    ltp = ticker_data.info['currentPrice']
    print("ltp is: ", ltp)
    return ltp

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

# Takes in a list of tickers, and returns a dictionary of (ticker, prediction, last traded price)
@app.route('/data', methods=['POST'])
def get_data():
    request_data = request.get_json()
    print("request data is: ", request_data)
    tickers = request_data.get('stocks', [])
    market = request_data.get('market', '')
    print("tickers are: ", tickers)
    print("market is: ", market)

    # Fetch stock data using the function from getTickers.py
    data_dict = fetch_stock_data(tickers)
    
    # Assuming you want to predict the next day's closing price for the first ticker
    if tickers:
        predictions = []
        for key, data in data_dict.items():
            print("data columns: ", data.columns, data.shape)
            if data.shape[0] == 0:
                continue
            if get_ltp(key) != data['Close'].iloc[-1]:
                print("Can not trade ", key, " right now as the market is not closed.")
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

# Takes in the market type, and returns the bot trades recorded in the appropriate file
@app.route('/getBotTrades', methods=['POST'])
def get_bot_trades():
    print("inside get bot trades")
    request_data = request.get_json()
    market = request_data.get('market', '')
    print("market is: ", market)
    if market == 'NSE':
        print("Inside market == nse")
        trade_file = 'nse_daily_bot_trades.csv'

        if not os.path.exists(trade_file):
            print("returning empty list")
            return jsonify([])  # Return an empty list if the file doesn't exist
        print("continuing in if.")
        trades = []
        with open(trade_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                trades.append(row)

        return jsonify(trades)
    else:
        trade_file = 'us_daily_bot_trades.csv'
        if not os.path.exists(trade_file):
            return jsonify([])  # Return an empty list if the file doesn't exist

        trades = []
        with open(trade_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                trades.append(row)

        return jsonify(trades)

# Takes in the market type, and returns the user trades recorded in the appropriate file
@app.route('/getTrades', methods=['POST'])
def get_trades():
    request_data = request.get_json()
    market = request_data.get('market', '')
    print("market is: ", market)
    if market == 'NSE':
        trade_file = 'nse_daily_user_trades.csv'
        if not os.path.exists(trade_file):
            return jsonify([])  # Return an empty list if the file doesn't exist

        trades = []
        with open(trade_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                trades.append(row)

        return jsonify(trades)
    else:
        trade_file = 'us_daily_user_trades.csv'
        if not os.path.exists(trade_file):
            return jsonify([])  # Return an empty list if the file doesn't exist

        trades = []
        with open(trade_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                trades.append(row)

        return jsonify(trades)


# Define route to receive trade information
@app.route('/trade', methods=['POST'])
def trade():
    request_data = request.get_json()
    trade_data = request_data.get('trade', [])
    market = request_data.get('market', '')
    print("market is: ", market)

    if market == 'NSE':
        trade_file = 'nse_daily_user_trades.csv'
        # Check if the file exists, if not create it with headers
        if not os.path.exists(trade_file):
            with open(trade_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ticker', 'predictedClose', 'lastClosePrice', 'positionType', 'entryPrice', 'closePrice', 'profit', 'date'])
        
        # Append the trade data to the CSV file
        with open(trade_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([trade_data['ticker'], trade_data['predictedClose'], trade_data['lastClosePrice'], trade_data['positionType'], '', '', '', ''])
        
        return jsonify({"message": "Trade saved successfully!"}), 200
    else:
        trade_file = 'us_daily_user_trades.csv'
    
        # Check if the file exists, if not create it with headers
        if not os.path.exists(trade_file):
            with open(trade_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ticker', 'predictedClose', 'lastClosePrice', 'positionType', 'entryPrice', 'closePrice', 'profit', 'date'])
        
        # Append the trade data to the CSV file
        with open(trade_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([trade_data['ticker'], trade_data['predictedClose'], trade_data['lastClosePrice'], trade_data['positionType'], '', '', '', ''])
        
        return jsonify({"message": "Trade saved successfully!"}), 200

def bot_trades_us():
    for stock_list, market in zip([us_stocks], ['us']):
        print("stock, prefix : ", stock_list, market)
        # Fetch stock data using the function from getTickers.py
        data_dict = fetch_stock_data(stock_list)
        
        if stock_list:
            predictions = []
            for key, data in data_dict.items():
                if data.shape[0] == 0:
                    continue
                prediction, ltp = make_predictions(model, data[-30:], key)
                position_type = 'Long' if prediction > ltp else 'Short'
                prediction_tup = [key, prediction.flatten().item(), ltp, position_type, '', '', '', '']
                predictions.append(prediction_tup)
                
                # Write to daily bot trades CSV
                daily_trade_file = f'{market}_daily_bot_trades.csv'
                if not os.path.exists(daily_trade_file):
                    with open(daily_trade_file, mode='w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['ticker', 'predictedClose', 'lastClosePrice', 'positionType', 'entryPrice', 'closePrice', 'profit', 'date'])
                with open(daily_trade_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(prediction_tup)

def bot_trades_nse():
    for stock_list, market in zip([nse_stocks], ['nse']):
        print("stock, prefix : ", stock_list, market)
        # Fetch stock data using the function from getTickers.py
        data_dict = fetch_stock_data(stock_list)
        
        if stock_list:
            predictions = []
            for key, data in data_dict.items():
                if data.shape[0] == 0:
                    continue
                prediction, ltp = make_predictions(model, data[-30:], key)
                position_type = 'Long' if prediction > ltp else 'Short'
                prediction_tup = [key, prediction.flatten().item(), ltp, position_type, '', '', '', '']
                predictions.append(prediction_tup)
                
                # Write to daily bot trades CSV
                daily_trade_file = f'{market}_daily_bot_trades.csv'
                if not os.path.exists(daily_trade_file):
                    with open(daily_trade_file, mode='w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['ticker', 'predictedClose', 'lastClosePrice', 'positionType', 'entryPrice', 'closePrice', 'profit', 'date'])
                with open(daily_trade_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(prediction_tup)

def update_entry_prices_nse():
    trade_files = ['nse_daily_bot_trades.csv', 'nse_daily_user_trades.csv']

    for trade_file in trade_files:
        if not os.path.exists(trade_file):
            return

        trades = pd.read_csv(trade_file)
        for index, trade in trades.iterrows():
            ticker = trade['ticker']
            # Fetch the opening price
            opening_price = get_ltp(ticker)
            trades.at[index, 'entryPrice'] = opening_price

        trades.to_csv(trade_file, index=False)
        print("Entry prices updated.")

def update_entry_prices_us():
    trade_files = ['us_daily_bot_trades.csv', 'us_daily_user_trades.csv']

    for trade_file in trade_files:
        if not os.path.exists(trade_file):
            return

        trades = pd.read_csv(trade_file)
        for index, trade in trades.iterrows():
            ticker = trade['ticker']
            # Fetch the opening price
            opening_price = get_ltp(ticker)
            trades.at[index, 'entryPrice'] = opening_price

        trades.to_csv(trade_file, index=False)
        print("Entry prices updated.")

def update_close_prices_and_profit_us():
    trade_files = ['us_daily_user_trades.csv', 'us_daily_bot_trades.csv']
    target_files = ['us_user_trades.csv', 'us_bot_trades.csv']

    for trade_file, target_file in zip(trade_files, target_files):
        if not os.path.exists(trade_file):
            continue

        trades = pd.read_csv(trade_file)
        print("trades are : ", trades)
        executed_trades = []
        for index, trade in trades.iterrows():
            current_date = datetime.now().strftime('%Y-%m-%d')
            ticker = trade['ticker']
            # Fetch the closing price
            closing_price = get_ltp(ticker)
            entry_price = trades.at[index, 'entryPrice']
            position_type = trades.at[index, 'positionType']
            
            if pd.isna(entry_price) or pd.isna(closing_price):
                continue  # Skip if entry price or closing price is NaN
            
            entry_price = float(entry_price)
            closing_price = float(closing_price)
            
            if position_type == 'Long':
                profit = (closing_price - entry_price + 1) * 100 / entry_price
            else:  # Short position
                profit = (entry_price - closing_price + 1) * 100 / entry_price
            
            print("closing price, entry_price and position_type : ", closing_price, entry_price, position_type, type(closing_price),type(entry_price))
            print("profit , closing price: ", profit, type(profit), closing_price, type(closing_price))
            trades.at[index, 'closePrice'] = closing_price
            trades.at[index, 'profit'] = profit
            trades.at[index, 'date'] = str(current_date)

        # Append executed trades to user_trades.csv
        trades.to_csv(target_file, index=False)
        # Clear daily_user_trades.csv
        trades.drop(trades.index, inplace=True)
        trades.to_csv(trade_file, index=False)
        print("Close prices and profit updated, and daily trades moved to user_trades.csv.")

def update_close_prices_and_profit_nse():
    trade_files = ['nse_daily_user_trades.csv', 'nse_daily_bot_trades.csv']
    target_files = ['nse_user_trades.csv', 'nse_bot_trades.csv']

    for trade_file, target_file in zip(trade_files, target_files):
        if not os.path.exists(trade_file):
            continue

        trades = pd.read_csv(trade_file)
        print("trades are : ", trades)
        executed_trades = []
        for index, trade in trades.iterrows():
            current_date = datetime.now().strftime('%Y-%m-%d')
            ticker = trade['ticker']
            # Fetch the closing price
            closing_price = get_ltp(ticker)
            entry_price = trades.at[index, 'entryPrice']
            position_type = trades.at[index, 'positionType']
            
            if pd.isna(entry_price) or pd.isna(closing_price):
                continue  # Skip if entry price or closing price is NaN
            
            entry_price = float(entry_price)
            closing_price = float(closing_price)
            
            if position_type == 'Long':
                profit = (closing_price - entry_price + 1) * 100 / entry_price
            else:  # Short position
                profit = (entry_price - closing_price + 1) * 100 / entry_price
            
            print("closing price, entry_price and position_type : ", closing_price, entry_price, position_type, type(closing_price),type(entry_price))
            print("profit , closing price: ", profit, type(profit), closing_price, type(closing_price))
            trades.at[index, 'closePrice'] = closing_price
            trades.at[index, 'profit'] = profit
            trades.at[index, 'date'] = str(current_date)

        trades.to_csv(target_file, index=False)
        # Clear daily_user_trades.csv
        trades.drop(trades.index, inplace=True)
        trades.to_csv(trade_file, index=False)
        print("Close prices and profit updated, and daily trades moved to user_trades.csv.")

# Scheduler setup
scheduler = BackgroundScheduler()
timezone_us = pytz.timezone('America/New_York')
timezone_nse = pytz.timezone('Asia/Kolkata')

# Check if the script is being run directly
if __name__ == "__main__":
    # Schedule bot for US markets
    # Ideal timings: bot_trade_us : 15:30 pm, update_entry_prices_us : 9:31 am, update_close_prices_and_profit_us : 16:00 pm
    scheduler.add_job(bot_trades_us, CronTrigger(day_of_week='mon-fri', hour=15, minute=30, timezone=timezone_us))
    scheduler.add_job(update_entry_prices_us, CronTrigger(day_of_week='mon-fri', hour=9, minute=31, timezone=timezone_us))
    scheduler.add_job(update_close_prices_and_profit_us, CronTrigger(day_of_week='mon-fri', hour=16, minute=0, timezone=timezone_us))

    # Schedule bot for NSE markets
    # Ideal timings: bot_trade_nse : 15:30 pm, update_entry_prices_nse : 9:16 am, update_close_prices_and_profit_nse : 15:30 pm
    scheduler.add_job(bot_trades_nse, CronTrigger(day_of_week='mon-fri', hour=15, minute=30, timezone=timezone_nse))
    scheduler.add_job(update_entry_prices_nse, CronTrigger(day_of_week='mon-fri', hour=9, minute=16, timezone=timezone_nse))
    scheduler.add_job(update_close_prices_and_profit_nse, CronTrigger(day_of_week='mon-fri', hour=15, minute=30, timezone=timezone_nse))

    scheduler.start()

    app.run(debug=True)  # Set debug to False to prevent re-execution
