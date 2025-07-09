<template>
  <div class="statistics-panel">
    <n-space vertical size="large">
      <!-- 总体统计卡片 -->
      <n-card title="总体统计" :bordered="false" class="summary-card">
        <n-grid :cols="4" :x-gap="16">
          <n-gi>
            <n-statistic label="总记录数">
              <n-number-animation
                ref="recordCountRef"
                :from="0"
                :to="statistics.total_records || 0"
                :duration="1500"
              />
            </n-statistic>
          </n-gi>
          <n-gi>
            <n-statistic label="总积分">
              <n-number-animation
                ref="totalScoreRef"
                :from="0"
                :to="statistics.total_score || 0"
                :duration="1500"
              />
            </n-statistic>
          </n-gi>
          <n-gi>
            <n-statistic label="平均分">
              <template #value>
                <span class="average-score">{{ formatAverage(statistics.average_score) }}</span>
              </template>
            </n-statistic>
          </n-gi>
          <n-gi>
            <n-statistic label="学生覆盖率">
              <template #value>
                <n-progress
                  type="circle"
                  :percentage="calculateCoverage()"
                  :indicator-text-color="coverageColor"
                  :color="coverageColor"
                  :rail-style="{ stroke: 'rgba(0, 0, 0, 0.05)' }"
                  :stroke-width="10"
                />
              </template>
            </n-statistic>
          </n-gi>
        </n-grid>
      </n-card>

      <!-- 学生排名表格 -->
      <n-card title="学生排名" :bordered="false">
        <template #header-extra>
          <n-space>
            <n-button text @click="refreshRankings">
              <template #icon>
                <n-icon>
                  <RefreshOutlined />
                </n-icon>
              </template>
              刷新
            </n-button>
            <n-button text @click="exportRankings">
              <template #icon>
                <n-icon>
                  <DownloadOutlined />
                </n-icon>
              </template>
              导出
            </n-button>
          </n-space>
        </template>

        <n-data-table
          :columns="rankingColumns"
          :data="studentRankings"
          :loading="loadingRankings"
          :pagination="rankingPagination"
          :row-key="row => row.student_id"
        />
      </n-card>

      <!-- 记录分布图表 -->
      <n-grid :cols="2" :x-gap="16">
        <!-- 按日期分布 -->
        <n-gi>
          <n-card title="记录时间分布" :bordered="false">
            <div ref="dateChartRef" class="chart-container"></div>
          </n-card>
        </n-gi>
        
        <!-- 按项目分布 -->
        <n-gi>
          <n-card title="记录项目分布" :bordered="false">
            <div ref="itemChartRef" class="chart-container"></div>
          </n-card>
        </n-gi>
      </n-grid>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick, onUnmounted, h } from 'vue';
import {
  NSpace,
  NCard,
  NGrid,
  NGi,
  NStatistic,
  NNumberAnimation,
  NProgress,
  NDataTable,
  NButton,
  NIcon,
  useMessage
} from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import { getStudentRankings, getClassStatistics, exportStatisticsData } from '@/services/api/statistics';
import RefreshOutlined from '@vicons/antd/es/RefreshOutlined';
import DownloadOutlined from '@vicons/antd/es/DownloadOutlined';
import * as echarts from 'echarts/core';
import { BarChart, PieChart, LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { StudentRankingItem, ClassStatisticsData } from '@/types/statistics';

// 注册 ECharts 组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  BarChart,
  PieChart,
  LineChart,
  CanvasRenderer
]);

// Props 定义
const props = defineProps({
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
  dateRange: {
    type: Array as () => [string, string] | null,
    default: null
  }
});

// 组件状态
const message = useMessage();
const dateChartRef = ref<HTMLElement | null>(null);
const itemChartRef = ref<HTMLElement | null>(null);
const recordCountRef = ref(null);
const totalScoreRef = ref(null);
const dateChart = ref<echarts.ECharts | null>(null);
const itemChart = ref<echarts.ECharts | null>(null);
const loadingStatistics = ref(false);
const loadingRankings = ref(false);

// 统计数据
const statistics = reactive({
  total_records: 0,
  total_score: 0,
  average_score: 0,
  positive_records: 0,
  negative_records: 0,
  students_with_records: 0,
  total_students: 0,
  date_distribution: [] as { date: string; count: number }[],
  item_distribution: [] as { item_name: string; count: number }[]
});

// 学生排名
const studentRankings = ref<{
  student_id: number;
  student_name: string;
  student_id_no: string;
  class_name: string;
  total_score: number;
  record_count: number;
  rank: number;
}[]>([]);

// 排名表格分页
const rankingPagination = reactive({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page: number) => {
    rankingPagination.page = page;
  },
  onUpdatePageSize: (pageSize: number) => {
    rankingPagination.pageSize = pageSize;
    rankingPagination.page = 1;
  }
});

// 排名表格列定义
const rankingColumns = computed<DataTableColumns>(() => [
  {
    title: '排名',
    key: 'rank',
    width: 60,
    render: (row, index) => {
      const actualIndex = (rankingPagination.page - 1) * rankingPagination.pageSize + index + 1;
      const rankClass = actualIndex <= 3 ? `top-${actualIndex}` : '';
      return h('span', { class: rankClass }, actualIndex);
    }
  },
  {
    title: '学号',
    key: 'student_id_no'
  },
  {
    title: '姓名',
    key: 'student_name'
  },
  {
    title: '班级',
    key: 'class_name'
  },
  {
    title: '总积分',
    key: 'total_score',
    sorter: 'default',
    defaultSortOrder: 'descend',
    render: (row) => {
      return h('span', {
        style: {
          color: row.total_score > 0 ? '#18a058' : row.total_score < 0 ? '#d03050' : ''
        }
      }, row.total_score);
    }
  },
  {
    title: '记录数',
    key: 'record_count'
  }
]);

// 计算学生覆盖率颜色
const coverageColor = computed(() => {
  const coverage = calculateCoverage();
  if (coverage >= 80) return '#18a058';
  if (coverage >= 50) return '#2080f0';
  return '#d03050';
});

// 计算学生覆盖率
const calculateCoverage = () => {
  if (!statistics.total_students) return 0;
  return Math.round((statistics.students_with_records / statistics.total_students) * 100);
};

// 格式化平均分
const formatAverage = (value: number) => {
  return value.toFixed(2);
};

// 初始化日期分布图表
const initDateChart = () => {
  if (!dateChartRef.value) return;
  
  dateChart.value = echarts.init(dateChartRef.value);
  
  const dates = statistics.date_distribution.map(item => item.date);
  const counts = statistics.date_distribution.map(item => item.count);
  
  const option = {
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
      data: dates,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '记录数',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: '#2080f0'
        }
      }
    ]
  };
  
  dateChart.value.setOption(option);
};

// 初始化项目分布图表
const initItemChart = () => {
  if (!itemChartRef.value) return;
  
  itemChart.value = echarts.init(itemChartRef.value);
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 20,
      bottom: 20,
      data: statistics.item_distribution.map(item => item.item_name)
    },
    series: [
      {
        name: '记录分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
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
        data: statistics.item_distribution.map(item => ({
          name: item.item_name,
          value: item.count
        }))
      }
    ]
  };
  
  itemChart.value.setOption(option);
};

// 加载统计数据
const loadStatistics = async () => {
  loadingStatistics.value = true;
  
  try {
    const params: Record<string, any> = {};
    
    if (props.classId) {
      params.class_id = props.classId;
    }
    
    if (props.studentId) {
      params.student_id = props.studentId;
    }
    
    if (props.itemId) {
      params.item_id = props.itemId;
    }
    
    if (props.dateRange) {
      params.start_date = props.dateRange[0];
      params.end_date = props.dateRange[1];
    }
    
    const response = await getClassStatistics(params);
    
    if (response.data && response.data.data) {
      // 更新统计数据
      Object.assign(statistics, response.data.data);
      
      // 初始化图表
      nextTick(() => {
        initDateChart();
        initItemChart();
      });
    }
  } catch (error) {
    console.error('Failed to load statistics:', error);
    message.error('加载统计数据失败');
  } finally {
    loadingStatistics.value = false;
  }
};

// 加载学生排名
const loadRankings = async () => {
  loadingRankings.value = true;
  
  try {
    const params: Record<string, any> = {};
    
    if (props.classId) {
      params.class_id = props.classId;
    }
    
    if (props.dateRange) {
      params.start_date = props.dateRange[0];
      params.end_date = props.dateRange[1];
    }
    
    const response = await getStudentRankings(params);
    
    if (response.data && response.data.data) {
      studentRankings.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load rankings:', error);
    message.error('加载学生排名失败');
  } finally {
    loadingRankings.value = false;
  }
};

// 刷新排名数据
const refreshRankings = () => {
  loadRankings();
};

// 导出统计数据
const exportRankings = async () => {
  try {
    const params: Record<string, any> = {};
    
    if (props.classId) {
      params.class_id = props.classId;
    }
    
    if (props.studentId) {
      params.student_id = props.studentId;
    }
    
    if (props.dateRange) {
      params.start_date = props.dateRange[0];
      params.end_date = props.dateRange[1];
    }
    
    const response = await exportStatisticsData(params);
    
    // 处理下载文件
    const blob = new Blob([response as Blob], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `量化统计_${new Date().toISOString().split('T')[0]}.xlsx`;
    link.click();
    
    message.success('导出成功');
  } catch (error) {
    console.error('Failed to export statistics:', error);
    message.error('导出统计数据失败');
  }
};

// 窗口大小改变时调整图表
const handleResize = () => {
  dateChart.value?.resize();
  itemChart.value?.resize();
};

// 监听筛选条件变化
watch([() => props.classId, () => props.studentId, () => props.itemId, () => props.dateRange], () => {
  loadStatistics();
  loadRankings();
});

// 组件挂载
onMounted(() => {
  loadStatistics();
  loadRankings();
  window.addEventListener('resize', handleResize);
});

// 组件卸载
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  dateChart.value?.dispose();
  itemChart.value?.dispose();
});
</script>

<style scoped>
.statistics-panel {
  width: 100%;
}

.summary-card {
  background-color: #f8fafc;
}

.chart-container {
  height: 320px;
  width: 100%;
}

.average-score {
  font-size: 24px;
  font-weight: bold;
}

.top-1 {
  color: #f5222d;
  font-weight: bold;
}

.top-2 {
  color: #fa8c16;
  font-weight: bold;
}

.top-3 {
  color: #faad14;
  font-weight: bold;
}
</style> 