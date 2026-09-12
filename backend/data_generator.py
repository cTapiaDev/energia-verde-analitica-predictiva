import pandas as pd
import numpy as np
import os

def generate_energy_demand_data():
    print("Generando datos de demanda energética...")
    fechas = pd.date_range(start="2019-01-01", end="2023-12-31 23:00:00", freq='h')
    n = len(fechas)
    
    tendencia = np.linspace(50, 100, n)
    
    estacionalidad_diaria = 20 * np.sin(2 * np.pi * fechas.hour.to_numpy() / 24)
    estacionalidad_anual = 30 * np.sin(2 * np.pi * fechas.dayofyear.to_numpy() / 365)
    
    ruido = np.random.normal(0, 5, n)
    
    demanda = tendencia + estacionalidad_diaria + estacionalidad_anual + ruido
    
    df = pd.DataFrame({'fecha': fechas, 'demanda': demanda})
    df.to_csv('data/demanda_energia.csv', index=False)
    print(f"Archivo demanda_energia.csv generado con {n} registros.")

def generate_sensor_data():
    print("Generando datos de sensores de turbinas...")
    fechas = pd.date_range(start="2022-01-01", end="2023-12-31 23:50:00", freq='10min')
    n = len(fechas)
    
    vibracion = np.random.normal(2.0, 0.3, n)
    
    temperatura = 60 + 15 * np.sin(2 * np.pi * fechas.hour.to_numpy() / 24) + np.random.normal(0, 2, n)
    
    anomalia_label = np.zeros(n)
    
    num_anomalias = 50
    indices_anomalias = np.random.choice(n, num_anomalias, replace=False)
    
    for idx in indices_anomalias:
        vibracion[idx:idx+6] += np.random.uniform(2.0, 5.0, min(6, n-idx))
        temperatura[idx:idx+6] += np.random.uniform(15.0, 30.0, min(6, n-idx))
        anomalia_label[idx:idx+6] = 1

    df = pd.DataFrame({
        'fecha': fechas,
        'vibracion': vibracion,
        'temperatura': temperatura,
        'es_anomalia': anomalia_label
    })
    df.to_csv('data/sensores_turbinas.csv', index=False)
    print(f"Archivo sensores_turbinas.csv generado con {n} registros.")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    generate_energy_demand_data()
    generate_sensor_data()