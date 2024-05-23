import yfinance as yf

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


