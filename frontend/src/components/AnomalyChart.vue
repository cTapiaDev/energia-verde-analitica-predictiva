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
    if (!chartRef.value || !props.data || !props.data.fechas) return;

    d3.select(chartRef.value).selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = 800 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

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
    const dataset = props.data.fechas.map((d: string, i: number) => ({
        date: parseTime(d) as Date,
        vibration: props.data.vibracion[i],
        isAnomaly: props.data.anomalias_ae[i] === 1,
    }));

    const x = d3
        .scaleTime()
        .domain(d3.extent(dataset, (d: any) => d.date) as [Date, Date])
        .range([0, width]);

    const y = d3
        .scaleLinear()
        .domain([0, (d3.max(dataset, (d: any) => d.vibration) as number) * 1.2])
        .range([height, 0]);

    svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x));
    svg.append('g').call(d3.axisLeft(y));

    const line = d3
        .line<any>()
        .x((d) => x(d.date))
        .y((d) => y(d.vibration));

    svg.append('path')
        .datum(dataset)
        .attr('fill', 'none')
        .attr('stroke', '#888888')
        .attr('stroke-width', 1.5)
        .attr('d', line);

    const anomalies = dataset.filter((d: any) => d.isAnomaly);

    svg.selectAll('.dot')
        .data(anomalies)
        .enter()
        .append('circle')
        .attr('cx', (d: any) => x(d.date))
        .attr('cy', (d: any) => y(d.vibration))
        .attr('r', 4)
        .attr('fill', '#e74c3c');
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
