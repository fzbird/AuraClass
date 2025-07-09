<template>
  <div ref="chartContainer" class="simple-bar-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts/core';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { BarChart } from 'echarts/charts';
import { UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';

// 注册必要的组件
echarts.use([
  GridComponent,
  TooltipComponent,
  LegendComponent,
  BarChart,
  UniversalTransition,
  CanvasRenderer
]);

interface DataItem {
  name: string;
  value: number;
}

interface ChartConfig {
  xAxisName?: string;
  yAxisName?: string;
  color?: string;
  barWidth?: number;
  title?: string;
  horizontal?: boolean;
}

const props = defineProps({
  data: {
    type: Array as () => DataItem[],
    required: true
  },
  config: {
    type: Object as () => ChartConfig,
    default: () => ({})
  }
});

const chartContainer = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return;
  
  // 创建图表实例
  chart = echarts.init(chartContainer.value);
  
  // 配置图表选项
  updateChart();
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', handleResize);
};

// 更新图表数据和配置
const updateChart = () => {
  if (!chart) return;
  
  const { data, config } = props;
  const defaultConfig = {
    xAxisName: '',
    yAxisName: '',
    color: '#3366FF',
    barWidth: 16,
    title: '',
    horizontal: false
  };
  
  const mergedConfig = { ...defaultConfig, ...config };
  
  // 获取名称和值数据
  const categories = data.map(item => item.name);
  const values = data.map(item => item.value);
  
  // 根据方向生成不同的配置
  const xAxis = mergedConfig.horizontal ? {
    type: 'value',
    name: mergedConfig.xAxisName,
    axisLine: {
      show: false
    },
    axisLabel: {
      fontSize: 10,
      color: '#909399'
    },
    splitLine: {
      lineStyle: {
        color: '#F5F5F5'
      }
    }
  } : {
    type: 'category',
    data: categories,
    name: mergedConfig.xAxisName,
    axisLine: {
      lineStyle: {
        color: '#E0E0E0'
      }
    },
    axisLabel: {
      fontSize: 10,
      color: '#909399',
      interval: 0,
      rotate: categories.length > 6 ? 45 : 0
    }
  };
  
  const yAxis = mergedConfig.horizontal ? {
    type: 'category',
    data: categories,
    name: mergedConfig.yAxisName,
    axisLine: {
      lineStyle: {
        color: '#E0E0E0'
      }
    },
    axisLabel: {
      fontSize: 10,
      color: '#909399'
    }
  } : {
    type: 'value',
    name: mergedConfig.yAxisName,
    axisLine: {
      show: false
    },
    axisLabel: {
      fontSize: 10,
      color: '#909399'
    },
    splitLine: {
      lineStyle: {
        color: '#F5F5F5'
      }
    }
  };
  
  // 生成图表配置项
  const option = {
    title: mergedConfig.title ? {
      text: mergedConfig.title,
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    } : undefined,
    grid: {
      top: mergedConfig.title ? 40 : 15,
      right: 15,
      bottom: 20,
      left: 20,
      containLabel: true
    },
    xAxis,
    yAxis,
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const dataIndex = params[0].dataIndex;
        const name = data[dataIndex].name;
        const value = data[dataIndex].value;
        return `${name}<br/>${value}`;
      }
    },
    series: [
      {
        type: 'bar',
        data: values,
        barWidth: mergedConfig.barWidth,
        itemStyle: {
          color: mergedConfig.color
        }
      }
    ]
  };
  
  // 设置图表选项
  chart.setOption(option);
};

// 处理窗口大小调整
const handleResize = () => {
  chart?.resize();
};

// 监听数据和配置变化
watch(() => props.data, updateChart, { deep: true });
watch(() => props.config, updateChart, { deep: true });

// 组件挂载时初始化图表
onMounted(() => {
  initChart();
});

// 组件卸载时销毁图表
onUnmounted(() => {
  if (chart) {
    chart.dispose();
    chart = null;
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.simple-bar-chart {
  width: 100%;
  height: 100%;
}
</style> 