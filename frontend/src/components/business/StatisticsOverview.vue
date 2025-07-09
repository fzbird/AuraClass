<template>
  <div>
    <!-- 总体统计卡片 -->
    <n-grid :cols="24" :x-gap="16" :y-gap="16" class="mb-6">
      <n-grid-item :span="12" :md="8" :lg="6" v-for="(stat, index) in summaryStats" :key="index">
        <n-card class="statistic-card">
          <div class="text-center">
            <h3 class="text-lg mb-2 text-gray-600">{{ stat.title }}</h3>
            <div class="font-bold text-3xl">{{ stat.value }}</div>
            <div class="text-sm mt-2" :class="getValueChangeClass(stat.change)">
              {{ getFormattedChange(stat.change) }}
            </div>
          </div>
        </n-card>
      </n-grid-item>
    </n-grid>
    
    <!-- 量化项目分布图表 -->
    <n-grid :cols="24" :x-gap="16" :y-gap="16">
      <n-grid-item :span="24" :lg="12">
        <n-card title="量化项目分类分布" class="h-96">
          <div ref="categoryChartRef" class="w-full h-80"></div>
        </n-card>
      </n-grid-item>
      
      <n-grid-item :span="24" :lg="12">
        <n-card title="量化分数分布" class="h-96">
          <div ref="scoreChartRef" class="w-full h-80"></div>
        </n-card>
      </n-grid-item>
      
      <n-grid-item :span="24">
        <n-card title="每日记录数量趋势" class="h-96">
          <div ref="dailyChartRef" class="w-full h-80"></div>
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { NGrid, NGridItem, NCard } from 'naive-ui';
import * as echarts from 'echarts/core';
import { PieChart, BarChart, LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import dayjs from 'dayjs';
import { useThemeStore } from '@/stores/theme';

// 注册 ECharts 组件
echarts.use([
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  CanvasRenderer
]);

const props = defineProps({
  stats: {
    type: Object,
    default: () => ({})
  }
});

// 获取主题状态
const themeStore = useThemeStore();
const isDarkMode = computed(() => themeStore.darkMode);

const categoryChartRef = ref<HTMLElement | null>(null);
const scoreChartRef = ref<HTMLElement | null>(null);
const dailyChartRef = ref<HTMLElement | null>(null);
let categoryChart: echarts.ECharts | null = null;
let scoreChart: echarts.ECharts | null = null;
let dailyChart: echarts.ECharts | null = null;

// 获取 ECharts 主题配置
const getChartTheme = computed(() => {
  return isDarkMode.value ? {
    backgroundColor: 'transparent',
    textStyle: {
      color: '#e5e5e5'
    },
    title: {
      textStyle: {
        color: '#e5e5e5'
      }
    },
    legend: {
      textStyle: {
        color: '#e5e5e5'
      }
    },
    xAxis: {
      axisLine: {
        lineStyle: {
          color: '#555'
        }
      },
      axisLabel: {
        color: '#e5e5e5'
      },
      splitLine: {
        lineStyle: {
          color: '#333'
        }
      }
    },
    yAxis: {
      axisLine: {
        lineStyle: {
          color: '#555'
        }
      },
      axisLabel: {
        color: '#e5e5e5'
      },
      splitLine: {
        lineStyle: {
          color: '#333'
        }
      }
    }
  } : {};
});

// 处理概览统计数据
const summaryStats = computed(() => {
  if (!props.stats.summary) return [];
  
  const summary = props.stats.summary;
  
  return [
    {
      title: '总记录数',
      value: summary.total_records || 0,
      change: summary.records_change || 0
    },
    {
      title: '总学生数',
      value: summary.total_students || 0,
      change: 0
    },
    {
      title: '平均每人记录',
      value: summary.avg_records_per_student || 0,
      change: summary.avg_records_change || 0
    },
    {
      title: '平均分数',
      value: parseFloat(summary.avg_score).toFixed(2) || 0,
      change: summary.avg_score_change || 0
    }
  ];
});

// 获取变化值的 CSS 类
const getValueChangeClass = (change: number | null | undefined) => {
  if (!change) return '';
  return change > 0 ? 'text-green-500' : (change < 0 ? 'text-red-500' : '');
};

// 格式化变化值
const getFormattedChange = (change: number | null | undefined) => {
  if (!change) return '与上期持平';
  const prefix = change > 0 ? '+' : '';
  return `${prefix}${change} 与上期比较`;
};

// 初始化图表
onMounted(() => {
  // 延迟初始化图表，确保DOM已完全渲染
  setTimeout(initCharts, 500);
  
  // 添加窗口加载完成事件和调整大小事件
  window.addEventListener('load', reinitCharts);
  window.addEventListener('resize', handleResize);
});

// 监听数据变化，更新图表
watch(() => props.stats, (newVal) => {
  console.log('统计数据已更新:', newVal);
  
  // 当数据更新时，确保图表已经初始化并更新内容
  if (!categoryChart || !scoreChart || !dailyChart) {
    console.log('图表未初始化，尝试重新初始化...');
    reinitCharts();
  } else {
    console.log('更新已初始化的图表...');
  updateCharts();
  }
}, { deep: true });

// 监听主题变化，更新图表
watch(isDarkMode, () => {
  console.log('主题已变更，更新图表样式...');
  reinitCharts();
}, { immediate: false });

// 重新初始化所有图表
const reinitCharts = () => {
  console.log('重新初始化所有图表...');
  
  // 清理旧的图表实例
  categoryChart?.dispose();
  scoreChart?.dispose();
  dailyChart?.dispose();
  
  // 重新初始化
  initCharts();
};

const initCharts = () => {
  console.log('初始化图表...');
  
  if (!categoryChartRef.value || !scoreChartRef.value || !dailyChartRef.value) {
    console.log('图表容器DOM元素未就绪，500ms后重试...');
    setTimeout(initCharts, 500);
    return;
  }
  
  try {
    // 确保容器可见且有尺寸
    if (categoryChartRef.value.offsetWidth === 0 || categoryChartRef.value.offsetHeight === 0) {
      console.log('图表容器尺寸为0，500ms后重试...');
      setTimeout(initCharts, 500);
      return;
    }
  
    // 初始化图表
    console.log('创建ECharts实例...');
    categoryChart = echarts.init(categoryChartRef.value);
    scoreChart = echarts.init(scoreChartRef.value);
  dailyChart = echarts.init(dailyChartRef.value);
  
    // 立即更新图表数据
  updateCharts();
  } catch (error) {
    console.error('初始化图表时出错:', error);
    
    // 出错时延迟重试
    setTimeout(initCharts, 1000);
  }
};

const updateCharts = () => {
  console.log('更新图表数据...');
  
  // 确保图表实例存在
  if (!categoryChart || !scoreChart || !dailyChart) {
    console.log('图表未初始化，无法更新...');
    return;
  }
  
  // 更新分类分布图表
  updateCategoryChart();
  
  // 更新分数分布图表
  updateScoreChart();
  
  // 更新每日记录图表
  updateDailyChart();
};

// 更新分类分布图表
const updateCategoryChart = () => {
  if (!categoryChart) return;
  
  // 获取分类数据或使用默认空数据
  let categoryData: Array<{name: string, value: number}> = [];
  
  if (props.stats.category_distribution) {
    categoryData = Object.entries(props.stats.category_distribution).map(([name, value]) => ({
      name,
      value: Number(value)
    }));
  }
  
  // 设置默认数据，确保即使没有数据也能显示图表
  if (categoryData.length === 0) {
    categoryData = [
      { name: '暂无数据', value: 1 }
    ];
  }
    
    categoryChart.setOption({
    ...getChartTheme.value,
    title: {
      ...getChartTheme.value.title,
      text: '量化项目分类分布',
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
        ...(getChartTheme.value.title?.textStyle || {})
      }
    },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
      textStyle: {
        ...(getChartTheme.value.legend?.textStyle || {})
      }
      },
      series: [
        {
        name: '分类分布',
          type: 'pie',
        radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
            fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: categoryData
        }
      ]
    });
};
  
  // 更新分数分布图表
const updateScoreChart = () => {
  if (!scoreChart) return;
  
  // 获取分数分布数据
  const scoreData = props.stats.score_distribution || {};
  
  // 设置X轴标签
  let xAxisData: string[] = [];
  
  // 使用现有数据键作为标签，或者使用默认标签
  if (Object.keys(scoreData).length > 0) {
    xAxisData = Object.keys(scoreData);
  } else {
    xAxisData = ['-2', '-1', '0', '1', '2'];
  }
  
  // 设置Y轴数据
  const seriesData = xAxisData.map(key => scoreData[key] || 0);
    
    scoreChart.setOption({
    ...getChartTheme.value,
    title: {
      ...getChartTheme.value.title,
      text: '量化分数分布',
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
        ...(getChartTheme.value.title?.textStyle || {})
      }
    },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
      xAxis: {
        type: 'category',
        data: xAxisData,
      axisLine: {
        ...(getChartTheme.value.xAxis?.axisLine || {})
      },
        axisLabel: {
        ...(getChartTheme.value.xAxis?.axisLabel || {})
        }
      },
      yAxis: {
      type: 'value',
      axisLine: {
        ...(getChartTheme.value.yAxis?.axisLine || {})
      },
      axisLabel: {
        ...(getChartTheme.value.yAxis?.axisLabel || {})
      },
      splitLine: {
        ...(getChartTheme.value.yAxis?.splitLine || {})
      }
      },
      series: [
        {
        name: '记录数量',
        type: 'bar',
        barWidth: '60%',
          data: seriesData,
          itemStyle: {
          color: function(params: {dataIndex: number}) {
            const colors = ['#F56C6C', '#E6A23C', '#909399', '#67C23A', '#409EFF'];
            return colors[params.dataIndex % colors.length];
            }
          }
        }
      ]
    });
};
  
  // 更新每日记录图表
const updateDailyChart = () => {
  if (!dailyChart) return;
  
  const dailyRecords = props.stats.daily_records || {};
  
  // 获取日期列表（X轴数据）
  let dates: string[] = [];
  let recordCounts: number[] = [];
  
  if (Object.keys(dailyRecords).length > 0) {
    // 如果有实际数据，按日期排序
    dates = Object.keys(dailyRecords).sort((a, b) => {
      return dayjs(a).valueOf() - dayjs(b).valueOf();
    });
    recordCounts = dates.map(date => dailyRecords[date] || 0);
  } else {
    // 默认数据：过去7天
    for (let i = 6; i >= 0; i--) {
      const date = dayjs().subtract(i, 'day').format('YYYY-MM-DD');
      dates.push(date);
      recordCounts.push(0);
    }
  }
    
    dailyChart.setOption({
    ...getChartTheme.value,
    title: {
      ...getChartTheme.value.title,
      text: '每日记录数量趋势',
      left: 'center',
      top: 0,
      textStyle: {
        fontSize: 16,
        ...(getChartTheme.value.title?.textStyle || {})
      }
    },
      tooltip: {
        trigger: 'axis'
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
      data: dates,
      axisLine: {
        ...(getChartTheme.value.xAxis?.axisLine || {})
      },
        axisLabel: {
        ...(getChartTheme.value.xAxis?.axisLabel || {})
        }
      },
      yAxis: {
      type: 'value',
      axisLine: {
        ...(getChartTheme.value.yAxis?.axisLine || {})
      },
      axisLabel: {
        ...(getChartTheme.value.yAxis?.axisLabel || {})
      },
      splitLine: {
        ...(getChartTheme.value.yAxis?.splitLine || {})
      }
      },
      series: [
        {
        name: '记录数',
          type: 'line',
        data: recordCounts,
          areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: isDarkMode.value ? 'rgba(65, 105, 225, 0.6)' : 'rgba(65, 105, 225, 0.8)'
          },
              {
                offset: 1,
                color: isDarkMode.value ? 'rgba(65, 105, 225, 0.1)' : 'rgba(65, 105, 225, 0.2)'
          }
            ]
          }
        },
        smooth: true
        }
      ]
    });
};

// 响应窗口大小变化的处理函数
const handleResize = () => {
  categoryChart?.resize();
  scoreChart?.resize();
  dailyChart?.resize();
};

// 组件销毁前清理图表和事件监听器
onUnmounted(() => {
  console.log('组件卸载，清理资源...');
  categoryChart?.dispose();
  scoreChart?.dispose();
  dailyChart?.dispose();
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('load', reinitCharts);
});
</script>

<style scoped>
.statistic-card {
  transition: all 0.3s ease;
}

.statistic-card .text-lg {
  transition: color 0.3s ease;
}

.statistic-card .text-3xl {
  transition: color 0.3s ease;
}

:root.dark .statistic-card {
  background-color: #202023;
}

:root.dark .text-gray-600 {
  color: #a0aec0;
}

:root.dark .text-3xl {
  color: #e2e8f0;
}

.text-green-500 {
  color: #48bb78;
}

.text-red-500 {
  color: #f56565;
}

:root.dark .text-green-500 {
  color: #68d391;
}

:root.dark .text-red-500 {
  color: #fc8181;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.text-center {
  text-align: center;
}

.text-lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
}

.text-3xl {
  font-size: 1.875rem;
  line-height: 2.25rem;
}

.text-sm {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.font-bold {
  font-weight: 700;
}

.text-gray-600 {
  color: #4b5563;
}

.w-full {
  width: 100%;
}

.h-80 {
  height: 20rem;
}

.h-96 {
  height: 24rem;
}
</style>
