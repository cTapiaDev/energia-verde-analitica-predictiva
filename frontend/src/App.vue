<template>
    <div class="dashboard">
        <header class="header">
            <h1>Informe Técnico: Energía Verde S.A.</h1>
            <p>Análisis de Series Temporales y Detección de Anomalías</p>
        </header>

        <main v-if="demandData && anomalyData" class="content">
            <section class="card">
                <h2>1. Predicción de Demanda Energética</h2>
                <DemandChart :data="demandData" />

                <div class="metrics-container">
                    <h3>Métricas de Evaluación (Último Mes)</h3>
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>Modelo</th>
                                <th>RMSE</th>
                                <th>MAE</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(metrics, model) in demandData.metricas" :key="model">
                                <td>{{ model }}</td>
                                <td>{{ metrics.RMSE.toFixed(2).replace('.', ',') }}</td>
                                <td>{{ metrics.MAE.toFixed(2).replace('.', ',') }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <section class="card">
                <h2>2. Detección de Anomalías en Turbinas</h2>
                <AnomalyChart :data="anomalyData" />

                <div class="metrics-container">
                    <h3>Métricas de Clasificación (Vibración y Temperatura)</h3>
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>Modelo</th>
                                <th>Precision</th>
                                <th>Recall</th>
                                <th>F1-Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(metrics, model) in anomalyData.metricas" :key="model">
                                <td>{{ model }}</td>
                                <td>{{ metrics.Precision.toFixed(2).replace('.', ',') }}</td>
                                <td>{{ metrics.Recall.toFixed(2).replace('.', ',') }}</td>
                                <td>{{ metrics.F1_Score.toFixed(2).replace('.', ',') }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>
        </main>

        <div v-else class="loading">
            <p>Cargando datos analíticos desde la API...</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { fetchDemandResults, fetchAnomalyResults } from './services/api';
import DemandChart from './components/DemandChart.vue';
import AnomalyChart from './components/AnomalyChart.vue';

const demandData = ref<any>(null);
const anomalyData = ref<any>(null);

const loadData = async () => {
    try {
        const [demand, anomaly] = await Promise.all([fetchDemandResults(), fetchAnomalyResults()]);
        demandData.value = demand;
        anomalyData.value = anomaly;
    } catch (error) {
        console.error('Error al cargar datos:', error);
    }
};

onMounted(() => {
    loadData();
});
</script>

<style>
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f5f7fa;
    margin: 0;
    padding: 0;
    color: #2c3e50;
}

.dashboard {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
}

.header {
    text-align: center;
    margin-bottom: 2rem;
}

.header h1 {
    margin: 0;
    color: #2c3e50;
}

.header p {
    color: #7f8c8d;
}

.card {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.metrics-container {
    margin-top: 2rem;
}

.metrics-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

.metrics-table th,
.metrics-table td {
    border: 1px solid #ebeef5;
    padding: 12px;
    text-align: left;
}

.metrics-table th {
    background-color: #f8f9fa;
    font-weight: 600;
}

.loading {
    text-align: center;
    font-size: 1.2rem;
    color: #7f8c8d;
    padding: 3rem;
}
</style>
