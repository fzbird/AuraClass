<template>
  <div class="ai-data-analysis">
    <div class="analysis-header">
      <h3>{{ title }}</h3>
      <n-button quaternary circle size="small" @click="refreshAnalysis">
        <template #icon>
          <n-icon><ReloadOutlined /></n-icon>
        </template>
      </n-button>
    </div>

    <div class="analysis-content">
      <div v-if="loading" class="analysis-loading">
        <n-spin size="medium" />
        <p>正在分析数据...</p>
      </div>
      
      <div v-else-if="error" class="analysis-error">
        <n-alert type="error" :title="error.title" closable @close="error = null">
          {{ error.message }}
        </n-alert>
      </div>
      
      <div v-else-if="insights.length" class="analysis-insights">
        <div v-for="(insight, index) in insights" :key="index" class="insight-item">
          <n-card size="small" :bordered="false">
            <template #header>
              <div class="insight-header">
                <n-icon :color="getInsightColor(insight.type)" size="18">
                  <component :is="getInsightIcon(insight.type)" />
                </n-icon>
                <span class="insight-title">{{ insight.title }}</span>
              </div>
            </template>
            
            <div class="insight-content">
              <p>{{ insight.description }}</p>
              <div v-if="insight.chart" class="insight-chart">
                <!-- 图表内容 -->
                <component :is="insight.chart.type" :data="insight.chart.data" :config="insight.chart.config" />
              </div>
              <div v-if="insight.action" class="insight-action">
                <n-button size="small" type="primary" @click="handleAction(insight.action)">
                  {{ insight.action.text }}
                </n-button>
              </div>
            </div>
          </n-card>
        </div>
      </div>
      
      <div v-else class="analysis-empty">
        <n-empty description="暂无数据分析结果">
          <template #extra>
            <n-button size="small" @click="refreshAnalysis">
              开始分析
            </n-button>
          </template>
        </n-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { 
  NButton, 
  NIcon, 
  NSpin, 
  NAlert, 
  NCard, 
  NEmpty, 
  useMessage 
} from 'naive-ui';
import { useRoute, useRouter } from 'vue-router';
import ReloadOutlined from '@vicons/antd/es/ReloadOutlined';
import RiseOutlined from '@vicons/antd/es/RiseOutlined';
import FallOutlined from '@vicons/antd/es/FallOutlined';
import AlertOutlined from '@vicons/antd/es/AlertOutlined';
import BulbOutlined from '@vicons/antd/es/BulbOutlined';
import LineChartOutlined from '@vicons/antd/es/LineChartOutlined';
import { getDataAnalysis } from '@/services/api/assistant';
import { SimpleAreaChart, SimpleBarChart } from '@/components/business/charts';

interface InsightAction {
  text: string;
  type: 'navigate' | 'download' | 'custom';
  payload: any;
}

interface InsightChart {
  type: 'SimpleAreaChart' | 'SimpleBarChart' | 'SimplePieChart';
  data: any[];
  config: any;
}

interface Insight {
  id: string;
  type: 'trend' | 'alert' | 'suggestion' | 'comparison';
  title: string;
  description: string;
  chart?: InsightChart;
  action?: InsightAction;
}

// 组件属性定义
const props = defineProps({
  title: {
    type: String,
    default: 'AI 智能分析'
  },
  context: {
    type: String,
    default: 'dashboard' // dashboard, students, records, statistics
  },
  contextId: {
    type: [String, Number],
    default: null
  },
  autoRefresh: {
    type: Boolean,
    default: true
  }
});

// 组件事件
const emit = defineEmits(['insight-action', 'error', 'loading', 'loaded']);

// 组件状态
const message = useMessage();
const route = useRoute();
const router = useRouter();
const loading = ref(false);
const error = ref<{ title: string; message: string } | null>(null);
const insights = ref<Insight[]>([]);

// 获取分析数据
const fetchInsights = async () => {
  loading.value = true;
  error.value = null;
  emit('loading');
  
  try {
    const params = {
      context: props.context,
      contextId: props.contextId,
      timestamp: new Date().getTime()
    };
    
    const response = await getDataAnalysis(params);
    insights.value = response.data;
    emit('loaded', response.data);
  } catch (err: any) {
    console.error('Failed to fetch data insights:', err);
    error.value = {
      title: '数据分析失败',
      message: err?.message || '获取数据分析结果时出错，请稍后重试'
    };
    emit('error', error.value);
  } finally {
    loading.value = false;
  }
};

// 刷新分析数据
const refreshAnalysis = () => {
  fetchInsights();
};

// 根据洞察类型获取图标组件
const getInsightIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    'trend': RiseOutlined,
    'alert': AlertOutlined,
    'suggestion': BulbOutlined,
    'comparison': LineChartOutlined
  };
  
  return iconMap[type] || BulbOutlined;
};

// 根据洞察类型获取图标颜色
const getInsightColor = (type: string) => {
  const colorMap: Record<string, string> = {
    'trend': '#18a058',
    'alert': '#d03050',
    'suggestion': '#2080f0',
    'comparison': '#f0a020'
  };
  
  return colorMap[type] || '#2080f0';
};

// 处理洞察操作
const handleAction = (action: InsightAction) => {
  emit('insight-action', action);
  
  if (action.type === 'navigate') {
    router.push(action.payload);
  } else if (action.type === 'download') {
    // 处理下载操作
    window.open(action.payload, '_blank');
  }
};

// 组件挂载时加载数据
onMounted(() => {
  if (props.autoRefresh) {
    fetchInsights();
  }
});
</script>

<style scoped>
.ai-data-analysis {
  margin-bottom: 16px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.analysis-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.analysis-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 0;
}

.analysis-loading p {
  margin-top: 12px;
  color: #8c8c8c;
}

.analysis-empty {
  padding: 24px 0;
}

.analysis-insights {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.insight-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.insight-title {
  font-weight: 500;
}

.insight-content {
  font-size: 14px;
}

.insight-chart {
  margin: 12px 0;
  height: 120px;
}

.insight-action {
  margin-top: 8px;
  text-align: right;
}
</style> 