<template>
  <div class="data-visualization-dashboard">
    <n-space vertical :size="16">
      <!-- WebSocket连接状态 -->
      <n-alert v-if="!isConnected && wsStore.config.enabled" type="warning" closable>
        实时更新已断开，点击
        <n-button text type="primary" @click="reconnect">重新连接</n-button>
        以获取最新数据。
      </n-alert>
      
      <n-alert v-if="hasDashboardUpdate" type="info" closable @close="refreshDashboard">
        仪表盘数据有更新，点击刷新或关闭此提示自动刷新。
      </n-alert>
      
      <!-- 过滤器面板 -->
      <n-card title="筛选条件" class="filter-card">
        <n-grid :cols="24" :x-gap="16">
          <n-gi :span="6">
            <n-form-item label="班级">
              <n-select
                v-model:value="filter.classId"
                clearable
                filterable
                placeholder="选择班级"
                :options="classOptions"
                :loading="loadingClasses"
                @update:value="handleClassChange"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="6">
            <n-form-item label="学生">
              <n-select
                v-model:value="filter.studentId"
                clearable
                filterable
                placeholder="选择学生"
                :options="studentOptions"
                :loading="loadingStudents"
                :disabled="!filter.classId"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="6">
            <n-form-item label="量化项目">
              <n-select
                v-model:value="filter.itemId"
                clearable
                filterable
                placeholder="选择量化项目"
                :options="itemOptions"
                :loading="loadingItems"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="6">
            <n-form-item label="日期范围">
              <n-date-picker
                v-model:value="filter.dateRange"
                type="daterange"
                clearable
                style="width: 100%"
              />
            </n-form-item>
          </n-gi>
        </n-grid>
        
        <div class="filter-actions">
          <n-space>
            <n-switch v-model:value="realtimeEnabled" @update:value="toggleRealtimeUpdates">
              <template #checked>实时更新: 开</template>
              <template #unchecked>实时更新: 关</template>
            </n-switch>
            <n-button @click="resetFilters">重置</n-button>
            <n-button type="primary" @click="applyFilters" :loading="loading">
              应用筛选
            </n-button>
          </n-space>
        </div>
      </n-card>
      
      <!-- 数据摘要卡片 -->
      <n-grid :cols="24" :x-gap="16" :y-gap="16">
        <n-gi :span="6">
          <n-card class="stat-card">
            <n-statistic label="总记录数" :value="statistics.total_records ?? 0">
              <template #prefix>
                <n-icon><FormOutlined /></n-icon>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
        
        <n-gi :span="6">
          <n-card class="stat-card">
            <n-statistic label="总积分" :value="statistics.total_score ?? 0">
              <template #prefix>
                <n-icon><StarOutlined /></n-icon>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
        
        <n-gi :span="6">
          <n-card class="stat-card">
            <n-statistic label="平均分" :value="formattedAverage">
              <template #prefix>
                <n-icon><CalculatorOutlined /></n-icon>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
        
        <n-gi :span="6">
          <n-card class="stat-card">
            <n-statistic label="覆盖学生" :value="`${statistics.students_with_records ?? 0}/${statistics.total_students ?? 0}`">
              <template #prefix>
                <n-icon><TeamOutlined /></n-icon>
              </template>
              <template #suffix>
                <n-text depth="3">
                  ({{ formattedCoverageRate }})
                </n-text>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
      </n-grid>
      
      <!-- 趋势图和分布图 -->
      <n-grid :cols="24" :x-gap="16" :y-gap="16">
        <!-- 趋势图 -->
        <n-gi :span="12">
          <trend-analysis-chart
            :class-id="appliedFilter.classId || undefined"
            :student-id="appliedFilter.studentId || undefined"
            :item-id="appliedFilter.itemId || undefined"
            :start-date="startDateString || undefined"
            :end-date="endDateString || undefined"
          />
        </n-gi>
        
        <!-- 项目分布饼图 -->
        <n-gi :span="12">
          <n-card title="量化项目分布" :bordered="false">
            <div class="chart-container" ref="pieChartRef"></div>
            <n-empty v-if="!hasDistributionData" description="暂无数据" />
          </n-card>
        </n-gi>
        
        <!-- 正负分布 -->
        <n-gi :span="8">
          <n-card title="正负分布" :bordered="false">
            <div class="chart-container small-chart" ref="gaugeChartRef"></div>
            <n-empty v-if="!hasDistributionData" description="暂无数据" />
          </n-card>
        </n-gi>
        
        <!-- 学生排名Top5 -->
        <n-gi :span="16">
          <n-card title="学生排名Top5" :bordered="false">
            <n-data-table
              :columns="rankColumns"
              :data="topStudents"
              :pagination="false"
              :bordered="false"
            />
          </n-card>
        </n-gi>
      </n-grid>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, h, watch } from 'vue';
import {
  NSpace,
  NCard,
  NGrid,
  NGi,
  NFormItem,
  NSelect,
  NDatePicker,
  NButton,
  NStatistic,
  NIcon,
  NDataTable,
  NEmpty,
  NText,
  NSwitch,
  NAlert,
  useMessage
} from 'naive-ui';
import * as echarts from 'echarts/core';
import { PieChart, GaugeChart } from 'echarts/charts';
import { 
  TitleComponent, 
  TooltipComponent, 
  LegendComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import FormOutlined from '@vicons/antd/es/FormOutlined';
import StarOutlined from '@vicons/antd/es/StarOutlined';
import CalculatorOutlined from '@vicons/antd/es/CalculatorOutlined';
import TeamOutlined from '@vicons/antd/es/TeamOutlined';
import TrendAnalysisChart from '@/components/business/TrendAnalysisChart.vue';
import { getClasses } from '@/services/api/classes';
import { getStudents } from '@/services/api/students';
import { getQuantItems } from '@/services/api/quant-items';
import { 
  getStatisticsSummary, 
  getStudentRankings,
  getClassStatistics
} from '@/services/api/statistics';
import { 
  getMockClasses, 
  getMockQuantItems, 
  getMockStatisticsSummary, 
  getMockStudentRankings 
} from '@/services/api/mock-dashboard';
import type { StudentRankingItem, StatisticsSummary } from '@/types/statistics';
import type { DataTableColumn } from 'naive-ui';
import { useRealtimeUpdates } from '@/composables/useRealtimeUpdates';
import { useWebSocketStore } from '@/stores/websocket';

// 注册ECharts组件
echarts.use([
  PieChart,
  GaugeChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  CanvasRenderer
]);

// 状态变量
const message = useMessage();
const loading = ref(false);
const loadingClasses = ref(false);
const loadingStudents = ref(false);
const loadingItems = ref(false);
const pieChartRef = ref<HTMLElement | null>(null);
const gaugeChartRef = ref<HTMLElement | null>(null);
const pieChart = ref<echarts.ECharts | null>(null);
const gaugeChart = ref<echarts.ECharts | null>(null);

// WebSocket状态
const wsStore = useWebSocketStore();
const {
  isConnected,
  hasDashboardUpdate,
  enableRealtimeUpdates,
  disableRealtimeUpdates,
  resetUpdateFlags,
  reconnect
} = useRealtimeUpdates();

// 实时更新开关
const realtimeEnabled = ref(wsStore.config.enabled);

// 切换实时更新
const toggleRealtimeUpdates = (value: boolean) => {
  if (value) {
    enableRealtimeUpdates();
  } else {
    disableRealtimeUpdates();
  }
};

// 刷新仪表盘数据
const refreshDashboard = () => {
  loadDashboardData();
  resetUpdateFlags();
};

// 监听实时更新标志
watch(hasDashboardUpdate, (hasUpdate) => {
  if (hasUpdate && realtimeEnabled.value) {
    // 自动刷新
    refreshDashboard();
  }
});

// 数据源
const classes = ref<{ id: number; name: string }[]>([]);
const students = ref<{ id: number; student_id_no: string; full_name: string }[]>([]);
const items = ref<{ id: number; name: string; category?: string }[]>([]);
const topStudents = ref<StudentRankingItem[]>([]);
const statistics = ref<StatisticsSummary>({
  total_students: 0,
  total_records: 0,
  total_items: 0,
  total_score: 0,
  monthly_records: 0,
  average_score: 0,
  students_with_records: 0,
  positive_percentage: 0,
  negative_percentage: 0,
  neutral_percentage: 0,
  categories: [],
  itemDistribution: []
});

const distributionData = ref<Array<{ item_id: number; item_name: string; count: number; score_sum: number }>>([]);

// 筛选条件
const filter = reactive({
  classId: null as number | null,
  studentId: null as number | null,
  itemId: null as number | null,
  dateRange: null as [number, number] | null
});

// 已应用的筛选条件
const appliedFilter = reactive({
  classId: null as number | null,
  studentId: null as number | null,
  itemId: null as number | null,
  dateRange: null as [number, number] | null
});

// 计算属性：选项
const classOptions = computed(() => 
  classes.value.map(cls => ({
    label: cls.name,
    value: cls.id
  }))
);

const studentOptions = computed(() => 
  students.value.map(student => ({
    label: `${student.student_id_no} - ${student.full_name}`,
    value: student.id
  }))
);

const itemOptions = computed(() => 
  items.value.map(item => ({
    label: `${item.name}${item.category ? ` (${item.category})` : ''}`,
    value: item.id
  }))
);

// 学生排名列定义
const rankColumns = computed(() => [
  {
    title: '排名',
    key: 'rank',
    width: 80
  },
  {
    title: '学号',
    key: 'student_id_no',
    width: 120
  },
  {
    title: '姓名',
    key: 'name',
    width: 100
  },
  {
    title: '班级',
    key: 'class_name'
  },
  {
    title: '总积分',
    key: 'total_score',
    width: 100,
    render: (row: any) => {
      const scoreClass = row.total_score > 0 ? 'positive-score' : row.total_score < 0 ? 'negative-score' : '';
      return h('span', { class: scoreClass }, row.total_score);
    }
  },
  {
    title: '记录数',
    key: 'record_count',
    width: 80
  }
]);

// 是否有分布数据
const hasDistributionData = computed(() => {
  return distributionData.value && Array.isArray(distributionData.value) && distributionData.value.length > 0;
});

// 格式化平均分
const formattedAverage = computed(() => {
  if (!statistics.value || statistics.value.average_score === undefined || statistics.value.average_score === null) {
    return '0.00';
  }
  return statistics.value.average_score.toFixed(2);
});

// 格式化覆盖率
const formattedCoverageRate = computed(() => {
  if (!statistics.value || 
      statistics.value.total_students === undefined || 
      statistics.value.total_students === null ||
      statistics.value.students_with_records === undefined ||
      statistics.value.students_with_records === null ||
      statistics.value.total_students === 0) {
    return '0%';
  }
  return `${Math.round(statistics.value.students_with_records / statistics.value.total_students * 100)}%`;
});

// 日期字符串
const startDateString = computed(() => {
  if (!appliedFilter.dateRange) return null;
  return new Date(appliedFilter.dateRange[0]).toISOString().split('T')[0];
});

const endDateString = computed(() => {
  if (!appliedFilter.dateRange) return null;
  return new Date(appliedFilter.dateRange[1]).toISOString().split('T')[0];
});

// 调试函数
const debugApiResponse = (label: string, response: any) => {
  console.log(`[调试] ${label}:`, response);
  if (response) {
    console.log(`[调试] ${label} 类型:`, typeof response);
    if (typeof response === 'object') {
      console.log(`[调试] ${label} 键:`, Object.keys(response));
      if ('data' in response) {
        console.log(`[调试] ${label}.data 类型:`, typeof response.data);
        console.log(`[调试] ${label}.data 值:`, response.data);
      }
    }
  }
};

// 加载班级数据
const loadClasses = async () => {
  loadingClasses.value = true;
  try {
    const response = await getClasses();
    debugApiResponse('班级数据响应', response);
    
    // 处理不同的响应格式情况
    let classData;
    if (Array.isArray(response)) {
      classData = response;
    } else if (response && typeof response === 'object') {
      if (Array.isArray(response.data)) {
        classData = response.data;
      } else if (response.data && Array.isArray(response.data.data)) {
        classData = response.data.data;
      }
    }
    
    if (classData && Array.isArray(classData)) {
      classes.value = classData;
      console.log('加载到班级数据:', classes.value.length, '条');
    } else {
      throw new Error('班级数据格式不正确');
    }
  } catch (error) {
    console.error('Failed to load classes:', error);
    message.error('加载班级数据失败，使用模拟数据');
    
    // 加载失败时使用模拟数据作为后备
    const mockResponse = getMockClasses();
    classes.value = mockResponse.data;
    console.log('使用模拟班级数据:', classes.value.length, '条');
  } finally {
    loadingClasses.value = false;
  }
};

// 加载学生数据
const loadStudentsByClass = async (classId: number) => {
  loadingStudents.value = true;
  try {
    const response = await getStudents({ class_id: classId, page_size: 1000 });
    debugApiResponse('学生数据响应', response);
    
    // 处理不同的响应格式情况
    let studentsData;
    if (Array.isArray(response)) {
      studentsData = response;
    } else if (response && typeof response === 'object') {
      if (Array.isArray(response.data)) {
        studentsData = response.data;
      } else if (response.data && Array.isArray(response.data.data)) {
        studentsData = response.data.data;
      }
    }
    
    if (studentsData && Array.isArray(studentsData)) {
      students.value = studentsData;
      console.log('加载到学生数据:', students.value.length, '条');
    } else {
      throw new Error('学生数据格式不正确');
    }
  } catch (error) {
    console.error('Failed to load students:', error);
    message.error('加载学生数据失败，使用模拟数据');
    
    // 加载失败时使用模拟数据作为后备
    const mockStudents = Array.from({ length: 20 }, (_, i) => ({
      id: classId * 100 + i + 1,
      student_id_no: `S${classId}${(i + 1).toString().padStart(2, '0')}`,
      full_name: `学生${classId}-${i + 1}`,
      class_id: classId
    }));
    students.value = mockStudents;
    console.log('使用模拟学生数据:', students.value.length, '条');
  } finally {
    loadingStudents.value = false;
  }
};

// 加载量化项目数据
const loadItems = async () => {
  loadingItems.value = true;
  try {
    const response = await getQuantItems();
    debugApiResponse('量化项目响应', response);
    
    // 处理不同的响应格式情况
    let itemsData;
    if (Array.isArray(response)) {
      itemsData = response;
    } else if (response && typeof response === 'object') {
      if (Array.isArray(response.data)) {
        itemsData = response.data;
      } else if (response.data && Array.isArray(response.data.data)) {
        itemsData = response.data.data;
      }
    }
    
    if (itemsData && Array.isArray(itemsData)) {
      items.value = itemsData;
      console.log('加载到量化项目数据:', items.value.length, '条');
    } else {
      throw new Error('量化项目数据格式不正确');
    }
  } catch (error) {
    console.error('Failed to load quant items:', error);
    message.error('加载量化项目失败，使用模拟数据');
    
    // 加载失败时使用模拟数据作为后备
    const mockResponse = getMockQuantItems();
    items.value = mockResponse.data;
    console.log('使用模拟量化项目数据:', items.value.length, '条');
  } finally {
    loadingItems.value = false;
  }
};

// 处理班级变更
const handleClassChange = (value: number | null) => {
  filter.classId = value;
  filter.studentId = null;
  
  if (value) {
    loadStudentsByClass(value);
  } else {
    students.value = [];
  }
};

// 应用筛选条件
const applyFilters = () => {
  // 复制当前筛选条件到已应用的筛选条件
  appliedFilter.classId = filter.classId;
  appliedFilter.studentId = filter.studentId;
  appliedFilter.itemId = filter.itemId;
  appliedFilter.dateRange = filter.dateRange ? [...filter.dateRange] : null;
  
  // 加载数据
  loadDashboardData();
};

// 重置筛选条件
const resetFilters = () => {
  filter.classId = null;
  filter.studentId = null;
  filter.itemId = null;
  filter.dateRange = null;
  
  // 重置已应用的筛选条件
  appliedFilter.classId = null;
  appliedFilter.studentId = null;
  appliedFilter.itemId = null;
  appliedFilter.dateRange = null;
  
  // 重新加载数据
  loadDashboardData();
};

// 加载仪表盘数据
const loadDashboardData = async () => {
  loading.value = true;
  
  try {
    // 准备请求参数
    const params: Record<string, any> = {};
    
    if (appliedFilter.classId) {
      params.class_id = appliedFilter.classId;
    }
    
    if (appliedFilter.studentId) {
      params.student_id = appliedFilter.studentId;
    }
    
    if (appliedFilter.itemId) {
      params.item_id = appliedFilter.itemId;
    }
    
    if (appliedFilter.dateRange) {
      params.start_date = startDateString.value;
      params.end_date = endDateString.value;
    }
    
    console.log('仪表盘请求参数:', params);
    
    // 获取统计摘要
    const summaryResponse = await getStatisticsSummary(params);
    debugApiResponse('统计摘要响应', summaryResponse);
    
    // 处理不同的响应格式情况
    let summaryData;
    if (summaryResponse && typeof summaryResponse === 'object') {
      if ('data' in summaryResponse) {
        if (typeof summaryResponse.data === 'object') {
          if ('data' in summaryResponse.data) {
            summaryData = summaryResponse.data.data;
          } else {
            summaryData = summaryResponse.data;
          }
        }
      } else {
        summaryData = summaryResponse;
      }
    }
    
    if (summaryData) {
      statistics.value = summaryData;
      console.log('加载到统计摘要:', statistics.value);
    } else {
      throw new Error('统计摘要数据格式不正确');
    }
    
    // 获取学生排名Top5
    const rankingParams = { ...params, limit: 5 };
    const rankingResponse = await getStudentRankings(rankingParams);
    debugApiResponse('学生排名响应', rankingResponse);
    
    // 处理不同的响应格式情况
    let rankingData;
    if (Array.isArray(rankingResponse)) {
      rankingData = rankingResponse;
    } else if (rankingResponse && typeof rankingResponse === 'object') {
      if (Array.isArray(rankingResponse.data)) {
        rankingData = rankingResponse.data;
      } else if (rankingResponse.data && Array.isArray(rankingResponse.data.data)) {
        rankingData = rankingResponse.data.data;
      }
    }
    
    if (rankingData && Array.isArray(rankingData)) {
      topStudents.value = rankingData;
      console.log('加载到学生排名数据:', topStudents.value.length, '条');
    } else {
      throw new Error('学生排名数据格式不正确');
    }
    
    // 获取项目分布数据
    let hasItemDistribution = false;
    if (statistics.value && statistics.value.itemDistribution) {
      distributionData.value = statistics.value.itemDistribution;
      hasItemDistribution = true;
    } 
    
    if (!hasItemDistribution) {
      // 模拟项目分布数据作为后备
      distributionData.value = [
        { item_id: 1, item_name: '按时完成作业', count: 450, score_sum: 900 },
        { item_id: 2, item_name: '课堂发言积极', count: 320, score_sum: 320 },
        { item_id: 3, item_name: '迟到', count: 120, score_sum: -240 },
        { item_id: 4, item_name: '违反纪律', count: 80, score_sum: -240 },
        { item_id: 5, item_name: '清扫责任区', count: 180, score_sum: 360 },
        { item_id: 6, item_name: '参与志愿活动', count: 100, score_sum: 300 }
      ];
      console.log('使用模拟分布数据');
    }
    renderPieChart();
    renderGaugeChart();
  } catch (error) {
    console.error('Failed to load dashboard data:', error);
    message.error('加载仪表盘数据失败，使用模拟数据');
    
    // 加载失败时使用模拟数据作为后备
    const mockSummaryResponse = getMockStatisticsSummary();
    statistics.value = mockSummaryResponse.data;
    console.log('使用模拟统计摘要');
    
    const mockRankingResponse = getMockStudentRankings();
    topStudents.value = mockRankingResponse.data;
    console.log('使用模拟学生排名数据:', topStudents.value.length, '条');
    
    distributionData.value = [
      { item_id: 1, item_name: '按时完成作业', count: 450, score_sum: 900 },
      { item_id: 2, item_name: '课堂发言积极', count: 320, score_sum: 320 },
      { item_id: 3, item_name: '迟到', count: 120, score_sum: -240 },
      { item_id: 4, item_name: '违反纪律', count: 80, score_sum: -240 },
      { item_id: 5, item_name: '清扫责任区', count: 180, score_sum: 360 },
      { item_id: 6, item_name: '参与志愿活动', count: 100, score_sum: 300 }
    ];
    console.log('使用模拟分布数据');
    
    renderPieChart();
    renderGaugeChart();
  } finally {
    loading.value = false;
  }
};

// 渲染项目分布饼图
const renderPieChart = () => {
  if (!pieChartRef.value || !hasDistributionData.value) return;
  
  // 确保图表实例已创建
  if (!pieChart.value) {
    pieChart.value = echarts.init(pieChartRef.value);
  }
  
  // 准备数据，添加安全检查
  if (!distributionData.value || !Array.isArray(distributionData.value)) {
    console.warn('缺少分布数据，无法渲染饼图');
    return;
  }
  
  const data = distributionData.value.map(item => ({
    name: item.item_name || '未命名项目',
    value: item.count || 0
  }));
  
  // 图表配置
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
      data: data.map(item => item.name)
    },
    series: [
      {
        name: '项目分布',
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
            fontSize: '14',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ]
  };
  
  // 设置图表配置
  pieChart.value.setOption(option);
};

// 渲染正负分布仪表盘
const renderGaugeChart = () => {
  if (!gaugeChartRef.value) return;
  
  // 确保图表实例已创建
  if (!gaugeChart.value) {
    gaugeChart.value = echarts.init(gaugeChartRef.value);
  }
  
  // 准备数据，添加空值检查
  const positivePercentage = statistics.value?.positive_percentage ?? 0;
  const negativePercentage = statistics.value?.negative_percentage ?? 0;
  const neutralPercentage = statistics.value?.neutral_percentage ?? 0;
  
  // 图表配置
  const option = {
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        center: ['50%', '75%'],
        radius: '90%',
        min: 0,
        max: 1,
        splitNumber: 8,
        axisLine: {
          lineStyle: {
            width: 6,
            color: [
              [0.25, '#d03050'],
              [0.5, '#d9d9d9'],
              [1, '#18a058']
            ]
          }
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '12%',
          width: 20,
          offsetCenter: [0, '-60%'],
          itemStyle: {
            color: '#4f4f4f'
          }
        },
        axisTick: {
          length: 12,
          lineStyle: {
            color: 'auto',
            width: 2
          }
        },
        splitLine: {
          length: 20,
          lineStyle: {
            color: 'auto',
            width: 5
          }
        },
        axisLabel: {
          show: false
        },
        title: {
          offsetCenter: [0, '10%'],
          fontSize: 14
        },
        detail: {
          fontSize: 12,
          offsetCenter: [0, '-35%'],
          valueAnimation: true,
          formatter: function (value: number) {
            return '正面: ' + Math.round(positivePercentage * 100) + '%\n' +
                   '中性: ' + Math.round(neutralPercentage * 100) + '%\n' +
                   '负面: ' + Math.round(negativePercentage * 100) + '%';
          },
          color: 'inherit'
        },
        data: [
          {
            value: positivePercentage > negativePercentage ? 0.75 : 0.25,
            name: '正负分布'
          }
        ]
      }
    ]
  };
  
  // 设置图表配置
  gaugeChart.value.setOption(option);
};

// 窗口大小改变时调整图表大小
const handleResize = () => {
  pieChart.value?.resize();
  gaugeChart.value?.resize();
};

// 组件挂载
onMounted(() => {
  // 加载初始数据
  loadClasses();
  loadItems();
  loadDashboardData();
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize);
});

// 组件卸载
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  pieChart.value?.dispose();
  gaugeChart.value?.dispose();
});
</script>

<style scoped>
.data-visualization-dashboard {
  width: 100%;
}

.filter-card {
  margin-bottom: 16px;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.stat-card {
  text-align: center;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.small-chart {
  height: 300px;
}

.positive-score {
  color: #18a058;
  font-weight: bold;
}

.negative-score {
  color: #d03050;
  font-weight: bold;
}
</style> 