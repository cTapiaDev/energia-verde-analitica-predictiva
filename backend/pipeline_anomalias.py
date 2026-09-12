import pandas as pd
import numpy as np
import json
import warnings
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense

warnings.filterwarnings("ignore")

def build_autoencoder(input_dim):
    input_layer = Input(shape=(input_dim,))
    encoded = Dense(16, activation='relu')(input_layer)
    encoded = Dense(8, activation='relu')(encoded)
    decoded = Dense(16, activation='relu')(encoded)
    output_layer = Dense(input_dim, activation='linear')(decoded)
    
    autoencoder = Model(inputs=input_layer, outputs=output_layer)
    autoencoder.compile(optimizer='adam', loss='mse')
    return autoencoder

def run_anomaly_pipeline():
    print("Iniciando pipeline de detección de anomalías...")
    df = pd.read_csv('data/sensores_turbinas.csv')
    
    anomalias_idx = df[df['es_anomalia'] == 1].index
    if len(anomalias_idx) > 0:
        centro = anomalias_idx[-1]
        inicio = max(0, centro - 1500)
        fin = min(len(df), inicio + 2000)
        df_subset = df.iloc[inicio:fin].copy()
    else:
        df_subset = df.tail(2000).copy()
        
    df_subset.reset_index(drop=True, inplace=True)
    
    print("Ejecutando modelo ARIMA para detección de anomalías...")
    arima_model = ARIMA(df_subset['vibracion'], order=(1, 0, 1))
    arima_result = arima_model.fit()
    
    residuos = np.abs(arima_result.resid)
    umbral_arima = np.mean(residuos) + 3 * np.std(residuos)
    df_subset['prediccion_arima'] = (residuos > umbral_arima).astype(int)

    print("Ejecutando modelo Autoencoder...")
    scaler = StandardScaler()
    datos_escalados = scaler.fit_transform(df_subset[['vibracion', 'temperatura']])
    
    autoencoder = build_autoencoder(datos_escalados.shape[1])
    autoencoder.fit(datos_escalados, datos_escalados, epochs=10, batch_size=32, verbose=0)
    
    reconstruccion = autoencoder.predict(datos_escalados, verbose=0)
    mse = np.mean(np.power(datos_escalados - reconstruccion, 2), axis=1)
    
    umbral_ae = np.percentile(mse, 95)
    df_subset['prediccion_ae'] = (mse > umbral_ae).astype(int)

    print("Calculando métricas de clasificación...")
    y_true = df_subset['es_anomalia'].to_numpy()
    y_pred_arima = df_subset['prediccion_arima'].to_numpy()
    y_pred_ae = df_subset['prediccion_ae'].to_numpy()

    metrics = {
        "ARIMA": {
            "Precision": float(precision_score(y_true, y_pred_arima, zero_division=0)),
            "Recall": float(recall_score(y_true, y_pred_arima, zero_division=0)),
            "F1_Score": float(f1_score(y_true, y_pred_arima, zero_division=0))
        },
        "Autoencoder": {
            "Precision": float(precision_score(y_true, y_pred_ae, zero_division=0)),
            "Recall": float(recall_score(y_true, y_pred_ae, zero_division=0)),
            "F1_Score": float(f1_score(y_true, y_pred_ae, zero_division=0))
        }
    }

    results = {
        "fechas": df_subset['fecha'].astype(str).tolist(),
        "vibracion": df_subset['vibracion'].tolist(),
        "temperatura": df_subset['temperatura'].tolist(),
        "anomalias_reales": y_true.tolist(),
        "anomalias_arima": y_pred_arima.tolist(),
        "anomalias_ae": y_pred_ae.tolist(),
        "metricas": metrics
    }

    with open('data/resultados_anomalias.json', 'w') as f:
        json.dump(results, f)

    print("Pipeline de anomalías finalizado. Resultados en data/resultados_anomalias.json")

if __name__ == "__main__":
    run_anomaly_pipeline()