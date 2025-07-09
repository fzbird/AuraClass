// 定义渲染进程可访问的Electron API类型
interface ElectronAPI {
  saveFile: (data: any, defaultPath: string, filters?: any[]) => Promise<{
    success: boolean;
    path?: string;
    error?: string;
    canceled?: boolean;
  }>;
  
  openFile: (filters?: any[], properties?: string[]) => Promise<{
    success: boolean;
    path?: string;
    content?: string;
    error?: string;
    canceled?: boolean;
  }>;
  
  openExternal: (url: string) => Promise<{
    success: boolean;
    error?: string;
  }>;
  
  getAppVersion: () => Promise<string>;
  
  saveAppConfig: (config: any) => Promise<{
    success: boolean;
    error?: string;
  }>;
  
  getAppConfig: () => Promise<{
    success: boolean;
    config?: any;
    error?: string;
  }>;
  
  sendNotification: (
    title: string,
    body: string,
    silent?: boolean
  ) => {
    notification: Notification;
    onClick: (callback: () => void) => void;
  };
  
  // 新增以下IPC方法
  checkForUpdates: () => Promise<void>;
  downloadUpdate: () => Promise<void>;
  restartApp: () => Promise<void>;
  minimizeWindow: () => Promise<void>;
  maximizeWindow: () => Promise<void>;
  closeWindow: () => Promise<void>;
  toggleDevTools: () => Promise<void>;
  reloadWindow: () => Promise<void>;
  toggleFullscreen: () => Promise<void>;
  setTitle: (title: string) => Promise<void>;
}

// 定义平台信息接口
interface PlatformInfo {
  isElectron: boolean;
  isWindows: boolean;
  isMacOS: boolean;
  isLinux: boolean;
}

// 声明全局变量，使TypeScript能够识别window上的Electron API
declare global {
  interface Window {
    electronAPI?: ElectronAPI;
    platform?: PlatformInfo;
  }
}

/**
 * 判断当前是否在Electron环境中运行
 */
export const isElectron = (): boolean => {
  return Boolean(window.platform?.isElectron);
};

/**
 * 获取平台信息
 */
export const getPlatformInfo = (): PlatformInfo => {
  if (isElectron()) {
    return window.platform as PlatformInfo;
  }
  
  // 浏览器环境下的默认平台信息
  return {
    isElectron: false,
    isWindows: navigator.userAgent.indexOf('Windows') !== -1,
    isMacOS: navigator.userAgent.indexOf('Macintosh') !== -1,
    isLinux: navigator.userAgent.indexOf('Linux') !== -1
  };
};

/**
 * 安全地调用Electron API
 * @param apiName 要调用的API名称
 * @param args API参数
 * @returns API调用结果，如果不在Electron环境中则返回错误
 */
export const callElectron = async <T>(
  apiName: keyof ElectronAPI,
  ...args: any[]
): Promise<T | { success: false; error: string }> => {
  if (!isElectron() || !window.electronAPI) {
    return {
      success: false,
      error: 'Electron API not available'
    };
  }
  
  try {
    // @ts-ignore - 动态调用API
    return await window.electronAPI[apiName](...args);
  } catch (error) {
    return {
      success: false,
      error: (error as Error).message || 'Unknown error'
    };
  }
};

/**
 * 保存文件
 * @param data 要保存的数据
 * @param defaultPath 默认保存路径
 * @param filters 文件类型过滤器
 */
export const saveFile = async (
  data: string | Blob | ArrayBuffer,
  defaultPath: string,
  filters?: Array<{ name: string; extensions: string[] }>
) => {
  // 如果是Electron环境，使用Electron API
  if (isElectron()) {
    let fileData: string;
    
    // 将数据转换为字符串
    if (typeof data === 'string') {
      fileData = data;
    } else if (data instanceof Blob) {
      fileData = await data.text();
    } else if (data instanceof ArrayBuffer) {
      fileData = new TextDecoder().decode(data);
    } else {
      fileData = JSON.stringify(data);
    }
    
    // 调用Electron API
    return await callElectron<{
      success: boolean;
      path?: string;
      error?: string;
      canceled?: boolean;
    }>('saveFile', fileData, defaultPath, filters);
  }
  
  // 浏览器环境下使用下载API
  try {
    const blob = data instanceof Blob 
      ? data 
      : data instanceof ArrayBuffer 
        ? new Blob([data]) 
        : new Blob([data], { type: 'text/plain' });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = defaultPath.split('/').pop() || 'download';
    a.click();
    
    // 清理URL对象
    setTimeout(() => URL.revokeObjectURL(url), 100);
    
    return {
      success: true,
      path: a.download
    };
  } catch (error) {
    return {
      success: false,
      error: (error as Error).message
    };
  }
};

/**
 * 打开文件
 * @param filters 文件类型过滤器
 * @param properties 文件选择属性
 */
export const openFile = async (
  filters?: Array<{ name: string; extensions: string[] }>,
  properties?: string[]
) => {
  // 如果是Electron环境，使用Electron API
  if (isElectron()) {
    return await callElectron<{
      success: boolean;
      path?: string;
      content?: string;
      error?: string;
      canceled?: boolean;
    }>('openFile', filters, properties);
  }
  
  // 浏览器环境下使用文件选择API
  try {
    return new Promise<{
      success: boolean;
      path?: string;
      content?: string;
      error?: string;
      canceled?: boolean;
    }>((resolve) => {
      const input = document.createElement('input');
      input.type = 'file';
      
      // 设置接受的文件类型
      if (filters && filters.length > 0) {
        const mimeTypes = filters
          .flatMap(filter => filter.extensions.map(ext => `.${ext}`))
          .join(',');
        input.accept = mimeTypes;
      }
      
      input.onchange = async (event) => {
        const files = (event.target as HTMLInputElement).files;
        
        if (!files || files.length === 0) {
          resolve({
            success: false,
            canceled: true
          });
          return;
        }
        
        const file = files[0];
        try {
          const content = await file.text();
          resolve({
            success: true,
            path: file.name,
            content
          });
        } catch (error) {
          resolve({
            success: false,
            error: (error as Error).message
          });
        }
      };
      
      // 用户取消选择
      input.oncancel = () => {
        resolve({
          success: false,
          canceled: true
        });
      };
      
      // 触发文件选择
      input.click();
    });
  } catch (error) {
    return {
      success: false,
      error: (error as Error).message
    };
  }
};

/**
 * 打开外部链接
 * @param url 要打开的URL
 */
export const openExternal = async (url: string) => {
  // 如果是Electron环境，使用Electron API
  if (isElectron()) {
    return await callElectron<{
      success: boolean;
      error?: string;
    }>('openExternal', url);
  }
  
  // 浏览器环境下直接打开链接
  try {
    window.open(url, '_blank', 'noopener,noreferrer');
    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: (error as Error).message
    };
  }
};

/**
 * 获取应用版本
 */
export const getAppVersion = async (): Promise<string> => {
  // 如果是Electron环境，使用Electron API
  if (isElectron()) {
    const result = await callElectron<string>('getAppVersion');
    if (typeof result === 'string') {
      return result;
    }
    return 'unknown';
  }
  
  // 浏览器环境下返回前端版本
  return import.meta.env.VITE_APP_VERSION || 'web';
};

/**
 * 发送系统通知
 * @param title 通知标题
 * @param body 通知内容
 * @param silent 是否静音
 */
export const sendNotification = (
  title: string,
  body: string,
  silent: boolean = false
) => {
  // 检查浏览器通知权限
  const checkNotificationPermission = async (): Promise<boolean> => {
    if (Notification.permission === 'granted') {
      return true;
    }
    
    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    
    return false;
  };
  
  // 如果是Electron环境，使用Electron API
  if (isElectron() && window.electronAPI) {
    return window.electronAPI.sendNotification(title, body, silent);
  }
  
  // 浏览器环境下使用Web Notifications API
  const sendBrowserNotification = async () => {
    const hasPermission = await checkNotificationPermission();
    
    if (!hasPermission) {
      console.warn('Notification permission not granted');
      return null;
    }
    
    const notification = new Notification(title, {
      body,
      silent
    });
    
    return {
      notification,
      onClick: (callback: () => void) => {
        notification.onclick = callback;
      }
    };
  };
  
  return sendBrowserNotification();
}; 