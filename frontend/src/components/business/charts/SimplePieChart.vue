<template>
  <div ref="chartContainer" class="simple-pie-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts/core';
import { TooltipComponent, LegendComponent } from 'echarts/components';
import { PieChart } from 'echarts/charts';
import { UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';

// 注册必要的组件
echarts.use([
  TooltipComponent,
  LegendComponent,
  PieChart,
  UniversalTransition,
  CanvasRenderer
]);

interface DataItem {
  name: string;
  value: number;
}

interface ChartConfig {
  title?: string;
  colors?: string[];
  radius?: string | string[];
  showLegend?: boolean;
  legendPosition?: 'right' | 'bottom';
  roseType?: boolean;
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
    title: '',
    colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'],
    radius: '65%',
    showLegend: true,
    legendPosition: 'bottom' as 'bottom' | 'right',
    roseType: false
  };
  
  const mergedConfig = { ...defaultConfig, ...config };
  
  // 生成图表配置项
  const option = {
    title: mergedConfig.title ? {
      text: mergedConfig.title,
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 14,
        fontWeight: 'normal'
      }
    } : undefined,
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: mergedConfig.showLegend ? {
      orient: mergedConfig.legendPosition === 'right' ? 'vertical' : 'horizontal',
      right: mergedConfig.legendPosition === 'right' ? 10 : undefined,
      bottom: mergedConfig.legendPosition === 'bottom' ? 10 : undefined,
      type: 'scroll',
      pageIconSize: 8,
      pageButtonItemGap: 5,
      pageButtonGap: 5,
      pageTextStyle: {
        fontSize: 10
      },
      itemWidth: 10,
      itemHeight: 10,
      textStyle: {
        fontSize: 10
      }
    } : undefined,
    color: mergedConfig.colors,
    series: [
      {
        name: '',
        type: 'pie',
        radius: mergedConfig.radius,
        center: ['50%', '50%'],
        roseType: mergedConfig.roseType ? 'radius' : undefined,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 1
        },
        label: {
          show: false
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: data
      }
    ]
  };
  
  // 动态调整配置
  if (mergedConfig.title) {
    if (mergedConfig.legendPosition === 'bottom') {
      option.series[0].center = ['50%', '40%'];
    }
  }
  
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
.simple-pie-chart {
  width: 100%;
  height: 100%;
}
</style> 