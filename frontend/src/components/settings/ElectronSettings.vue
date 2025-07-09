<template>
  <div class="electron-settings">
    <n-card title="桌面应用设置" size="small" class="mb-4">
      <n-space vertical>
        <n-switch v-model:value="minToTray" size="medium">
          <template #checked>最小化到托盘</template>
          <template #unchecked>最小化到托盘</template>
        </n-switch>
        
        <n-switch v-model:value="startAtLogin" size="medium">
          <template #checked>开机自启动</template>
          <template #unchecked>开机自启动</template>
        </n-switch>
        
        <n-switch v-model:value="checkForUpdates" size="medium">
          <template #checked>自动检查更新</template>
          <template #unchecked>自动检查更新</template>
        </n-switch>
      </n-space>
    </n-card>
    
    <n-card title="应用更新" size="small" class="mb-4">
      <n-space vertical>
        <n-space justify="space-between" align="center">
          <span>当前版本：{{ appVersion }}</span>
          <n-button 
            @click="checkUpdates" 
            :loading="checkingUpdates"
            :disabled="!isElectron || checkingUpdates"
            size="small"
          >
            检查更新
          </n-button>
        </n-space>
        
        <div v-if="updateInfo && !updateDownloaded" class="update-info">
          <n-alert type="info" class="mb-2">
            <template #header>
              <div class="flex justify-between items-center">
                <span>发现新版本: {{ updateInfo.version }}</span>
                <span class="text-xs opacity-70">{{ formatDate(updateInfo.releaseDate) }}</span>
              </div>
            </template>
            <div v-if="updateInfo.releaseNotes" class="update-notes">
              <div v-html="formatReleaseNotes(updateInfo.releaseNotes)"></div>
            </div>
          </n-alert>
          
          <div class="flex justify-end space-x-2 mt-2">
            <n-button 
              @click="downloadUpdate" 
              type="primary" 
              size="small"
              :loading="downloading"
              :disabled="downloading"
            >
              {{ downloading ? `下载中 ${updateProgress.percent.toFixed(0)}%` : '下载更新' }}
            </n-button>
          </div>
          
          <n-progress 
            v-if="downloading" 
            type="line" 
            :percentage="updateProgress.percent" 
            :processing="updateProgress.percent < 100"
            :indicator-placement="'inside'"
            :height="12"
          />
        </div>
        
        <n-alert 
          v-if="updateDownloaded" 
          type="success"
        >
          <template #header>
            <span>更新已下载完成</span>
          </template>
          <p>新版本 {{ updateInfo?.version }} 已下载完成，重启应用后将自动安装。</p>
        </n-alert>
        
        <div v-if="updateDownloaded" class="flex justify-end space-x-2 mt-2">
          <n-button 
            @click="restartApp" 
            type="primary" 
            size="small"
          >
            立即重启并安装
          </n-button>
        </div>
        
        <n-alert 
          v-if="updateError" 
          type="error"
        >
          <template #header>
            <span>更新失败</span>
          </template>
          <p>{{ updateError }}</p>
        </n-alert>
      </n-space>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { NCard, NSpace, NSwitch, NButton, NAlert, NProgress } from 'naive-ui';
import { isElectron, callElectron, getAppVersion } from '@/utils/electron';
import { IpcChannels } from '@/utils/electron-ipc';
import type { UpdateInfo, UpdateProgress, AppConfig } from '@/utils/electron-ipc';
import { format } from 'date-fns';
import { useMessage } from 'naive-ui';

const message = useMessage();

// 应用设置状态
const minToTray = ref(true);
const startAtLogin = ref(false);
const checkForUpdates = ref(true);
const appVersion = ref('loading...');

// 更新状态
const checkingUpdates = ref(false);
const updateInfo = ref<UpdateInfo | null>(null);
const updateError = ref<string | null>(null);
const downloading = ref(false);
const updateDownloaded = ref(false);
const updateProgress = ref<UpdateProgress>({
  percent: 0,
  bytesPerSecond: 0,
  total: 0,
  transferred: 0,
  delta: 0
});

// 计算是否为Electron环境
const electronAvailable = computed(() => isElectron());

// 加载应用设置
const loadAppConfig = async () => {
  if (!electronAvailable.value) return;
  
  try {
    const result = await callElectron<{ success: boolean; config?: AppConfig; error?: string }>('getAppConfig');
    
    if (result.success && result.config) {
      minToTray.value = result.config.minToTray;
      startAtLogin.value = result.config.startAtLogin;
      checkForUpdates.value = result.config.checkForUpdates;
    }
  } catch (error) {
    console.error('Failed to load app config:', error);
  }
};

// 保存应用设置
const saveAppConfig = async () => {
  if (!electronAvailable.value) return;
  
  const config: AppConfig = {
    minToTray: minToTray.value,
    startAtLogin: startAtLogin.value,
    checkForUpdates: checkForUpdates.value,
    theme: 'system',
    language: 'zh-CN'
  };
  
  try {
    const result = await callElectron<{ success: boolean; error?: string }>('saveAppConfig', config);
    
    if (result.success) {
      message.success('设置已保存');
    } else if (result.error) {
      message.error(`保存设置失败: ${result.error}`);
    }
  } catch (error) {
    console.error('Failed to save app config:', error);
    message.error('保存设置失败');
  }
};

// 检查更新
const checkUpdates = async () => {
  if (!electronAvailable.value) return;
  
  checkingUpdates.value = true;
  updateError.value = null;
  
  try {
    // 发送检查更新请求
    await callElectron('checkForUpdates');
    
    // 等待5秒，如果没有收到更新消息，则显示没有更新
    setTimeout(() => {
      if (checkingUpdates.value) {
        checkingUpdates.value = false;
        message.info('已是最新版本');
      }
    }, 5000);
  } catch (error) {
    checkingUpdates.value = false;
    updateError.value = (error as Error).message;
    message.error('检查更新失败');
  }
};

// 下载更新
const downloadUpdate = async () => {
  if (!electronAvailable.value || !updateInfo.value) return;
  
  downloading.value = true;
  updateError.value = null;
  
  try {
    await callElectron('downloadUpdate');
  } catch (error) {
    downloading.value = false;
    updateError.value = (error as Error).message;
  }
};

// 重启应用并安装更新
const restartApp = async () => {
  if (!electronAvailable.value) return;
  
  try {
    await callElectron('restartApp');
  } catch (error) {
    message.error('重启应用失败');
  }
};

// 格式化发布日期
const formatDate = (dateString: string) => {
  try {
    return format(new Date(dateString), 'yyyy-MM-dd');
  } catch (e) {
    return dateString;
  }
};

// 格式化发布说明
const formatReleaseNotes = (notes: string) => {
  // 简单转换Markdown格式的发布说明
  return notes
    .replace(/\n/g, '<br>')
    .replace(/#{1,6}\s+(.+)/g, '<strong>$1</strong><br>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/- (.+)/g, '• $1<br>')
    .replace(/```[^`]*```/g, (match) => `<pre>${match.slice(3, -3)}</pre>`);
};

// 监听设置变化并保存
watch([minToTray, startAtLogin, checkForUpdates], () => {
  saveAppConfig();
});

// 设置IPC事件监听
const setupIpcListeners = () => {
  if (!electronAvailable.value || !window.electronAPI) return;
  
  // 监听更新可用事件
  window.addEventListener('update-available', ((event: Event) => {
    const customEvent = event as CustomEvent<UpdateInfo>;
    checkingUpdates.value = false;
    updateInfo.value = customEvent.detail;
  }) as EventListener);
  
  // 监听更新下载进度
  window.addEventListener('update-progress', ((event: Event) => {
    const customEvent = event as CustomEvent<UpdateProgress>;
    updateProgress.value = customEvent.detail;
  }) as EventListener);
  
  // 监听更新下载完成
  window.addEventListener('update-downloaded', () => {
    downloading.value = false;
    updateDownloaded.value = true;
  });
  
  // 监听更新错误
  window.addEventListener('update-error', ((event: Event) => {
    const customEvent = event as CustomEvent<string>;
    checkingUpdates.value = false;
    downloading.value = false;
    updateError.value = customEvent.detail;
  }) as EventListener);
};

// 组件挂载
onMounted(async () => {
  // 获取应用版本
  appVersion.value = await getAppVersion();
  
  // 加载应用设置
  await loadAppConfig();
  
  // 设置IPC事件监听
  setupIpcListeners();
});
</script>

<style scoped>
.electron-settings {
  max-width: 800px;
  margin: 0 auto;
}

.update-notes {
  max-height: 150px;
  overflow-y: auto;
  margin: 8px 0;
  padding: 8px;
  background-color: rgba(0, 0, 0, 0.03);
  border-radius: 4px;
  font-size: 0.9em;
}

.mb-2 {
  margin-bottom: 8px;
}

.mb-4 {
  margin-bottom: 16px;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.justify-end {
  justify-content: flex-end;
}

.items-center {
  align-items: center;
}

.space-x-2 > * + * {
  margin-left: 8px;
}

.mt-2 {
  margin-top: 8px;
}

.text-xs {
  font-size: 0.75rem;
}

.opacity-70 {
  opacity: 0.7;
}
</style> 