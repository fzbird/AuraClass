import { ref, onMounted, onUnmounted } from 'vue';
import { useMessage } from 'naive-ui';

// 网络连接状态
export const isOnline = ref(navigator.onLine);
// 是否启用离线模式
export const offlineEnabled = ref(false);
// 当前同步状态
export const syncState = ref<'idle' | 'syncing' | 'error'>('idle');
// 同步进度
export const syncProgress = ref(0);
// 上次同步时间
export const lastSyncTime = ref<Date | null>(null);
// 等待同步的项目数量
export const pendingSyncItems = ref(0);

/**
 * 离线存储键前缀
 */
export const STORAGE_PREFIX = 'auraclass_offline_';

/**
 * 使用网络状态钩子
 * 监听网络状态变化并提供相关方法
 */
export function useNetworkStatus() {
  const message = useMessage();

  // 网络状态变化处理函数
  const handleNetworkChange = () => {
    const wasOnline = isOnline.value;
    isOnline.value = navigator.onLine;

    // 当网络重新连接时
    if (isOnline.value && !wasOnline) {
      message.success('网络已恢复连接');
      
      // 如果启用了离线模式，尝试同步离线数据
      if (offlineEnabled.value) {
        syncOfflineData();
      }
    } 
    // 当网络断开连接时
    else if (!isOnline.value && wasOnline) {
      message.warning('网络连接已断开，已切换至离线模式');
    }
  };

  onMounted(() => {
    window.addEventListener('online', handleNetworkChange);
    window.addEventListener('offline', handleNetworkChange);
    
    // 初始化状态
    isOnline.value = navigator.onLine;
    
    // 从本地存储读取离线模式设置
    const storedOfflineEnabled = localStorage.getItem('auraclass_offline_enabled');
    if (storedOfflineEnabled !== null) {
      offlineEnabled.value = storedOfflineEnabled === 'true';
    }
    
    // 从本地存储读取上次同步时间
    const storedLastSyncTime = localStorage.getItem('auraclass_last_sync_time');
    if (storedLastSyncTime) {
      lastSyncTime.value = new Date(storedLastSyncTime);
    }
    
    // 检查待同步项
    updatePendingSyncCount();
  });

  onUnmounted(() => {
    window.removeEventListener('online', handleNetworkChange);
    window.removeEventListener('offline', handleNetworkChange);
  });

  /**
   * 切换离线模式
   */
  const toggleOfflineMode = (enabled?: boolean) => {
    if (enabled !== undefined) {
      offlineEnabled.value = enabled;
    } else {
      offlineEnabled.value = !offlineEnabled.value;
    }
    
    // 保存设置到本地存储
    localStorage.setItem('auraclass_offline_enabled', offlineEnabled.value.toString());
    
    // 显示提示
    if (offlineEnabled.value) {
      message.info('已启用离线模式');
    } else {
      message.info('已禁用离线模式');
    }
  };

  return {
    isOnline,
    offlineEnabled,
    toggleOfflineMode,
    syncState,
    syncProgress,
    lastSyncTime,
    pendingSyncItems
  };
}

/**
 * 同步离线数据
 * 将所有离线缓存的数据同步到服务器
 */
export async function syncOfflineData(): Promise<boolean> {
  // 如果不在线或已在同步中，则返回
  if (!isOnline.value || syncState.value === 'syncing') {
    return false;
  }
  
  try {
    syncState.value = 'syncing';
    syncProgress.value = 0;
    
    // 获取所有离线数据键
    const offlineKeys = getOfflineKeys();
    
    if (offlineKeys.length === 0) {
      // 没有离线数据需要同步
      syncState.value = 'idle';
      syncProgress.value = 100;
      lastSyncTime.value = new Date();
      localStorage.setItem('auraclass_last_sync_time', lastSyncTime.value.toISOString());
      return true;
    }
    
    // 总项目数
    const totalItems = offlineKeys.length;
    let processedItems = 0;
    let hasErrors = false;
    
    // 遍历所有离线数据
    for (const key of offlineKeys) {
      try {
        const offlineData = getOfflineItem(key);
        
        if (offlineData) {
          // 提取API路径和方法
          const { apiPath, method, payload, timestamp } = offlineData;
          
          // 调用对应的API同步数据
          const response = await fetch(apiPath, {
            method,
            headers: {
              'Content-Type': 'application/json',
              'X-Offline-Timestamp': timestamp.toString()
            },
            body: method !== 'GET' ? JSON.stringify(payload) : undefined
          });
          
          if (response.ok) {
            // 同步成功，移除离线数据
            removeOfflineItem(key);
          } else {
            // 同步失败
            hasErrors = true;
            console.error(`Failed to sync item ${key}:`, await response.text());
          }
        }
      } catch (error) {
        console.error(`Error syncing item ${key}:`, error);
        hasErrors = true;
      }
      
      // 更新进度
      processedItems++;
      syncProgress.value = Math.round((processedItems / totalItems) * 100);
    }
    
    // 更新同步状态
    syncState.value = hasErrors ? 'error' : 'idle';
    lastSyncTime.value = new Date();
    localStorage.setItem('auraclass_last_sync_time', lastSyncTime.value.toISOString());
    
    // 重新计算待同步项
    updatePendingSyncCount();
    
    return !hasErrors;
  } catch (error) {
    console.error('Sync error:', error);
    syncState.value = 'error';
    return false;
  }
}

/**
 * 保存离线数据
 * @param apiPath API路径
 * @param method HTTP方法
 * @param payload 请求数据
 * @param identifier 可选标识符，用于区分相同路径的不同操作
 */
export function saveOfflineData(
  apiPath: string, 
  method: string, 
  payload: any, 
  identifier?: string
): string {
  const timestamp = Date.now();
  const id = identifier || Math.random().toString(36).substring(2, 9);
  const key = `${STORAGE_PREFIX}${apiPath.replace(/\//g, '_')}_${method}_${id}`;
  
  const offlineData = {
    apiPath,
    method,
    payload,
    timestamp,
    id
  };
  
  // 保存到本地存储
  localStorage.setItem(key, JSON.stringify(offlineData));
  
  // 更新待同步项计数
  updatePendingSyncCount();
  
  return key;
}

/**
 * 获取离线存储的项目
 */
export function getOfflineItem(key: string): any {
  const item = localStorage.getItem(key);
  if (item) {
    try {
      return JSON.parse(item);
    } catch (error) {
      console.error(`Error parsing offline item ${key}:`, error);
      return null;
    }
  }
  return null;
}

/**
 * 移除离线存储的项目
 */
export function removeOfflineItem(key: string): void {
  localStorage.removeItem(key);
  updatePendingSyncCount();
}

/**
 * 获取所有离线数据键
 */
export function getOfflineKeys(): string[] {
  const keys: string[] = [];
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith(STORAGE_PREFIX)) {
      keys.push(key);
    }
  }
  return keys;
}

/**
 * 清除所有离线数据
 */
export function clearOfflineData(): void {
  const keys = getOfflineKeys();
  for (const key of keys) {
    localStorage.removeItem(key);
  }
  updatePendingSyncCount();
}

/**
 * 更新待同步项数量
 */
export function updatePendingSyncCount(): void {
  pendingSyncItems.value = getOfflineKeys().length;
}

/**
 * 包装API请求函数，支持离线模式
 * @param apiFunction 原始API函数
 * @param fallbackData 离线模式下的回退数据
 */
export function withOfflineSupport<T, P extends any[]>(
  apiFunction: (...args: P) => Promise<T>,
  offlineOptions: {
    // API路径构建函数，根据传入的参数构建API路径
    getApiPath: (...args: P) => string,
    // HTTP方法
    method: string,
    // 获取请求体的函数，根据传入的参数构建请求体
    getPayload?: (...args: P) => any,
    // 离线模式下的回退数据
    fallbackData?: T | (() => T),
    // 离线标识符构建函数，用于区分相同路径的不同操作
    getIdentifier?: (...args: P) => string
  }
): (...args: P) => Promise<T> {
  
  return async (...args: P): Promise<T> => {
    // 如果在线或未启用离线模式，直接调用原API函数
    if (isOnline.value || !offlineEnabled.value) {
      try {
        return await apiFunction(...args);
      } catch (error) {
        // 如果发生网络错误且启用了离线模式，存储请求并返回回退数据
        if (error instanceof Error && error.message.includes('network') && offlineEnabled.value) {
          const apiPath = offlineOptions.getApiPath(...args);
          const payload = offlineOptions.getPayload ? offlineOptions.getPayload(...args) : args[0];
          const identifier = offlineOptions.getIdentifier ? offlineOptions.getIdentifier(...args) : undefined;
          
          // 保存到离线存储
          saveOfflineData(apiPath, offlineOptions.method, payload, identifier);
          
          // 返回回退数据
          return typeof offlineOptions.fallbackData === 'function'
            ? (offlineOptions.fallbackData as () => T)()
            : offlineOptions.fallbackData as T;
        }
        throw error;
      }
    } else {
      // 离线模式下，保存请求并返回回退数据
      const apiPath = offlineOptions.getApiPath(...args);
      const payload = offlineOptions.getPayload ? offlineOptions.getPayload(...args) : args[0];
      const identifier = offlineOptions.getIdentifier ? offlineOptions.getIdentifier(...args) : undefined;
      
      // 保存到离线存储
      saveOfflineData(apiPath, offlineOptions.method, payload, identifier);
      
      // 返回回退数据
      return typeof offlineOptions.fallbackData === 'function'
        ? (offlineOptions.fallbackData as () => T)()
        : offlineOptions.fallbackData as T;
    }
  };
} 