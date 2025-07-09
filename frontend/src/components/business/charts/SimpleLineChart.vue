<template>
  <div ref="chartContainer" class="simple-line-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts/core';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { LineChart } from 'echarts/charts';
import { UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';

// 注册必要的组件
echarts.use([
  GridComponent,
  TooltipComponent,
  LegendComponent,
  LineChart,
  UniversalTransition,
  CanvasRenderer
]);

interface LineDataItem {
  name: string;
  data: Array<number | null>;
}

interface ChartConfig {
  xAxisName?: string;
  yAxisName?: string;
  categories: string[];
  colors?: string[];
  showSymbol?: boolean;
  smooth?: boolean;
  title?: string;
  showLegend?: boolean;
}

const props = defineProps({
  data: {
    type: Array as () => LineDataItem[],
    required: true
  },
  config: {
    type: Object as () => ChartConfig,
    required: true
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
    showSymbol: false,
    smooth: true,
    title: '',
    showLegend: true,
    colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272']
  };
  
  const mergedConfig = { ...defaultConfig, ...config };
  
  // 生成序列数据
  const series = data.map((item, index) => ({
    name: item.name,
    type: 'line',
    data: item.data,
    smooth: mergedConfig.smooth,
    showSymbol: mergedConfig.showSymbol,
    symbol: 'circle',
    symbolSize: 5,
    lineStyle: {
      width: 2,
      color: mergedConfig.colors && mergedConfig.colors[index % mergedConfig.colors.length]
    },
    itemStyle: {
      color: mergedConfig.colors && mergedConfig.colors[index % mergedConfig.colors.length]
    }
  }));
  
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
      bottom: mergedConfig.showLegend ? 30 : 20,
      left: 20,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: mergedConfig.categories,
      name: mergedConfig.xAxisName,
      axisLine: {
        lineStyle: {
          color: '#E0E0E0'
        }
      },
      axisLabel: {
        fontSize: 10,
        color: '#909399',
        rotate: mergedConfig.categories.length > 8 ? 45 : 0
      },
      boundaryGap: false
    },
    yAxis: {
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
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: mergedConfig.showLegend ? {
      bottom: 0,
      itemWidth: 10,
      itemHeight: 10,
      textStyle: {
        fontSize: 10
      }
    } : undefined,
    color: mergedConfig.colors,
    series
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
.simple-line-chart {
  width: 100%;
  height: 100%;
}
</style> 