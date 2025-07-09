<template>
  <div>
    <n-grid :cols="24" :x-gap="16" :y-gap="16">
      <n-grid-item :span="24">
        <n-card title="记录数量时间趋势" class="h-96">
          <div ref="recordCountChartRef" class="chart-container w-full h-80"></div>
        </n-card>
      </n-grid-item>
      
      <n-grid-item :span="24">
        <n-card title="分数时间趋势" class="h-96">
          <div ref="scoreChartRef" class="chart-container w-full h-80"></div>
        </n-card>
      </n-grid-item>
      
      <n-grid-item :span="24">
        <n-card title="分类分布时间趋势" class="h-96">
          <div ref="categoryChartRef" class="chart-container w-full h-80"></div>
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue';
import { NGrid, NGridItem, NCard } from 'naive-ui';
import * as echarts from 'echarts/core';
import { LineChart, BarChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { ECharts } from 'echarts/core';
import dayjs from 'dayjs';

// 注册 ECharts 组件
echarts.use([
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  CanvasRenderer
]);

const props = defineProps({
  timelineData: {
    type: [Object, Array],
    default: () => []
  }
});

const recordCountChartRef = ref<HTMLElement | null>(null);
const scoreChartRef = ref<HTMLElement | null>(null);
const categoryChartRef = ref<HTMLElement | null>(null);
let recordCountChart: ECharts | null = null;
let scoreChart: ECharts | null = null;
let categoryChart: ECharts | null = null;

onMounted(() => {
  initCharts();
  
  // 处理窗口大小变化
  window.addEventListener('resize', handleResize);
});

watch(() => props.timelineData, () => {
  updateCharts();
}, { deep: true });

const handleResize = () => {
  if (recordCountChart) recordCountChart.resize();
  if (scoreChart) scoreChart.resize();
  if (categoryChart) categoryChart.resize();
};

const initCharts = () => {
  // 确保DOM已渲染且有尺寸后再初始化图表
  setTimeout(() => {
    nextTick(() => {
      try {
        console.log('开始初始化时间趋势图表...');
  // 初始化记录数量时间趋势图表
        if (recordCountChartRef.value) {
  recordCountChart = echarts.init(recordCountChartRef.value);
          console.log('记录数量图表初始化成功');
        }
  
  // 初始化分数时间趋势图表
        if (scoreChartRef.value) {
  scoreChart = echarts.init(scoreChartRef.value);
          console.log('分数趋势图表初始化成功');
        }
  
  // 初始化分类分布时间趋势图表
        if (categoryChartRef.value) {
  categoryChart = echarts.init(categoryChartRef.value);
          console.log('分类分布图表初始化成功');
        }
  
  // 更新图表数据
  updateCharts();
      } catch (error) {
        console.error('初始化图表失败:', error);
      }
    });
  }, 100); // 添加短暂延迟确保DOM已完全渲染
};

const updateCharts = () => {
  if (!props.timelineData || !recordCountChart || !scoreChart || !categoryChart) {
    console.warn('图表或数据未准备好，无法更新图表');
    return;
  }
  
  console.log('更新时间趋势图表数据:', props.timelineData);
  
  // 检查数据是否为数组格式
  const timelineArray = Array.isArray(props.timelineData) ? props.timelineData : [];
  
  // 如果是直接数组格式(后端返回的原始格式)，则处理这种情况
  if (timelineArray.length > 0) {
    // 映射字段名称 - 后端可能使用time_period而不是date
    const processedData = timelineArray.map(item => ({
      date: item.time_period || item.date || '',
      count: item.record_count || item.count || 0,
      score: item.total_score || item.score || 0,
      avg_score: item.avg_score || 0,
      positive: item.positive_count || item.positive || 0,
      negative: item.negative_count || item.negative || 0
    }));
    
    // 根据日期排序
    processedData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    
    // 提取日期和对应的值
    const dates = processedData.map(item => item.date);
    const recordCounts = processedData.map(item => item.count);
    const scores = processedData.map(item => item.score);
    const avgScores = processedData.map(item => item.avg_score);
    
    console.log('处理后的时间趋势数据:', {
      dates,
      recordCounts,
      scores,
      avgScores
    });
    
    // 更新记录数图表
    recordCountChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates.map(date => dayjs(date).format('MM-DD')),
        axisLabel: {
          interval: Math.floor(dates.length / 15),
          rotate: 30
        }
      },
      yAxis: {
        type: 'value',
        name: '记录数'
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          type: 'slider',
          start: 0,
          end: 100
        }
      ],
      series: [
        {
          name: '记录数',
          type: 'line',
          data: recordCounts,
          smooth: true,
          markPoint: {
            data: [
              { type: 'max', name: '最大值' },
              { type: 'min', name: '最小值' }
            ]
          },
          markLine: {
            data: [
              { type: 'average', name: '平均值' }
            ]
          },
          areaStyle: {
            opacity: 0.2
          },
          itemStyle: {
            color: '#3366FF'
          }
        }
      ]
    });
    
    // 更新分数图表
    scoreChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['总分', '平均分'],
        right: 10,
        top: 10
      },
      xAxis: {
        type: 'category',
        data: dates.map(date => dayjs(date).format('MM-DD')),
        axisLabel: {
          interval: Math.floor(dates.length / 15),
          rotate: 30
        }
      },
      yAxis: {
        type: 'value',
        name: '分数'
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          type: 'slider',
          start: 0,
          end: 100
        }
      ],
      series: [
        {
          name: '总分',
          type: 'line',
          data: scores,
          smooth: true,
          itemStyle: {
            color: '#3366FF'
          },
          z: 3
        },
        {
          name: '平均分',
          type: 'line',
          data: avgScores,
          smooth: true,
          itemStyle: {
            color: '#52C41A'
          },
          z: 2
        }
      ]
    });
    
    // 创建一个基本的分类图表，即使没有分类数据
    categoryChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: dates.map(date => dayjs(date).format('MM-DD')),
        axisLabel: {
          interval: Math.floor(dates.length / 15),
          rotate: 30
        }
      },
      yAxis: {
        type: 'value',
        name: '记录数/分数'
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          type: 'slider',
          start: 0,
          end: 100
        }
      ],
      series: [
        {
          name: '记录数',
          type: 'bar',
          data: recordCounts,
          itemStyle: {
            color: '#3366FF'
          }
        },
        {
          name: '总分',
          type: 'line',
          data: scores,
          smooth: true,
          itemStyle: {
            color: '#F5222D'
          },
          z: 3
        }
      ]
    });
    
    return;
  }
  
  // 以下是处理旧格式的数据（现在作为备用）
  const timelineObj = typeof props.timelineData === 'object' && !Array.isArray(props.timelineData) 
    ? props.timelineData 
    : {};
    
  const record_count_trend = timelineObj.record_count_trend || {};
  const score_trend = timelineObj.score_trend || {};
  const category_trend = timelineObj.category_trend || {};
  
  if (Object.keys(record_count_trend).length > 0) {
    // 准备记录数量时间趋势数据
    const dates = Object.keys(record_count_trend).sort();
    const values = dates.map(date => record_count_trend[date]);
    
    recordCountChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates.map(date => dayjs(date).format('MM-DD')),
        axisLabel: {
          interval: Math.floor(dates.length / 15),
          rotate: 30
        }
      },
      yAxis: {
        type: 'value',
        name: '记录数'
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          type: 'slider',
          start: 0,
          end: 100
        }
      ],
      series: [
        {
          name: '记录数',
          type: 'line',
          data: values,
          smooth: true,
          markPoint: {
            data: [
              { type: 'max', name: '最大值' },
              { type: 'min', name: '最小值' }
            ]
          },
          markLine: {
            data: [
              { type: 'average', name: '平均值' }
            ]
          },
          areaStyle: {
            opacity: 0.2
          },
          itemStyle: {
            color: '#3366FF'
          }
        }
      ]
    });
  }
  
  if (Object.keys(score_trend).length > 0) {
    // 准备分数时间趋势数据
    const dates = Object.keys(score_trend).sort();
    const positiveValues = dates.map(date => score_trend[date]?.positive || 0);
    const negativeValues = dates.map(date => score_trend[date]?.negative || 0);
    const totalValues = dates.map(date => score_trend[date]?.total || 0);
    
    scoreChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['总分', '加分', '减分'],
        right: 10,
        top: 10
      },
      xAxis: {
        type: 'category',
        data: dates.map(date => dayjs(date).format('MM-DD')),
        axisLabel: {
          interval: Math.floor(dates.length / 15),
          rotate: 30
        }
      },
      yAxis: {
        type: 'value',
        name: '分数'
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          type: 'slider',
          start: 0,
          end: 100
        }
      ],
      series: [
        {
          name: '总分',
          type: 'line',
          data: totalValues,
          smooth: true,
          itemStyle: {
            color: '#3366FF'
          },
          z: 3
        },
        {
          name: '加分',
          type: 'line',
          data: positiveValues,
          smooth: true,
          itemStyle: {
            color: '#52C41A'
          },
          z: 2
        },
        {
          name: '减分',
          type: 'line',
          data: negativeValues,
          smooth: true,
          itemStyle: {
            color: '#F5222D'
          },
          z: 1
        }
      ]
    });
  }
  
  if (Object.keys(category_trend).length > 0) {
    // 准备分类分布时间趋势数据
    const dates = Object.keys(category_trend).sort();
    const categories: string[] = [];
    const seriesData: Record<string, number[]> = {};
    
    // 收集所有分类
    dates.forEach(date => {
      Object.keys(category_trend[date] || {}).forEach(category => {
        if (!categories.includes(category)) {
          categories.push(category);
          seriesData[category] = [];
        }
      });
    });
    
    // 准备每个分类的数据
    categories.forEach(category => {
      dates.forEach(date => {
        seriesData[category].push(category_trend[date]?.[category] || 0);
      });
    });
    
    // 构建 series 配置
    const series = categories.map(category => ({
      name: category,
      type: 'bar',
      stack: '总量',
      data: seriesData[category],
      emphasis: {
        focus: 'series'
      }
    }));
    
    categoryChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: categories,
        right: 10,
        top: 10
      },
      xAxis: {
        type: 'category',
        data: dates.map(date => dayjs(date).format('MM-DD')),
        axisLabel: {
          interval: Math.floor(dates.length / 15),
          rotate: 30
        }
      },
      yAxis: {
        type: 'value',
        name: '数量'
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          type: 'slider',
          start: 0,
          end: 100
        }
      ],
      series
    });
  }
};

onUnmounted(() => {
  // 在组件卸载时释放资源
  window.removeEventListener('resize', handleResize);
  
  if (recordCountChart) {
    recordCountChart.dispose();
    recordCountChart = null;
  }
  
  if (scoreChart) {
    scoreChart.dispose();
    scoreChart = null;
  }
  
  if (categoryChart) {
    categoryChart.dispose();
    categoryChart = null;
  }
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 320px;
  min-height: 300px;
}
</style>
