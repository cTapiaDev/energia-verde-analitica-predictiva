import pandas as pd
import numpy as np
import json
import warnings
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense

warnings.filterwarnings("ignore")

def create_sequences(data: np.ndarray, seq_length: int):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        xs.append(data[i:(i + seq_length)])
        ys.append(data[i + seq_length])
    return np.array(xs), np.array(ys)

def run_pipeline():
    print("Iniciando pipeline de entrenamiento para demanda energética...")
    df = pd.read_csv('data/demanda_energia.csv')
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.set_index('fecha', inplace=True)

    print("Descomponiendo la serie temporal...")
    decomposition = seasonal_decompose(df['demanda'].tail(720), model='additive', period=24)

    test_size = 720
    train, test = df.iloc[:-test_size], df.iloc[-test_size:]

    print("Entrenando modelo ARIMA (esto puede tomar unos momentos)...")
    arima_model = ARIMA(train['demanda'], order=(2, 1, 2))
    arima_result = arima_model.fit()
    arima_pred = arima_result.forecast(steps=test_size).to_numpy()

    print("Preparando tensores para modelos de Deep Learning...")
    scaler = MinMaxScaler()
    scaled_train = scaler.fit_transform(train[['demanda']])
    
    seq_length = 24
    X_train, y_train = create_sequences(scaled_train, seq_length)

    test_inputs = df['demanda'].values[-(test_size + seq_length):].reshape(-1, 1)
    test_inputs = scaler.transform(test_inputs)
    X_test, y_test = create_sequences(test_inputs, seq_length)

    print("Entrenando modelo LSTM...")
    lstm_model = Sequential([
        LSTM(50, activation='relu', input_shape=(seq_length, 1)),
        Dense(1)
    ])
    lstm_model.compile(optimizer='adam', loss='mse')
    lstm_model.fit(X_train, y_train, epochs=3, batch_size=64, verbose=0) 
    lstm_pred_scaled = lstm_model.predict(X_test, verbose=0)
    lstm_pred = scaler.inverse_transform(lstm_pred_scaled).flatten()

    print("Entrenando modelo GRU...")
    gru_model = Sequential([
        GRU(50, activation='relu', input_shape=(seq_length, 1)),
        Dense(1)
    ])
    gru_model.compile(optimizer='adam', loss='mse')
    gru_model.fit(X_train, y_train, epochs=3, batch_size=64, verbose=0)
    gru_pred_scaled = gru_model.predict(X_test, verbose=0)
    gru_pred = scaler.inverse_transform(gru_pred_scaled).flatten()

    print("Calculando métricas de rendimiento...")
    real_values = test['demanda'].to_numpy()

    metrics = {
        "ARIMA": {
            "RMSE": float(np.sqrt(mean_squared_error(real_values, arima_pred))),
            "MAE": float(mean_absolute_error(real_values, arima_pred))
        },
        "LSTM": {
            "RMSE": float(np.sqrt(mean_squared_error(real_values, lstm_pred))),
            "MAE": float(mean_absolute_error(real_values, lstm_pred))
        },
        "GRU": {
            "RMSE": float(np.sqrt(mean_squared_error(real_values, gru_pred))),
            "MAE": float(mean_absolute_error(real_values, gru_pred))
        }
    }

    results = {
        "fechas_test": test.index.astype(str).tolist(),
        "valores_reales": real_values.tolist(),
        "predicciones": {
            "ARIMA": arima_pred.tolist(),
            "LSTM": lstm_pred.tolist(),
            "GRU": gru_pred.tolist()
        },
        "metricas": metrics,
        "descomposicion": {
            "fechas": decomposition.trend.index.astype(str).tolist(),
            "tendencia": np.nan_to_num(decomposition.trend.values).tolist(),
            "estacionalidad": np.nan_to_num(decomposition.seasonal.values).tolist(),
            "residuos": np.nan_to_num(decomposition.resid.values).tolist()
        }
    }

    with open('data/resultados_demanda.json', 'w') as f:
        json.dump(results, f)

    print("Pipeline finalizado exitosamente. Resultados en data/resultados_demanda.json")

if __name__ == "__main__":
    run_pipeline()