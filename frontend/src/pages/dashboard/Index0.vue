<template>
  <div class="dashboard-page">
    <div class="welcome-section">
      <div class="welcome-message">
        <h1>{{ getGreeting() }}，{{ userStore.user?.full_name || '管理员' }}</h1>
        <p>{{ currentDate }} {{ currentTime }}</p>
      </div>
      <div class="welcome-actions">
        <n-space>
          <n-button @click="refreshData" :loading="loading">
            <template #icon>
              <n-icon><refresh-icon /></n-icon>
            </template>
            刷新数据
          </n-button>
          <n-button type="primary" @click="router.push('/records/create')">
            <template #icon>
              <n-icon><add-icon /></n-icon>
            </template>
            新建记录
          </n-button>
        </n-space>
      </div>
    </div>
    
    <!-- 数据概览卡片 -->
    <div class="stat-cards">
      <dashboard-stat-card
        title="学生总数"
        :value="dashboardData.totalStudents"
        icon="people"
        color="#3366FF"
      />
      
      <dashboard-stat-card
        title="本月记录"
        :value="dashboardData.monthlyRecords"
        icon="document-text"
        color="#52C41A"
      />
      
      <dashboard-stat-card
        title="班级数量"
        :value="dashboardData.classCount"
        icon="school"
        color="#FA8C16"
      />
      
      <dashboard-stat-card
        title="今日记录"
        :value="dashboardData.todayRecords"
        icon="today"
        color="#EB2F96"
      />
    </div>
    
    <!-- 统计图表区域 -->
    <n-card title="数据统计" class="chart-section">
      <n-tabs type="line" animated>
        <n-tab-pane name="overview" tab="总体概览">
          <statistics-overview :stats="dashboardData.statistics" />
        </n-tab-pane>
        
        <n-tab-pane name="ranking" tab="班级排名">
          <div v-if="dashboardData.rankingData && dashboardData.rankingData.length > 0">
            <ranking-list :items="dashboardData.rankingData" />
          </div>
          <n-empty v-else description="暂无排名数据" />
        </n-tab-pane>
      </n-tabs>
    </n-card>
    
    <!-- 最近记录 & 通知区域 -->
    <n-grid :cols="24" :x-gap="16" class="bottom-section">
      <n-grid-item :span="24" :lg="16">
        <n-card title="最近量化记录" class="recent-records">
          <template #header-extra>
            <n-button text @click="router.push('/records')">
              查看全部
              <template #icon>
                <n-icon><arrow-forward-icon /></n-icon>
              </template>
            </n-button>
          </template>
          
          <n-data-table
            :columns="recordColumns"
            :data="dashboardData.recentRecords"
            :pagination="{ pageSize: 5 }"
            :bordered="false"
          />
        </n-card>
      </n-grid-item>
      
      <n-grid-item :span="24" :lg="8">
        <n-card title="通知中心" class="notifications">
          <template #header-extra>
            <n-button text @click="router.push('/notifications')">
              全部通知
              <template #icon>
                <n-icon><arrow-forward-icon /></n-icon>
              </template>
            </n-button>
          </template>
          
          <notification-list :notifications="dashboardData.notifications" />
        </n-card>
      </n-grid-item>
    </n-grid>
    
    <!-- 快速操作区域 -->
    <n-card title="快速操作" class="quick-actions">
      <n-grid :cols="24" :x-gap="16" :y-gap="16">
        <n-grid-item :span="8" :md="6" :lg="4" v-for="(action, index) in quickActions" :key="index">
          <div class="action-item" @click="handleQuickAction(action)">
            <n-icon :size="32" :color="action.color">
              <component :is="action.icon" />
            </n-icon>
            <span>{{ action.title }}</span>
          </div>
        </n-grid-item>
      </n-grid>
    </n-card>
    
    <!-- AI助手提示 -->
    <n-card v-if="dashboardData.aiSuggestions?.length" class="ai-suggestions">
      <template #header>
        <div class="flex items-center">
          <n-icon size="20" color="#722ED1" class="mr-2">
            <bulb-icon />
          </n-icon>
          <span>AI助手洞察</span>
        </div>
      </template>
      
      <n-carousel
        show-arrow
        dot-placement="bottom"
        effect="fade"
        autoplay
        :interval="5000"
      >
        <n-carousel-item v-for="(suggestion, index) in dashboardData.aiSuggestions" :key="index">
          <div class="suggestion-item">
            <p>{{ suggestion.content }}</p>
            <n-button text type="primary" size="small" @click="viewAiSuggestion(suggestion)">
              了解更多
            </n-button>
          </div>
        </n-carousel-item>
      </n-carousel>
    </n-card>
    
    <!-- 系统状态 -->
    <n-card v-if="showSystemInfo" class="system-info">
      <n-descriptions :column="3" size="small" bordered>
        <n-descriptions-item label="系统版本">1.0.0</n-descriptions-item>
        <n-descriptions-item label="上次更新">{{ lastUpdated }}</n-descriptions-item>
        <n-descriptions-item label="WebSocket">
          <n-tag :type="wsStore.isConnected ? 'success' : 'error'">
            {{ wsStore.isConnected ? '已连接' : '未连接' }}
          </n-tag>
        </n-descriptions-item>
      </n-descriptions>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, h } from 'vue';
import { useRouter } from 'vue-router';
import { 
  NCard, NButton, NSpace, NIcon, NGrid, NGridItem, 
  NDataTable, NTabs, NTabPane, NEmpty, NTag,
  NCarousel, NCarouselItem, NDescriptions, NDescriptionsItem,
  useMessage
} from 'naive-ui';
import { 
  RefreshOutline as RefreshIcon,
  AddOutline as AddIcon,
  PeopleOutline as PeopleIcon,
  SchoolOutline as SchoolIcon,
  DocumentTextOutline as DocumentIcon,
  CalendarOutline as CalendarIcon,
  SettingsOutline as SettingsIcon,
  BarChartOutline as ChartIcon,
  PersonAddOutline as PersonAddIcon,
  PieChartOutline as PieChartIcon,
  PrintOutline as PrintIcon,
  CloudUploadOutline as UploadIcon,
  CloudDownloadOutline as DownloadIcon,
  BulbOutline as BulbIcon,
  ArrowForwardOutline as ArrowForwardIcon
} from '@vicons/ionicons5';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

import { useUserStore } from '@/stores/user';
import { useWebSocketStore } from '@/stores/websocket';
import DashboardStatCard from '@/components/business/DashboardStatCard.vue';
import StatisticsOverview from '@/components/business/StatisticsOverview.vue';
import RankingList from '@/components/business/RankingList.vue';
import NotificationList from '@/components/business/NotificationList.vue';

const router = useRouter();
const message = useMessage();
const userStore = useUserStore();
const wsStore = useWebSocketStore();

const loading = ref(false);
const showSystemInfo = ref(true);
const lastUpdated = ref(format(new Date(), 'yyyy-MM-dd HH:mm:ss'));

// 当前日期时间
const currentDate = computed(() => {
  return format(new Date(), 'yyyy年MM月dd日', { locale: zhCN });
});
const currentTime = computed(() => {
  return format(new Date(), 'EEEE HH:mm', { locale: zhCN });
});

// 仪表盘数据
const dashboardData = ref({
  totalStudents: 246,
  monthlyRecords: 453,
  classCount: 8,
  todayRecords: 24,
  recentRecords: [
    { id: 1, student_name: '张三', class_name: '高一(1)班', item_name: '上课认真听讲', score: 2, created_at: '2025-03-15 08:30:00' },
    { id: 2, student_name: '李四', class_name: '高一(1)班', item_name: '课堂发言积极', score: 3, created_at: '2025-03-15 09:15:00' },
    { id: 3, student_name: '王五', class_name: '高一(2)班', item_name: '作业未完成', score: -2, created_at: '2025-03-15 10:00:00' },
    { id: 4, student_name: '赵六', class_name: '高一(2)班', item_name: '主动帮助同学', score: 5, created_at: '2025-03-15 11:45:00' },
    { id: 5, student_name: '钱七', class_name: '高一(3)班', item_name: '课堂违纪', score: -3, created_at: '2025-03-15 14:20:00' }
  ],
  notifications: [
    { 
      id: 1, 
      title: '系统更新通知', 
      content: '系统将于今晚22:00-23:00进行维护更新', 
      type: 'system', 
      isRead: false,
      createdAt: '2025-03-15 12:00:00',
      updatedAt: '2025-03-15 12:00:00'
    },
    { 
      id: 2, 
      title: '成绩导入完成', 
      content: '3月月考成绩已导入完成，请查看', 
      type: 'success', 
      isRead: true,
      createdAt: '2025-03-14 09:30:00',
      updatedAt: '2025-03-14 09:30:00'
    },
    { 
      id: 3, 
      title: '班级量化排名', 
      content: '本周班级量化排名已生成', 
      type: 'info', 
      isRead: false,
      createdAt: '2025-03-13 16:45:00',
      updatedAt: '2025-03-13 16:45:00'
    }
  ],
  rankingData: [
    { id: 1, name: '高一(1)班', value: 568, suffix: '分' },
    { id: 2, name: '高一(2)班', value: 512, suffix: '分' },
    { id: 3, name: '高一(3)班', value: 490, suffix: '分' },
    { id: 4, name: '高一(4)班', value: 475, suffix: '分' },
    { id: 5, name: '高一(5)班', value: 468, suffix: '分' }
  ],
  aiSuggestions: [
    { id: 1, content: '高一(3)班近期量化分数下降明显，建议关注班级纪律问题', type: 'warning' },
    { id: 2, content: '张明同学本月表现优异，可考虑授予"月度之星"称号', type: 'suggestion' },
    { id: 3, content: '高二年级学习量化项目记录偏少，建议加强关注', type: 'insight' }
  ],
  statistics: {
    summary: {
      total_records: 1453,
      total_students: 246,
      avg_records_per_student: 5.9,
      avg_score: 2.4,
      records_change: 128,
      avg_records_change: 0.5,
      avg_score_change: 0.2
    },
    category_distribution: {
      '学习': 623,
      '纪律': 452,
      '卫生': 216,
      '德育': 162
    },
    score_distribution: {
      '-5': 12,
      '-3': 42,
      '-2': 86,
      '-1': 120,
      '1': 345,
      '2': 423,
      '3': 312,
      '5': 113
    },
    daily_records: {
      '2025-03-01': 32,
      '2025-03-02': 28,
      '2025-03-03': 45,
      '2025-03-04': 42,
      '2025-03-05': 38,
      '2025-03-06': 51,
      '2025-03-07': 29,
      '2025-03-08': 24,
      '2025-03-09': 20,
      '2025-03-10': 48,
      '2025-03-11': 52,
      '2025-03-12': 41,
      '2025-03-13': 39,
      '2025-03-14': 44
    }
  }
});

// 记录表格列定义
const recordColumns = [
  {
    title: '学生',
    key: 'student_name'
  },
  {
    title: '班级',
    key: 'class_name'
  },
  {
    title: '量化项目',
    key: 'item_name'
  },
  {
    title: '分数',
    key: 'score',
    render(row: any) {
      const type = row.score > 0 ? 'success' : (row.score < 0 ? 'error' : 'default');
      return h('div', {
        style: { 
          color: row.score > 0 ? '#52C41A' : (row.score < 0 ? '#F5222D' : 'inherit'),
          fontWeight: 'bold'
        }
      }, [row.score > 0 ? '+' : '', row.score]);
    }
  },
  {
    title: '记录时间',
    key: 'created_at'
  },
  {
    title: '操作',
    key: 'actions',
    render(row: any) {
      return h(NButton, {
        size: 'small',
        text: true,
        onClick: () => viewRecord(row.id)
      }, { default: () => '查看' });
    }
  }
];

// 快速操作定义
const quickActions = [
  {
    title: '添加学生',
    icon: PersonAddIcon,
    color: '#3366FF',
    action: '/students/create'
  },
  {
    title: '新建记录',
    icon: DocumentIcon,
    color: '#52C41A',
    action: '/records/create'
  },
  {
    title: '数据统计',
    icon: ChartIcon,
    color: '#FA8C16',
    action: '/statistics'
  },
  {
    title: '排名报表',
    icon: PieChartIcon,
    color: '#EB2F96',
    action: '/reports'
  },
  {
    title: '导出数据',
    icon: DownloadIcon,
    color: '#722ED1',
    action: 'exportData'
  },
  {
    title: '打印报表',
    icon: PrintIcon,
    color: '#13C2C2',
    action: '/reports/print'
  },
  {
    title: '导入数据',
    icon: UploadIcon,
    color: '#1890FF',
    action: 'importData'
  },
  {
    title: '系统设置',
    icon: SettingsIcon,
    color: '#595959',
    action: '/settings'
  }
];

// 根据时间返回问候语
const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 6) return '凌晨好';
  if (hour < 9) return '早上好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 18) return '下午好';
  if (hour < 22) return '晚上好';
  return '夜深了';
};

// 刷新仪表盘数据
const refreshData = async () => {
  loading.value = true;
  try {
    // 这里可以添加实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000));
    message.success('数据已刷新');
    lastUpdated.value = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
  } catch (error) {
    message.error('刷新数据失败');
    console.error('刷新数据失败:', error);
  } finally {
    loading.value = false;
  }
};

// 查看记录详情
const viewRecord = (id: number) => {
  router.push(`/records/${id}`);
};

// 处理快速操作
const handleQuickAction = (action: { action: string }) => {
  if (typeof action.action === 'string') {
    if (action.action.startsWith('/')) {
      router.push(action.action);
    } else if (action.action === 'exportData') {
      message.info('正在准备导出数据...');
      // 这里可以添加导出逻辑
    } else if (action.action === 'importData') {
      message.info('正在准备导入数据...');
      // 这里可以添加导入逻辑
    }
  }
};

// 查看AI建议详情
const viewAiSuggestion = (suggestion: any) => {
  router.push('/ai-assistant');
};

// 组件挂载后检查用户登录状态并加载数据
onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/auth/login');
    return;
  }
  
  refreshData();
});
</script>

<style scoped>
.dashboard-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.welcome-message h1 {
  font-size: 1.5rem;
  font-weight: 500;
  margin: 0;
  color: #333;
}

.welcome-message p {
  color: #666;
  margin: 8px 0 0;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.chart-section {
  margin-bottom: 24px;
}

.bottom-section {
  margin-bottom: 24px;
}

.recent-records, .notifications {
  height: 100%;
}

.quick-actions {
  margin-bottom: 24px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background-color: #f9fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-item span {
  margin-top: 8px;
  color: #333;
}

.ai-suggestions {
  margin-bottom: 24px;
}

.suggestion-item {
  background-color: rgba(114, 46, 209, 0.05);
  border-left: 4px solid #722ED1;
  padding: 16px;
  border-radius: 4px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.system-info {
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .welcome-actions {
    margin-top: 16px;
  }
  
  .stat-cards {
    grid-template-columns: repeat(auto-fill, minmax(100%, 1fr));
  }
}
</style> 