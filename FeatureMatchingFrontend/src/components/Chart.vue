<template>
    <div ref="chartRef" :style="{ width: props.width, height: props.height }"></div>
</template>

<script setup lang="ts" name="Chart">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import * as echarts from 'echarts';

interface Props {
    option: any;
    width?: string;
    height?: string;
}

const props = withDefaults(defineProps<Props>(), {
    width: '100%',
    height: '100%',
});

const chartRef = ref<HTMLElement>();

let chart: echarts.ECharts | null = null;
let resizeTimer: any = null;

const initChart = () => {
    if (!chartRef.value) return;
    if (chart) chart.dispose();
    chart = echarts.init(chartRef.value);
    chart.setOption(props.option);
};

const handleResize = () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        chart?.resize();
    }, 300);
};

onMounted(() => {
    initChart();
    window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize);
    chart?.dispose();
    chart = null;
});
</script>
