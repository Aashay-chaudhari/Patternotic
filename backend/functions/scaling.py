from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import numpy as np
import pandas as pd
from .common_fn import get_ltp

def get_scaled_dataset_from_dict(data_dict, model_str):
    dataset = []
    scaler_close_array = []
    ticker_ltps = []
    tickers = []
    for key, data in data_dict.items():
        ltp = get_ltp(key)
        if model_str == "model1":
            scaler = StandardScaler()
            scaler_close = StandardScaler()
        elif model_str == "model2":
            scaler = MinMaxScaler()
            scaler_close = MinMaxScaler()
        else:
            scaler = RobustScaler()
            scaler_close = RobustScaler()
        
        scaled_data = scaler.fit_transform(data)
        _ = scaler_close.fit_transform(pd.DataFrame(data['Close']))
        if scaled_data.shape[0] == 30:
            dataset.append(np.array(scaled_data))
            ticker_ltps.append(ltp)
            tickers.append(key)
            scaler_close_array.append(scaler_close)

    return np.array(dataset), scaler_close_array, tickers, ticker_ltps

def get_predictions(data_dict : dict, model_str, model):
    dataset, scaler_close, tickers, ltps = get_scaled_dataset_from_dict(data_dict, model_str)
    print("shape of dataset: ", dataset.shape)
    predictions = model.predict(dataset)

    inverse_scaled_predictions = []

    for prediction, scaler in zip(predictions, scaler_close):
        rescaled_val = scaler.inverse_transform(prediction.reshape(-1, 1))
        inverse_scaled_predictions.append(rescaled_val.flatten().tolist())

    prediction_arr = []
    for key, prediction, ltp in zip(tickers, inverse_scaled_predictions, ltps):
        prediction_tup = (key, prediction, ltp)
        prediction_arr.append(prediction_tup)
    
    print("Prediction tuple example : ", prediction_arr[0])
    return prediction_arr, tickers
    

