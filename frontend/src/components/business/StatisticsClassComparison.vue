<template>
  <div>
    <n-grid :cols="24" :x-gap="16" :y-gap="16">
      <n-grid-item :span="24">
        <n-card title="班级总分对比" class="h-96">
          <div ref="totalScoreChartRef" class="chart-container w-full h-80"></div>
        </n-card>
      </n-grid-item>
      
      <n-grid-item :span="24" :lg="12">
        <n-card title="班级平均分对比" class="h-96">
          <div ref="avgScoreChartRef" class="chart-container w-full h-80"></div>
        </n-card>
      </n-grid-item>
      
      <n-grid-item :span="24" :lg="12">
        <n-card title="班级记录数对比" class="h-96">
          <div ref="recordCountChartRef" class="chart-container w-full h-80"></div>
        </n-card>
      </n-grid-item>
    </n-grid>
    
    <n-card title="班级详情对比" class="mt-6">
      <n-data-table
        :columns="columns"
        :data="tableData"
        :bordered="false"
        striped
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, onUnmounted, nextTick } from 'vue';
import { NGrid, NGridItem, NCard, NDataTable } from 'naive-ui';
import * as echarts from 'echarts/core';
import { BarChart, PieChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { ECharts } from 'echarts/core';
import { useThemeStore } from '@/stores/theme';

// 注册 ECharts 组件
echarts.use([
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  CanvasRenderer
]);

interface ClassData {
  class_id?: number;
  id?: number;
  name?: string;
  class_name?: string;
  grade?: string;
  student_count: number;
  record_count: number;
  total_score: number;
  avg_score?: number;
  avg_records?: number;
  max_score?: number;
  min_score?: number;
}

const props = defineProps({
  comparisonData: {
    type: Object,
    default: () => ({})
  }
});

// 获取主题状态
const themeStore = useThemeStore();
const isDarkMode = computed(() => themeStore.darkMode);

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

const totalScoreChartRef = ref<HTMLElement | null>(null);
const avgScoreChartRef = ref<HTMLElement | null>(null);
const recordCountChartRef = ref<HTMLElement | null>(null);
let totalScoreChart: ECharts | null = null;
let avgScoreChart: ECharts | null = null;
let recordCountChart: ECharts | null = null;
let resizeHandler: (() => void) | null = null;

// 表格列定义
const columns = [
  {
    title: '班级',
    key: 'class_name'
  },
  {
    title: '总学生数',
    key: 'student_count',
    sorter: (a: ClassData, b: ClassData) => a.student_count - b.student_count
  },
  {
    title: '总记录数',
    key: 'record_count',
    sorter: (a: ClassData, b: ClassData) => a.record_count - b.record_count
  },
  {
    title: '总分',
    key: 'total_score',
    sorter: (a: ClassData, b: ClassData) => a.total_score - b.total_score
  },
  {
    title: '人均分',
    key: 'avg_score',
    sorter: (a: ClassData, b: ClassData) => (a.avg_score || 0) - (b.avg_score || 0),
    render: (row: ClassData) => (row.avg_score || 0).toFixed(1)
  },
  {
    title: '人均记录数',
    key: 'avg_records',
    sorter: (a: ClassData, b: ClassData) => (a.avg_records || 0) - (b.avg_records || 0),
    render: (row: { avg_records: number }) => row.avg_records.toFixed(1)
  },
  {
    title: '最高分',
    key: 'max_score',
    sorter: (a: ClassData, b: ClassData) => (a.max_score || 0) - (b.max_score || 0)
  },
  {
    title: '最低分',
    key: 'min_score',
    sorter: (a: ClassData, b: ClassData) => (a.min_score || 0) - (b.min_score || 0)
  }
];

// 处理表格数据
const tableData = computed(() => {
  if (!props.comparisonData.classes) return [];
  
  return Object.values(props.comparisonData.classes).map((cls: any) => ({
    ...cls,
    avg_score: cls.total_score / (cls.student_count || 1),
    avg_records: cls.record_count / (cls.student_count || 1)
  }));
});

// 初始化图表
onMounted(() => {
  // 延迟初始化图表，确保DOM已经完全渲染，防止宽高为0
  setTimeout(() => {
  initCharts();
  }, 300);
});

// 监听数据变化，更新图表
watch(() => props.comparisonData, () => {
  // 确保图表实例已创建后再更新
  if (totalScoreChart && avgScoreChart && recordCountChart) {
  updateCharts();
  } else {
    // 图表未初始化，尝试重新初始化
    nextTick(() => {
      if (!totalScoreChart || !avgScoreChart || !recordCountChart) {
        console.log('图表尚未初始化，重新尝试初始化...');
        initCharts();
      }
    });
  }
}, { deep: true });

// 监听主题变化，重新初始化图表
watch(isDarkMode, () => {
  // 当主题改变时，重新初始化所有图表
  console.log('主题已变更，重新初始化图表...');
  
  // 清理旧图表实例
  if (totalScoreChart) {
    totalScoreChart.dispose();
    totalScoreChart = null;
  }
  
  if (avgScoreChart) {
    avgScoreChart.dispose();
    avgScoreChart = null;
  }
  
  if (recordCountChart) {
    recordCountChart.dispose();
    recordCountChart = null;
  }
  
  // 重新初始化
  nextTick(() => {
    initCharts();
  });
});

const initCharts = () => {
  console.log('开始初始化班级对比图表...');

  try {
    // 确保DOM元素存在且已渲染
    if (!totalScoreChartRef.value || !avgScoreChartRef.value || !recordCountChartRef.value) {
      console.warn('图表容器DOM元素尚未就绪，稍后重试');
      setTimeout(initCharts, 200);
      return;
    }

  // 初始化总分对比图表
    if (!totalScoreChart && totalScoreChartRef.value) {
  totalScoreChart = echarts.init(totalScoreChartRef.value);
    }
  
  // 初始化平均分对比图表
    if (!avgScoreChart && avgScoreChartRef.value) {
  avgScoreChart = echarts.init(avgScoreChartRef.value);
    }
  
  // 初始化记录数对比图表
    if (!recordCountChart && recordCountChartRef.value) {
  recordCountChart = echarts.init(recordCountChartRef.value);
    }
  
  // 更新图表数据
  updateCharts();
  
    // 处理窗口大小变化，使用单一的事件处理器引用以便清理
    resizeHandler = () => {
      if (totalScoreChart) totalScoreChart.resize();
      if (avgScoreChart) avgScoreChart.resize();
      if (recordCountChart) recordCountChart.resize();
    };
    
    window.addEventListener('resize', resizeHandler);
    console.log('班级对比图表初始化完成');
  } catch (error) {
    console.error('初始化图表失败:', error);
  }
};

const updateCharts = () => {
  console.log('更新班级对比图表数据...');
  
  if (!props.comparisonData.classes) {
    console.warn('没有班级数据可供图表显示');
    return;
  }
  
  if (!totalScoreChart || !avgScoreChart || !recordCountChart) {
    console.warn('图表尚未初始化，无法更新数据');
    return;
  }
  
  try {
    const classData = Array.isArray(props.comparisonData.classes) 
      ? props.comparisonData.classes 
      : Object.values(props.comparisonData.classes);
      
    if (!classData.length) {
      console.warn('班级数据为空数组');
      return;
    }
    
    const classNames = classData.map((cls: ClassData) => cls.name || cls.class_name || '未命名班级');
  
  // 更新总分对比图表
  totalScoreChart.setOption({
      ...getChartTheme.value,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: classNames,
      axisLabel: {
        interval: 0,
          rotate: 30,
          ...(getChartTheme.value.xAxis?.axisLabel || {})
        },
        axisLine: {
          ...(getChartTheme.value.xAxis?.axisLine || {})
      }
    },
    yAxis: {
      type: 'value',
        name: '分数',
        axisLabel: {
          ...(getChartTheme.value.yAxis?.axisLabel || {})
        },
        axisLine: {
          ...(getChartTheme.value.yAxis?.axisLine || {})
        },
        splitLine: {
          ...(getChartTheme.value.yAxis?.splitLine || {})
        }
    },
    series: [
      {
        name: '总分',
        type: 'bar',
          data: classData.map((cls: ClassData) => cls.total_score || 0),
        itemStyle: {
            color: isDarkMode.value ? '#409EFF' : '#3366FF'
        }
      }
    ]
  });
  
  // 更新平均分对比图表
  avgScoreChart.setOption({
      ...getChartTheme.value,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: classNames,
      axisLabel: {
        interval: 0,
          rotate: 30,
          ...(getChartTheme.value.xAxis?.axisLabel || {})
        },
        axisLine: {
          ...(getChartTheme.value.xAxis?.axisLine || {})
      }
    },
    yAxis: {
      type: 'value',
        name: '平均分',
        axisLabel: {
          ...(getChartTheme.value.yAxis?.axisLabel || {})
        },
        axisLine: {
          ...(getChartTheme.value.yAxis?.axisLine || {})
        },
        splitLine: {
          ...(getChartTheme.value.yAxis?.splitLine || {})
        }
    },
    series: [
      {
        name: '平均分',
        type: 'bar',
          data: classData.map((cls: ClassData) => {
            if (!cls.student_count) return 0;
            return +(cls.total_score / cls.student_count).toFixed(1);
          }),
        itemStyle: {
            color: isDarkMode.value ? '#67C23A' : '#52C41A'
        }
      }
    ]
  });
  
  // 更新记录数对比图表
  recordCountChart.setOption({
      ...getChartTheme.value,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: classNames,
      axisLabel: {
        interval: 0,
          rotate: 30,
          ...(getChartTheme.value.xAxis?.axisLabel || {})
        },
        axisLine: {
          ...(getChartTheme.value.xAxis?.axisLine || {})
      }
    },
    yAxis: {
      type: 'value',
        name: '记录数',
        axisLabel: {
          ...(getChartTheme.value.yAxis?.axisLabel || {})
        },
        axisLine: {
          ...(getChartTheme.value.yAxis?.axisLine || {})
        },
        splitLine: {
          ...(getChartTheme.value.yAxis?.splitLine || {})
        }
    },
    series: [
      {
        name: '记录数',
        type: 'bar',
          data: classData.map((cls: ClassData) => cls.record_count || 0),
        itemStyle: {
            color: isDarkMode.value ? '#E6A23C' : '#FA8C16'
        }
      }
    ]
  });
    
    console.log('班级对比图表数据更新完成');
  } catch (error) {
    console.error('更新图表数据时出错:', error);
  }
};

onUnmounted(() => {
  console.log('班级对比组件卸载，清理资源...');
  
  // 移除事件监听器
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler);
    resizeHandler = null;
  }
  
  // 释放图表实例
  if (totalScoreChart) {
    totalScoreChart.dispose();
    totalScoreChart = null;
  }
  
  if (avgScoreChart) {
    avgScoreChart.dispose();
    avgScoreChart = null;
  }
  
  if (recordCountChart) {
    recordCountChart.dispose();
    recordCountChart = null;
  }
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
  position: relative;
}
</style>
