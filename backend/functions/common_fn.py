import yfinance as yf
from datetime import datetime
import os
import csv



def get_model_from_str(model_str : str, model1, model2, model3):
    if model_str == 'model1':
        return model1
    elif model_str == 'model2':
        return model2
    else:
        return model3

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


def get_date_in_timezone(timezone):
    return datetime.now(timezone).strftime('%Y-%m-%d')

def ensure_headers(file_path, headers):
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

def get_ltp(ticker):
    ticker_data = yf.Ticker(ticker)
    ltp = ticker_data.info['currentPrice']
    return ltp