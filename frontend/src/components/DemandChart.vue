<template>
    <div class="chart-container" ref="chartRef"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as d3 from 'd3';

const props = defineProps<{
    data: any;
}>();

const chartRef = ref<HTMLDivElement | null>(null);

const drawChart = () => {
    if (!chartRef.value || !props.data || !props.data.fechas_test) return;

    d3.select(chartRef.value).selectAll('*').remove();

    const margin = { top: 20, right: 100, bottom: 40, left: 50 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3
        .select(chartRef.value)
        .append('svg')
        .attr(
            'viewBox',
            `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`,
        )
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    const parseTime = d3.timeParse('%Y-%m-%d %H:%M:%S');
    const dataset = props.data.fechas_test.map((d: string, i: number) => ({
        date: parseTime(d) as Date,
        real: props.data.valores_reales[i],
        lstm: props.data.predicciones.LSTM[i],
        gru: props.data.predicciones.GRU[i],
        arima: props.data.predicciones.ARIMA[i],
    }));

    const x = d3
        .scaleTime()
        .domain(d3.extent(dataset, (d: any) => d.date) as [Date, Date])
        .range([0, width]);

    const maxVal = d3.max(dataset, (d: any) => Math.max(d.real, d.lstm, d.gru, d.arima)) as number;
    const minVal = d3.min(dataset, (d: any) => Math.min(d.real, d.lstm, d.gru, d.arima)) as number;

    const y = d3
        .scaleLinear()
        .domain([minVal * 0.9, maxVal * 1.1])
        .range([height, 0]);

    svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x));
    svg.append('g').call(d3.axisLeft(y));

    const lineGenerator = (key: string) =>
        d3
            .line<any>()
            .x((d) => x(d.date))
            .y((d) => y(d[key]));

    const legend = svg.append('g').attr('transform', `translate(${width + 10}, 0)`);

    const models = [
        { key: 'real', color: '#333333', label: 'Real' },
        { key: 'lstm', color: '#42b883', label: 'LSTM' },
        { key: 'gru', color: '#3498db', label: 'GRU' },
        { key: 'arima', color: '#e74c3c', label: 'ARIMA' },
    ];

    models.forEach((m, i) => {
        const row = legend.append('g').attr('transform', `translate(0, ${i * 25})`);

        row.append('rect').attr('width', 12).attr('height', 12).attr('fill', m.color).attr('rx', 2);

        row.append('text')
            .attr('x', 20)
            .attr('y', 10)
            .style('font-size', '12px')
            .style('fill', '#2c3e50')
            .text(m.label);

        svg.append('path')
            .datum(dataset)
            .attr('fill', 'none')
            .attr('stroke', m.color)
            .attr('stroke-width', 1.5)
            .attr('d', lineGenerator(m.key));
    });
};

onMounted(() => drawChart());
watch(
    () => props.data,
    () => drawChart(),
    { deep: true },
);
</script>

<style scoped>
.chart-container {
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
}
</style>
