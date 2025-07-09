<template>
  <div ref="chartContainer" class="simple-area-chart"></div>
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

interface DataItem {
  date: string;
  value: number;
}

interface ChartConfig {
  xAxisName?: string;
  yAxisName?: string;
  color?: string;
  showSymbol?: boolean;
  smooth?: boolean;
  areaStyle?: boolean;
  title?: string;
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
    showSymbol: false,
    smooth: true,
    areaStyle: true,
    title: ''
  };
  
  const mergedConfig = { ...defaultConfig, ...config };
  
  // 获取X轴和Y轴数据
  const xAxisData = data.map(item => item.date);
  const seriesData = data.map(item => item.value);
  
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
    xAxis: {
      type: 'category',
      data: xAxisData,
      name: mergedConfig.xAxisName,
      axisLine: {
        lineStyle: {
          color: '#E0E0E0'
        }
      },
      axisLabel: {
        fontSize: 10,
        color: '#909399'
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
      trigger: 'axis',
      formatter: (params: any) => {
        const dataIndex = params[0].dataIndex;
        const date = data[dataIndex].date;
        const value = data[dataIndex].value;
        return `${date}<br/>${value}`;
      }
    },
    series: [
      {
        type: 'line',
        data: seriesData,
        smooth: mergedConfig.smooth,
        showSymbol: mergedConfig.showSymbol,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: {
          width: 2,
          color: mergedConfig.color
        },
        itemStyle: {
          color: mergedConfig.color
        },
        areaStyle: mergedConfig.areaStyle ? {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: echarts.color.modifyAlpha(mergedConfig.color, 0.5)
              },
              {
                offset: 1,
                color: echarts.color.modifyAlpha(mergedConfig.color, 0.05)
              }
            ]
          }
        } : undefined
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
.simple-area-chart {
  width: 100%;
  height: 100%;
}
</style> 