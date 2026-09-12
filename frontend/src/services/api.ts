import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const fetchDemandResults = async () => {
    const response = await apiClient.get('/demanda/resultados');
    return response.data;
};

export const fetchAnomalyResults = async () => {
    const response = await apiClient.get('/anomalias/resultados');
    return response.data;
};
