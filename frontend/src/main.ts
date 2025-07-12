import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import './assets/styles/tailwind.css'
import 'katex/dist/katex.min.css'
import { initAppSettings } from './services/api/settings'
import i18n from './utils/i18n'
import { loadWsConfigFromSettings, autoConfigureWebSocket } from './services/websocket/config'
import { useUserStore } from './stores/user'
import { useWebSocketStore } from './stores/websocket'
import naive from 'naive-ui'

// 全局处理未捕获的Promise异常
window.addEventListener('unhandledrejection', (event) => {
  // 忽略翻译API相关的错误
  if (event.reason && 
      ((typeof event.reason === 'object' && 'cmd' in event.reason && event.reason.cmd === 'beacon-report-mes') ||
       (event.reason.toString().includes('translate-api')))) {
    // 阻止默认处理（例如将错误输出到控制台）
    event.preventDefault();
    console.debug('Ignored translation related error:', event.reason);
  }
});

// 创建Pinia实例
const pinia = createPinia()

// 初始化应用
const app = createApp(App)

// 注册插件
app.use(pinia)
app.use(router)
app.use(i18n)
app.use(naive)

// 初始化WebSocket配置
// 检查WebSocket支持并自动配置
const wsStatus = autoConfigureWebSocket();
if (import.meta.env.DEV) {
  console.info('WebSocket自动配置结果:', wsStatus);
}

// 如果自动配置失败，使用默认配置
if (!wsStatus.enabled) {
  // 从环境变量加载配置（可以被后续的settings API覆盖）
  loadWsConfigFromSettings({
    enable_websocket: true,
    websocket_heartbeat_interval: 30,
    websocket_max_reconnect: 5,
    websocket_reconnect_interval: 3
  });
  console.info('已加载WebSocket默认配置');
}

// 挂载应用
app.mount('#app')

// 尝试初始化应用设置（在挂载后异步加载）
initAppSettings().catch(error => {
  console.error('Failed to initialize app settings:', error)
})

// 在应用挂载后初始化WebSocket连接
const userStore = useUserStore()
const wsStore = useWebSocketStore()

// 如果用户已登录，确保WebSocket连接已建立
if (userStore.isLoggedIn) {
  wsStore.updateConfig({ enabled: true })
  console.info('用户已登录，已更新WebSocket配置为enabled=true');
}

export default app
