<template>
  <div ref="chartContainer" :style="{ height: `${height}px` }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts/core';
import { PieChart as EChartsPieChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

// 定义图表数据的类型
interface DatasetItem {
  label?: string;
  data: number[];
  backgroundColor: string[];
}

interface ChartDataType {
  labels: string[];
  datasets: DatasetItem[];
}

// 注册必要的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  EChartsPieChart,
  CanvasRenderer
]);

const props = defineProps({
  chartData: {
    type: Object as () => ChartDataType,
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
  
  if (datasets.length === 0 || labels.length === 0) {
    return;
  }
  
  // 构建饼图数据
  const dataset = datasets[0];
  const data = labels.map((label, index) => ({
    name: label,
    value: dataset.data[index],
    itemStyle: {
      color: dataset.backgroundColor[index % dataset.backgroundColor.length]
    }
  }));
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: labels
    },
    series: [
      {
        name: dataset.label || '数量',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '14',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data
      }
    ]
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