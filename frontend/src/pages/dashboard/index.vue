<template>
  <div>
    <!-- <n-alert v-if="apiError" type="error" closable class="mb-4">
      无法连接到后端服务器，请确保API服务正常运行。
      <br />
      错误信息: {{ apiError }}
      <div class="mt-2">
        <n-button size="small" type="primary" @click="checkApiStatus">
          重试连接
        </n-button>
      </div>
    </n-alert> -->
    
    <page-header title="仪表盘" subtitle="查看班级整体数据和学生表现趋势">
      <template #actions>
        <n-button-group>
          <n-button @click="refreshData">
            <template #icon>
              <n-icon><reload-outline /></n-icon>
            </template>
            刷新数据
          </n-button>
          <n-button type="primary" @click="exportDashboard">导出报表</n-button>
        </n-button-group>
      </template>
    </page-header>
    
    <responsive-container>
      <data-visualization-dashboard />
    </responsive-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NAlert, NButton, NButtonGroup, NIcon } from 'naive-ui';
import { ReloadOutline } from '@vicons/ionicons5';
import DataVisualizationDashboard from '@/components/dashboard/DataVisualizationDashboard.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue';
import http from '@/services/http';
import { useMessage } from 'naive-ui';

const apiError = ref<string | null>(null);
const message = useMessage();

// 检查API状态
const checkApiStatus = async () => {
  try {
    apiError.value = null;
    await http.get('/api/info');
    console.log('API服务连接成功');
  } catch (error) {
    console.error('API服务连接失败:', error);
    apiError.value = error instanceof Error ? error.message : String(error);
  }
};

// 刷新数据
const refreshData = () => {
  message.info('正在刷新数据...');
  checkApiStatus();
  // 这里可以添加其他刷新逻辑
};

// 导出报表
const exportDashboard = () => {
  message.info('正在生成报表...');
  // 导出逻辑
};

onMounted(() => {
  checkApiStatus();
});
</script>

<style scoped>
.mb-4 {
  margin-bottom: 16px;
}

.mt-2 {
  margin-top: 8px;
}
</style>
