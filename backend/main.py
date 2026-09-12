from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(title="API Energía Verde S.A.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/demanda/resultados")
def get_demand_results():
    filepath = os.path.join("data", "resultados_demanda.json")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {"error": "Archivo de resultados no encontrado. Ejecuta pipeline_demanda.py primero."}

@app.get("/api/anomalias/resultados")
def get_anomaly_results():
    filepath = os.path.join("data", "resultados_anomalias.json")
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {"error": "Archivo no encontrado. Ejecuta pipeline_anomalias.py"}