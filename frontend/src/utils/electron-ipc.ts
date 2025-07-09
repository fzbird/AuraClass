// electron-ipc.ts
// 定义IPC通信的类型和方法

/**
 * IPC消息类型
 */
export enum IpcChannels {
  SAVE_FILE = 'save-file',
  OPEN_FILE = 'open-file',
  OPEN_EXTERNAL = 'open-external',
  GET_APP_VERSION = 'get-app-version',
  SAVE_APP_CONFIG = 'save-app-config',
  GET_APP_CONFIG = 'get-app-config',
  SEND_NOTIFICATION = 'send-notification',
  CHECK_FOR_UPDATES = 'check-for-updates',
  DOWNLOAD_UPDATE = 'download-update',
  UPDATE_AVAILABLE = 'update-available',
  UPDATE_DOWNLOADED = 'update-downloaded',
  UPDATE_ERROR = 'update-error',
  UPDATE_PROGRESS = 'update-progress',
  RESTART_APP = 'restart-app',
  MINIMIZE_WINDOW = 'minimize-window',
  MAXIMIZE_WINDOW = 'maximize-window',
  CLOSE_WINDOW = 'close-window',
  APP_QUIT = 'app-quit',
  TOGGLE_DEVTOOLS = 'toggle-devtools',
  RELOAD_WINDOW = 'reload-window',
  TOGGLE_FULLSCREEN = 'toggle-fullscreen',
  SET_TITLE = 'set-title'
}

/**
 * 文件过滤器类型
 */
export interface FileFilter {
  name: string;
  extensions: string[];
}

/**
 * 文件保存选项
 */
export interface SaveDialogOptions {
  title?: string;
  defaultPath?: string;
  buttonLabel?: string;
  filters?: FileFilter[];
  message?: string;
  nameFieldLabel?: string;
  showOverwriteConfirmation?: boolean;
}

/**
 * 文件保存结果
 */
export interface SaveDialogResult {
  success: boolean;
  path?: string;
  error?: string;
  canceled?: boolean;
}

/**
 * 文件打开选项
 */
export interface OpenDialogOptions {
  title?: string;
  defaultPath?: string;
  buttonLabel?: string;
  filters?: FileFilter[];
  properties?: Array<
    | 'openFile'
    | 'openDirectory'
    | 'multiSelections'
    | 'showHiddenFiles'
    | 'createDirectory'
    | 'promptToCreate'
    | 'noResolveAliases'
    | 'treatPackageAsDirectory'
    | 'dontAddToRecent'
  >;
  message?: string;
}

/**
 * 文件打开结果
 */
export interface OpenDialogResult {
  success: boolean;
  paths?: string[];
  path?: string;
  content?: string;
  error?: string;
  canceled?: boolean;
}

/**
 * 应用配置类型
 */
export interface AppConfig {
  minToTray: boolean;
  startAtLogin: boolean;
  checkForUpdates: boolean;
  theme: 'system' | 'light' | 'dark';
  language: string;
  [key: string]: any;
}

/**
 * 应用配置保存结果
 */
export interface AppConfigResult {
  success: boolean;
  error?: string;
}

/**
 * 更新信息
 */
export interface UpdateInfo {
  version: string;
  releaseDate: string;
  releaseNotes?: string;
  files?: Array<{
    url: string;
    size: number;
    sha512?: string;
  }>;
}

/**
 * 更新进度信息
 */
export interface UpdateProgress {
  percent: number;
  bytesPerSecond: number;
  total: number;
  transferred: number;
  delta: number;
}

/**
 * 通知选项
 */
export interface NotificationOptions {
  title: string;
  body: string;
  silent?: boolean;
  icon?: string;
  timeoutType?: 'default' | 'never';
  urgency?: 'normal' | 'critical' | 'low';
  closeButtonText?: string;
  actions?: Array<{
    text: string;
    type: 'button';
  }>;
} 