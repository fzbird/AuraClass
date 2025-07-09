<template>
  <div ref="chartContainer" :style="{ height: `${height}px` }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts/core';
import { LineChart as EChartsLineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

// 注册必要的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  EChartsLineChart,
  CanvasRenderer
]);

const props = defineProps({
  chartData: {
    type: Object,
    required: true
  },
  height: {
    type: Number,
    default: 300
  },
  loading: {
    type: Boolean,
    default: false
  }
});

const chartContainer = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return;
  
  chart = echarts.init(chartContainer.value);
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize);
  
  // 更新图表数据
  updateChart();
};

// 更新图表数据
const updateChart = () => {
  if (!chart) return;
  
  // 设置loading状态
  if (props.loading) {
    chart.showLoading();
    return;
  } else {
    chart.hideLoading();
  }
  
  // 解析chartData
  const { labels = [], datasets = [] } = props.chartData;
  
  const series = datasets.map(dataset => ({
    name: dataset.label,
    type: 'line',
    data: dataset.data,
    smooth: true,
    showSymbol: false,
    lineStyle: {
      width: 2,
      color: dataset.borderColor
    },
    areaStyle: dataset.fill ? {
      color: dataset.backgroundColor
    } : undefined
  }));
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: datasets.map(dataset => dataset.label)
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: labels
    },
    yAxis: {
      type: 'value'
    },
    series
  };
  
  chart.setOption(option);
};

// 处理窗口大小变化
const handleResize = () => {
  chart?.resize();
};

// 组件挂载时初始化图表
onMounted(() => {
  initChart();
});

// 组件卸载时销毁图表实例
onUnmounted(() => {
  if (chart) {
    chart.dispose();
    chart = null;
  }
  window.removeEventListener('resize', handleResize);
});

// 监听数据变化，更新图表
watch(
  () => props.chartData,
  () => updateChart(),
  { deep: true }
);

// 监听loading状态变化
watch(
  () => props.loading,
  () => {
    if (chart) {
      props.loading ? chart.showLoading() : chart.hideLoading();
    }
  }
);
</script> 