<template>
  <div class="trend-analysis-chart">
    <n-card :title="title" :bordered="false">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="period"
            placeholder="选择时间周期"
            :options="periodOptions"
            size="small"
          />
          <n-select 
            v-model:value="metric"
            placeholder="选择指标"
            :options="metricOptions"
            size="small"
          />
        </n-space>
      </template>
      
      <div class="chart-container" ref="chartRef"></div>
      
      <n-skeleton v-if="loading" :repeat="1" animated />
      <n-empty v-else-if="!hasData" description="暂无数据" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { NCard, NSpace, NSelect, NSkeleton, NEmpty, useMessage } from 'naive-ui';
import * as echarts from 'echarts/core';
import { LineChart, BarChart } from 'echarts/charts';
import { 
  TitleComponent, 
  TooltipComponent, 
  GridComponent, 
  LegendComponent,
  DataZoomComponent,
  ToolboxComponent,
  MarkLineComponent,
  MarkPointComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { getQuantTrends } from '@/services/api/statistics';
import { getMockTrendData } from '@/services/api/mock-dashboard';
import type { RecordTrend } from '@/types/statistics';
import type { ECBasicOption } from 'echarts/types/dist/shared';
import { useUserStore } from '@/stores/user';

// 注册 ECharts 组件
echarts.use([
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
  ToolboxComponent,
  MarkLineComponent,
  MarkPointComponent,
  CanvasRenderer
]);

// 定义组件属性
const props = defineProps({
  title: {
    type: String,
    default: '量化记录趋势分析'
  },
  classId: {
    type: Number,
    default: null
  },
  studentId: {
    type: Number,
    default: null
  },
  itemId: {
    type: Number,
    default: null
  },
  startDate: {
    type: String,
    default: null
  },
  endDate: {
    type: String,
    default: null
  }
});

// 组件状态变量
const message = useMessage();
const chartRef = ref<HTMLElement | null>(null);
const chart = ref<echarts.ECharts | null>(null);
const loading = ref(false);
const data = ref<RecordTrend[]>([]);
const period = ref<'day' | 'week' | 'month'>('day');
const metric = ref<'count' | 'score' | 'average'>('count');

// 选项
const periodOptions = [
  { label: '按日', value: 'day' },
  { label: '按周', value: 'week' },
  { label: '按月', value: 'month' }
];

const metricOptions = [
  { label: '记录数', value: 'count' },
  { label: '总分', value: 'score' },
  { label: '平均分', value: 'average' }
];

// 计算属性
const hasData = computed(() => data.value.length > 0);

const chartTitle = computed(() => {
  const metricLabel = metricOptions.find(opt => opt.value === metric.value)?.label || '';
  const periodLabel = periodOptions.find(opt => opt.value === period.value)?.label || '';
  return `${periodLabel}${metricLabel}趋势`;
});

const metricField = computed(() => {
  switch (metric.value) {
    case 'count': return 'record_count';
    case 'score': return 'score_sum';
    case 'average': return 'average_score';
    default: return 'record_count';
  }
});

// 加载趋势数据
const loadTrendsData = async () => {
  loading.value = true;
  
  try {
    const params: Record<string, any> = {
      interval: period.value
    };
    
    if (props.classId) {
      params.class_id = props.classId;
    }
    
    if (props.studentId) {
      params.student_id = props.studentId;
    }
    
    if (props.itemId) {
      params.item_id = props.itemId;
    }
    
    if (props.startDate) {
      params.start_date = props.startDate;
    }
    
    if (props.endDate) {
      params.end_date = props.endDate;
    }

    const userStore = useUserStore();
    
    if (!userStore.isLoggedIn) {
      console.warn('用户未登录，无法获取趋势数据');
      message.warning('请先登录后再查看趋势数据');
      // 使用模拟数据
      const mockResponse = getMockTrendData(period.value);
      data.value = mockResponse.data;
      renderChart();
      return;
    }

    console.log('发送趋势数据请求，参数：', params, '认证状态：', userStore.isLoggedIn ? '已登录' : '未登录');
    
    // 调用API获取真实数据
    const response = await getQuantTrends(params);
    console.log('获取趋势数据响应:', response);

    // API响应格式可能是 { data: { data: RecordTrend[] } } 或 { data: RecordTrend[] }
    if (response) {
      let trendsData: RecordTrend[] = [];
      
      if (response.data && Array.isArray(response.data)) {
        // 直接数组格式: { data: RecordTrend[] }
        trendsData = response.data;
      } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        // 嵌套格式: { data: { data: RecordTrend[] } }
        trendsData = response.data.data;
      }
      
      data.value = trendsData;
      console.log('趋势数据加载成功，数据条数:', data.value.length);
      
      if (data.value.length === 0) {
        message.info('当前条件下没有趋势数据');
      }
      
      renderChart();
    } else {
      console.warn('获取到空数据或格式不正确:', response);
      message.warning('获取到的趋势数据为空');
      data.value = [];
    }

  } catch (error: any) {
    console.error('加载趋势数据失败:', error);
    console.error('错误详情:', error.response?.data || error.message);
    
    let errorMsg = '加载趋势数据失败';
    if (error.response) {
      if (error.response.status === 401) {
        errorMsg += '：未授权，请重新登录';
      } else if (error.response.data && error.response.data.error) {
        errorMsg += `：${error.response.data.error.message || '未知错误'}`;
      }
    }
    
    message.error(errorMsg + '，使用模拟数据显示');
    
    // 使用模拟数据
    const mockResponse = getMockTrendData(period.value);
    data.value = mockResponse.data;
    renderChart();
  } finally {
    loading.value = false;
  }
};

// 渲染图表
const renderChart = () => {
  if (!chartRef.value || !hasData.value) return;
  
  // 确保图表实例已创建
  if (!chart.value) {
    chart.value = echarts.init(chartRef.value);
  }
  
  // 准备数据
  const periods = data.value.map(item => {
    // 格式化日期显示
    if (period.value === 'week' && item.period.includes('-W')) {
      // 处理'2023-W01'格式，转为'2023年第1周'
      const [year, weekPart] = item.period.split('-W');
      const weekNum = parseInt(weekPart, 10);
      return `${year}年第${weekNum}周`;
    } else if (period.value === 'month' && item.period.includes('-')) {
      // 处理'2023-01'格式，转为'2023年1月'
      const [year, month] = item.period.split('-');
      return `${year}年${parseInt(month, 10)}月`;
    }
    return item.period;
  });
  const values = data.value.map(item => Number(item[metricField.value as keyof RecordTrend] || 0));
  
  // 计算移动平均线
  const movingAvg = calculateMovingAverage(values, 3);
  
  // 图表配置
  const option: ECBasicOption = {
    title: {
      text: chartTitle.value,
      left: 'center'
    },
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
      data: [getMetricLabel(metric.value), '3天移动平均'],
      bottom: '0%'
    },
    toolbox: {
      feature: {
        saveAsImage: {}
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: periods,
      axisLabel: {
        rotate: period.value === 'day' ? 45 : 0
      }
    },
    yAxis: {
      type: 'value',
      name: getMetricLabel(metric.value)
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: getMetricLabel(metric.value),
        type: 'bar',
        data: values,
        itemStyle: {
          color: getMetricColor(metric.value)
        },
        markPoint: {
          data: [
            { type: 'max', name: '最大值' },
            { type: 'min', name: '最小值' }
          ]
        }
      },
      {
        name: '3天移动平均',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: movingAvg,
        lineStyle: {
          color: '#f5a623',
          width: 2
        }
      }
    ]
  };
  
  // 设置图表配置
  chart.value.setOption(option);
};

// 计算移动平均线数据
const calculateMovingAverage = (data: number[], windowSize: number) => {
  if (data.length < windowSize) {
    return [];
  }
  
  const result: number[] = [];
  
  // 填充前面的nulls
  for (let i = 0; i < windowSize - 1; i++) {
    result.push(NaN);
  }
  
  for (let i = 0; i <= data.length - windowSize; i++) {
    const windowSum = data.slice(i, i + windowSize).reduce((sum, value) => sum + value, 0);
    const windowAvg = windowSum / windowSize;
    result.push(windowAvg);
  }
  
  return result;
};

// 获取指标标签
const getMetricLabel = (metricType: string): string => {
  switch (metricType) {
    case 'count': return '记录数';
    case 'score': return '总分';
    case 'average': return '平均分';
    default: return '记录数';
  }
};

// 获取指标颜色
const getMetricColor = (metricType: string): string => {
  switch (metricType) {
    case 'count': return '#2080f0';
    case 'score': return '#18a058';
    case 'average': return '#8550e4';
    default: return '#2080f0';
  }
};

// 处理窗口大小变化
const handleResize = () => {
  chart.value?.resize();
};

// 监听数据变化
watch([() => props.classId, () => props.studentId, () => props.itemId, () => props.startDate, () => props.endDate], () => {
  loadTrendsData();
});

// 监听周期和指标变化
watch([period, metric], () => {
  loadTrendsData();
});

// 组件挂载
onMounted(() => {
  loadTrendsData();
  window.addEventListener('resize', handleResize);
});

// 组件卸载
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  chart.value?.dispose();
});
</script>

<style scoped>
.trend-analysis-chart {
  width: 100%;
}

.chart-container {
  height: 400px;
  width: 100%;
}
</style> 