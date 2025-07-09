<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">学生详情</h1>
      
      <n-space>
        <n-button @click="$router.go(-1)">
          返回
        </n-button>
        <n-button 
          type="primary" 
          @click="showEditModal = true"
          v-if="hasPermission('update:students')"
        >
          编辑
        </n-button>
      </n-space>
    </div>
    
    <n-spin :show="loading">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="md:col-span-1">
          <n-card>
            <template #header>
              <div class="flex items-center">
                <n-avatar 
                  size="large" 
                  round 
                  :src="student?.avatar || null"
                  :style="{ 
                    background: student?.avatar ? 'transparent' : getAvatarColor(student?.full_name || student?.name || '未知')
                  }"
                >
                  {{ !student?.avatar ? (student?.full_name || student?.name || '未知').substring(0, 1) : '' }}
                </n-avatar>
                <div class="ml-4">
                  <div class="text-xl font-bold">{{ student?.full_name }}</div>
                  <div class="text-sm text-gray-500">{{ student?.student_id_no }}</div>
                </div>
              </div>
            </template>
            
            <n-descriptions bordered :column="1" label-placement="left">
              <n-descriptions-item label="班级">
                {{ student?.class_name }}
              </n-descriptions-item>
              <n-descriptions-item label="性别">
                {{ student?.gender === 'male' ? '男' : '女' }}
              </n-descriptions-item>
              <n-descriptions-item label="出生日期">
                {{ student?.birth_date ? formatDate(student.birth_date) : '未设置' }}
              </n-descriptions-item>
              <n-descriptions-item label="联系信息">
                {{ student?.contact_info || '未设置' }}
              </n-descriptions-item>
              <n-descriptions-item label="创建时间">
                {{ formatDateTime(student?.created_at) }}
              </n-descriptions-item>
            </n-descriptions>
          </n-card>
        </div>
        
        <div class="md:col-span-2">
          <n-card title="量化记录统计" class="mb-6">
            <n-grid :cols="24" :x-gap="16">
              <n-grid-item :span="8">
                <div class="stat-item">
                  <div class="text-xl font-bold">{{ stats.total_count }}</div>
                  <div class="text-sm text-gray-500">总记录数</div>
                </div>
              </n-grid-item>
              <n-grid-item :span="8">
                <div class="stat-item">
                  <div class="text-xl font-bold">{{ formatScore(stats.total_score) }}</div>
                  <div class="text-sm text-gray-500">总分值</div>
                </div>
              </n-grid-item>
              <n-grid-item :span="8">
                <div class="stat-item">
                  <div class="text-xl font-bold">{{ formatScore(stats.average_score) }}</div>
                  <div class="text-sm text-gray-500">平均分值</div>
                </div>
              </n-grid-item>
            </n-grid>
            
            <n-divider />
            
            <line-chart v-if="!loading && chartData.labels.length > 0" 
                      :chart-data="chartData" 
                      :height="250" />
            <div v-else class="text-center py-10 text-gray-500">
              暂无记录数据
            </div>
          </n-card>
          
          <n-card title="最近量化记录" class="mb-6">
            <template #header-extra>
              <n-button text @click="$router.push('/app/records?student_id=' + student?.id)">
                查看全部
              </n-button>
            </template>
            
            <n-data-table
              :columns="recordColumns"
              :data="records"
              :loading="recordsLoading"
              :pagination="recordPagination"
              size="small"
            />
          </n-card>
        </div>
      </div>
    </n-spin>
    
    <!-- 编辑学生模态框 -->
    <student-form-modal
      v-model:show="showEditModal"
      :class-options="classOptions"
      :student="student"
      @success="loadStudentData"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, h, watch } from 'vue';
import { useRoute } from 'vue-router';
import { 
  NButton, NCard, NSpin, NAvatar, NDescriptions, NDescriptionsItem,
  NGrid, NGridItem, NDivider, NDataTable, NSpace, useMessage
} from 'naive-ui';
import StudentFormModal from '@/components/business/StudentFormModal.vue';
import LineChart from '@/components/business/charts/LineChart.vue';
import { getStudent, getStudentRecords } from '@/services/api/students';
import { getTimeSeriesStats, getStudentStatisticsData } from '@/services/api/statistics';
import { getRecords } from '@/services/api/records';
import { getClasses } from '@/services/api/classes';
import { formatDate, formatDateTime, formatScore } from '@/utils';
import { usePermissionStore } from '@/stores/permission';

const route = useRoute();
const message = useMessage();
const permissionStore = usePermissionStore();

// 添加props接收参数
const props = defineProps({
  id: {
    type: [Number, String],
    default: null
  }
});

// 使用props.id作为首选，路由参数作为备选
const studentId = computed(() => {
  // 首先尝试从props获取
  if (props.id) {
    console.log('使用props中的id:', props.id);
    return Number(props.id);
  }
  // 备选使用路由参数
  console.log('使用路由参数中的id:', route.params.id);
  return Number(route.params.id);
});

const loading = ref(true);
const recordsLoading = ref(true);
const student = ref(null);
const records = ref([]);
const stats = ref({
  total_count: 0,
  total_score: 0,
  average_score: 0
});
const classOptions = ref([]);
const showEditModal = ref(false);

const chartData = reactive({
  labels: [],
  datasets: [
    {
      label: '量化分值',
      data: [],
      borderColor: '#3366FF',
      backgroundColor: 'rgba(51, 102, 255, 0.1)',
      fill: true
    }
  ]
});

const recordPagination = reactive({
  page: 1,
  pageSize: 5,
  showSizePicker: false,
  simple: true
});

const recordColumns = [
  {
    title: '日期',
    key: 'record_date',
    render: (row) => formatDate(row.record_date)
  },
  {
    title: '量化项目',
    key: 'item_name',
    render: (row) => row.item?.name || row.item_name || '-'
  },
  {
    title: '分值',
    key: 'score',
    render: (row) => {
      // 确保score是数字
      const score = parseFloat(row.score);
      if (isNaN(score)) return '-';

      // 直接返回带颜色的文本
      return h(
        'span',
        {
          style: {
            color: score >= 0 ? '#52C41A' : '#F5222D',
            fontWeight: 'bold'
          }
        },
        score > 0 ? `+${score}` : score.toString()
      );
    }
  },
  {
    title: '原因',
    key: 'reason',
    ellipsis: true
  },
  {
    title: '记录人',
    key: 'recorder_name',
    render: (row) => row.recorder?.full_name || row.recorder_name || '-'
  }
];

onMounted(() => {
  loadStudentData();
  fetchClasses();
});

// 添加对studentId的监听
watch(studentId, (newId, oldId) => {
  if (newId !== oldId) {
    console.log(`学生ID变化: ${oldId} -> ${newId}, 重新加载学生数据`);
    loadStudentData();
  }
}, { immediate: false });

const loadStudentData = async () => {
  loading.value = true;
  recordsLoading.value = true;
  
  console.log(`加载学生ID=${studentId.value}的详细信息`);
  
  try {
    // 获取学生信息
    const studentResponse = await getStudent(studentId.value);
    console.log(`获取到学生数据:`, studentResponse.data);
    student.value = studentResponse.data;
    
    // 获取学生量化记录
    await Promise.all([
      fetchStudentRecords(),
      fetchStudentStats()
    ]);
  } catch (error) {
    console.error('Failed to load student data:', error);
    message.error('加载学生数据失败');
  } finally {
    loading.value = false;
    recordsLoading.value = false;
  }
};

const fetchStudentRecords = async () => {
  try {
    // 使用正确的API获取学生的最近量化记录
    const recordsResponse = await getRecords({
      student_id: studentId.value,
      skip: 0,
      limit: 5,
      sort_by: 'record_date',
      sort_order: 'desc'
    });
    
    console.log('学生量化记录响应:', recordsResponse);
    
    if (recordsResponse && recordsResponse.data) {
      records.value = Array.isArray(recordsResponse.data) ? recordsResponse.data : [];
      console.log('处理后的记录数据:', records.value);
    } else {
      records.value = [];
    }
  } catch (error) {
    console.error('获取学生量化记录失败:', error);
    records.value = [];
  } finally {
    recordsLoading.value = false;
  }
};

const fetchStudentStats = async () => {
  try {
    // 使用正确的API获取学生统计数据
    const studentStatsResponse = await getStudentStatisticsData(studentId.value);
    console.log('学生统计数据原始响应:', studentStatsResponse);
    
    // 正确解析后端返回的数据结构
    if (studentStatsResponse && studentStatsResponse.data) {
      const rawData = studentStatsResponse.data;
      
      // 检查返回的是否为数组格式
      if (Array.isArray(rawData) && rawData.length > 0) {
        // 后端返回了数组形式的数据，提取第一条记录
        const studentStat = rawData[0];
        console.log('学生统计数据第一条记录:', studentStat);
        
        // 字段名称映射
        stats.value = {
          total_count: Number(studentStat.record_count || 0),
          total_score: Number(studentStat.total_score || 0),
          average_score: Number(studentStat.avg_score || 0)
        };
      } else if (typeof rawData === 'object') {
        // 后端返回了对象形式的数据
        stats.value = {
          total_count: Number(rawData.total_count || rawData.record_count || 0),
          total_score: Number(rawData.total_score || 0),
          average_score: Number(rawData.average_score || rawData.avg_score || 0)
        };
      }
      
      console.log('处理后的统计数据:', stats.value);
      
      // 如果有月度数据，设置图表数据
      if (rawData.monthly_data && Array.isArray(rawData.monthly_data)) {
        chartData.labels = rawData.monthly_data.map(item => item.month || '');
        chartData.datasets[0].data = rawData.monthly_data.map(item => Number(item.score || 0));
      }
    } else {
      // 如果获取统计数据失败，尝试回退到timeline数据
      await fetchTimelineStats();
    }
  } catch (error) {
    console.error('获取学生统计数据失败:', error);
    // 尝试回退到timeline数据
    await fetchTimelineStats();
  }
};

// 作为备用的timeline数据获取方法
const fetchTimelineStats = async () => {
  try {
    const timelineResponse = await getTimeSeriesStats({
      student_id: studentId.value,
      interval: 'month',
      limit: 6
    });
    
    console.log('学生时间线统计响应:', timelineResponse);
    
    // 确保有有效数据
    const timelineData = Array.isArray(timelineResponse.data) 
      ? timelineResponse.data 
      : [];
    
    // 设置图表数据
    chartData.labels = timelineData.map(item => item.date || '');
    chartData.datasets[0].data = timelineData.map(item => parseFloat(item.score || 0));
    
    // 计算总统计数据并确保所有值都是数字
    stats.value = {
      total_count: timelineData.reduce((sum, item) => sum + parseInt(item.count || 0, 10), 0),
      total_score: timelineData.reduce((sum, item) => sum + parseFloat(item.score || 0), 0),
      average_score: timelineData.length > 0 
        ? timelineData.reduce((sum, item) => sum + parseFloat(item.score || 0), 0) / timelineData.length
        : 0
    };
  } catch (error) {
    console.error('获取学生时间线统计失败:', error);
    // 提供默认统计值
    stats.value = {
      total_count: 0,
      total_score: 0,
      average_score: 0
    };
  }
};

const fetchClasses = async () => {
  try {
    const response = await getClasses();
    console.log('班级数据响应:', response);
    
    // 处理可能的不同响应格式
    let classesData = [];
    if (Array.isArray(response.data)) {
      classesData = response.data;
    } else if (Array.isArray(response)) {
      classesData = response;
    }
    
    classOptions.value = classesData.map(cls => ({
      label: cls.name,
      value: cls.id
    }));
  } catch (error) {
    console.error('Failed to fetch classes:', error);
    message.error('获取班级列表失败');
  }
};

const hasPermission = (permission) => {
  return permissionStore.hasPermission(permission);
};

// 添加getAvatarColor函数，与StudentRankingTable组件保持一致的颜色
const getAvatarColor = (name: string): string => {
  const colors = [
    '#3366FF', '#52C41A', '#FAAD14', '#F5222D', '#722ED1',
    '#13C2C2', '#1890FF', '#EB2F96', '#FA8C16', '#A0D911'
  ];
  
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  return colors[Math.abs(hash) % colors.length];
};
</script>

<style scoped>
.stat-item {
  text-align: center;
  padding: 12px;
}
</style>
