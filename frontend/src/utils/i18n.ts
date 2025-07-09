import { ref, computed, watch } from 'vue';

// 支持的语言列表
export const supportedLocales = ['zh-CN', 'en-US'] as const;
export type LocaleType = typeof supportedLocales[number];

// 当前语言
export const currentLocale = ref<LocaleType>(
  localStorage.getItem('auraclass_locale') as LocaleType || getBrowserLocale() || 'zh-CN'
);

// 获取浏览器语言
function getBrowserLocale(): LocaleType | null {
  const browserLocale = navigator.language;
  return supportedLocales.find(locale => browserLocale.startsWith(locale.split('-')[0])) || null;
}

// 中文消息
const zhMessages: Record<string, string> = {
  // 通用
  'common.yes': '是',
  'common.no': '否',
  'common.ok': '确定',
  'common.cancel': '取消',
  'common.save': '保存',
  'common.delete': '删除',
  'common.edit': '编辑',
  'common.add': '添加',
  'common.search': '搜索',
  'common.confirm': '确认',
  'common.loading': '加载中...',
  'common.noData': '暂无数据',
  'common.more': '更多',
  'common.all': '全部',
  
  // 导航
  'nav.dashboard': '仪表盘',
  'nav.students': '学生管理',
  'nav.classes': '班级管理',
  'nav.quantItems': '量化项目',
  'nav.records': '量化记录',
  'nav.statistics': '统计分析',
  'nav.settings': '系统设置',
  'nav.aiAssistant': 'AI助手',
  
  // 用户相关
  'user.login': '登录',
  'user.logout': '退出登录',
  'user.username': '用户名',
  'user.password': '密码',
  'user.role': '角色',
  'user.profile': '个人资料',
  'user.settings': '个人设置',
  
  // 消息通知
  'notification.success': '操作成功',
  'notification.error': '操作失败',
  'notification.warning': '警告',
  'notification.info': '提示',
  
  // 离线模式
  'offline.title': '离线模式',
  'offline.enable': '启用离线模式',
  'offline.disable': '禁用离线模式',
  'offline.sync': '同步数据',
  'offline.syncComplete': '数据同步完成',
  'offline.pendingSync': '待同步项',
  'offline.lastSync': '上次同步',
  'offline.networkError': '网络连接错误',
  'offline.networkReconnected': '网络已恢复连接',
  
  // 统计分析
  'stats.overview': '总体统计',
  'stats.ranking': '排名',
  'stats.trend': '趋势分析',
  'stats.comparison': '对比分析',
  'stats.export': '导出数据',
  
  // 时间相关
  'time.today': '今天',
  'time.yesterday': '昨天',
  'time.thisWeek': '本周',
  'time.lastWeek': '上周',
  'time.thisMonth': '本月',
  'time.lastMonth': '上月',
  'time.thisYear': '今年',
  'time.lastYear': '去年',
  'time.custom': '自定义'
};

// 英文消息
const enMessages: Record<string, string> = {
  // Common
  'common.yes': 'Yes',
  'common.no': 'No',
  'common.ok': 'OK',
  'common.cancel': 'Cancel',
  'common.save': 'Save',
  'common.delete': 'Delete',
  'common.edit': 'Edit',
  'common.add': 'Add',
  'common.search': 'Search',
  'common.confirm': 'Confirm',
  'common.loading': 'Loading...',
  'common.noData': 'No Data',
  'common.more': 'More',
  'common.all': 'All',
  
  // Navigation
  'nav.dashboard': 'Dashboard',
  'nav.students': 'Students',
  'nav.classes': 'Classes',
  'nav.quantItems': 'Quant Items',
  'nav.records': 'Records',
  'nav.statistics': 'Statistics',
  'nav.settings': 'Settings',
  'nav.aiAssistant': 'AI Assistant',
  
  // User related
  'user.login': 'Login',
  'user.logout': 'Logout',
  'user.username': 'Username',
  'user.password': 'Password',
  'user.role': 'Role',
  'user.profile': 'Profile',
  'user.settings': 'User Settings',
  
  // Notifications
  'notification.success': 'Success',
  'notification.error': 'Error',
  'notification.warning': 'Warning',
  'notification.info': 'Information',
  
  // Offline mode
  'offline.title': 'Offline Mode',
  'offline.enable': 'Enable Offline Mode',
  'offline.disable': 'Disable Offline Mode',
  'offline.sync': 'Sync Data',
  'offline.syncComplete': 'Data Synchronization Complete',
  'offline.pendingSync': 'Pending Sync Items',
  'offline.lastSync': 'Last Sync',
  'offline.networkError': 'Network Connection Error',
  'offline.networkReconnected': 'Network Connection Restored',
  
  // Statistics
  'stats.overview': 'Overview',
  'stats.ranking': 'Ranking',
  'stats.trend': 'Trend Analysis',
  'stats.comparison': 'Comparison',
  'stats.export': 'Export Data',
  
  // Time related
  'time.today': 'Today',
  'time.yesterday': 'Yesterday',
  'time.thisWeek': 'This Week',
  'time.lastWeek': 'Last Week',
  'time.thisMonth': 'This Month',
  'time.lastMonth': 'Last Month',
  'time.thisYear': 'This Year',
  'time.lastYear': 'Last Year',
  'time.custom': 'Custom Range'
};

// 消息库
const messages: Record<LocaleType, Record<string, string>> = {
  'zh-CN': zhMessages,
  'en-US': enMessages
};

// 切换语言
export function setLocale(locale: LocaleType): void {
  if (!supportedLocales.includes(locale)) {
    console.warn(`Unsupported locale: ${locale}`);
    return;
  }
  
  currentLocale.value = locale;
  localStorage.setItem('auraclass_locale', locale);
  
  // 设置HTML lang属性
  document.documentElement.setAttribute('lang', locale);
}

// 翻译函数
export function t(key: string, params?: Record<string, string | number>): string {
  const message = messages[currentLocale.value][key] || key;
  
  if (!params) {
    return message;
  }
  
  // 替换参数
  return message.replace(/\{(\w+)\}/g, (_, paramKey) => {
    return String(params[paramKey] !== undefined ? params[paramKey] : `{${paramKey}}`);
  });
}

// 使用翻译函数钩子
export function useI18n() {
  // 翻译函数
  const translate = (key: string, params?: Record<string, string | number>): string => {
    return t(key, params);
  };
  
  // 切换语言
  const changeLocale = (locale: LocaleType): void => {
    setLocale(locale);
  };
  
  // 判断是否为当前语言
  const isCurrentLocale = (locale: LocaleType): boolean => {
    return currentLocale.value === locale;
  };
  
  // 获取语言名称
  const getLocaleName = (locale: LocaleType): string => {
    const nameMap: Record<LocaleType, string> = {
      'zh-CN': '简体中文',
      'en-US': 'English'
    };
    return nameMap[locale];
  };
  
  return {
    t: translate,
    currentLocale: computed(() => currentLocale.value),
    supportedLocales,
    changeLocale,
    isCurrentLocale,
    getLocaleName
  };
}

// 初始化
watch(currentLocale, (locale) => {
  document.documentElement.setAttribute('lang', locale);
}, { immediate: true });

export default {
  install(app: any) {
    app.config.globalProperties.$t = t;
    app.provide('i18n', useI18n());
  }
}; 