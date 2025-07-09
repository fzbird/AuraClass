# AuraClass 班级量化管理软件 - 前端设计文档

## 1. 概述

本文档详细描述 AuraClass 班级量化管理软件的前端设计方案，包括技术选型、架构设计、功能模块、开发规范和实施计划等内容。前端设计遵循现代化、组件化、响应式的设计理念，确保系统的可用性、可维护性和扩展性。

## 2. 技术栈选型

### 2.1 核心框架

- **Vue 3**：使用 Composition API 构建响应式用户界面
- **TypeScript**：提供类型支持，增强代码健壮性
- **Vite**：作为构建工具，提供快速的开发体验

### 2.2 UI 组件库

- **Naive UI**：基于 Vue 3 的组件库，提供现代化 UI 组件
- **Tailwind CSS**：实用优先的 CSS 框架，用于自定义样式
- **SCSS**：预处理器，用于组织和管理样式

### 2.3 状态管理

- **Pinia**：Vue 3 官方推荐的状态管理库，提供简洁、类型安全的 API

### 2.4 路由

- **Vue Router 4**：Vue.js 官方路由管理器

### 2.5 网络请求

- **Axios**：基于 Promise 的 HTTP 客户端，用于与后端 API 通信
- **Native WebSocket**：用于实时通信功能

### 2.6 数据可视化

- **ECharts 5**：功能丰富的交互式图表库

### 2.7 工具库

- **Day.js**：轻量级的日期处理库
- **Lodash-es**：实用函数库，使用 ES 模块版本
- **Vue Use**：Vue 3 组合式 API 工具集

### 2.8 跨平台支持

- **Electron**：桌面应用封装
- **Capacitor**：移动应用封装

## 3. 前端架构设计

### 3.1 整体架构

```
+-----------------------------------+
|            应用容器               |
|  +----------------------------+   |
|  |          布局组件          |   |
|  |  +----------------------+  |   |
|  |  |      功能模块        |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  |  业务组件    |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  |  |  通用组件    |   |  |   |
|  |  |  +--------------+   |  |   |
|  |  +----------------------+  |   |
|  +----------------------------+   |
+-----------------------------------+
         |              |
         v              v
+---------------+  +---------------+
|   状态管理    |  |  API 服务层   |
|   (Pinia)     |  |   (Axios)     |
+---------------+  +---------------+
```

### 3.2 目录结构

```
src/
├── assets/            # 静态资源文件
│   ├── icons/         # 图标文件
│   ├── images/        # 图片资源
│   └── styles/        # 全局样式
├── components/        # 组件
│   ├── common/        # 通用组件
│   ├── layout/        # 布局组件
│   └── business/      # 业务组件
├── composables/       # 组合式函数
├── config/            # 配置文件
├── hooks/             # 自定义 hooks
├── pages/             # 页面组件
│   ├── dashboard/     # 仪表盘页面
│   ├── students/      # 学生管理页面
│   ├── quant-items/   # 量化项目页面
│   ├── records/       # 量化记录页面
│   ├── statistics/    # 统计分析页面
│   ├── notification/  # 通知管理页面
│   ├── settings/      # 设置页面
│   └── ai-assistant/  # AI 助手页面
├── router/            # 路由配置
├── services/          # API 服务
│   ├── api/           # API 请求函数
│   ├── websocket/     # WebSocket 服务
│   └── http.ts        # HTTP 客户端配置
├── stores/            # Pinia 状态管理
├── types/             # TypeScript 类型定义
├── utils/             # 工具函数
├── App.vue            # 根组件
├── main.ts            # 入口文件
├── env.d.ts           # 环境变量类型定义
└── shims-vue.d.ts     # Vue 模块声明
```

## 4. 功能模块设计

### 4.1 核心模块

#### 4.1.1 认证模块

- 登录/注销功能
- 用户信息管理
- 权限控制
- 会话管理

#### 4.1.2 仪表盘模块

- 数据概览
- 快速操作入口
- 最近活动
- 通知提醒

#### 4.1.3 学生管理模块

- 学生列表
- 学生信息详情
- 添加/编辑/删除学生
- 学生量化记录查看

#### 4.1.4 量化项目模块

- 量化项目列表
- 量化项目详情
- 添加/编辑/删除量化项目
- 项目分类管理

#### 4.1.5 量化记录模块

- 记录列表
- 记录详情
- 添加/编辑/删除记录
- 批量录入记录
- 记录筛选与搜索

#### 4.1.6 统计分析模块

- 总体统计概览
- 学生排名
- 班级对比
- 时间序列分析
- 数据导出

#### 4.1.7 通知管理模块

- 通知列表
- 通知创建
- 通知阅读状态
- 通知筛选

#### 4.1.8 AI 助手模块

- 查询界面
- 对话历史
- 建议功能
- 数据分析辅助

#### 4.1.9 系统设置模块

- 用户个人设置
- 系统配置
- 主题与界面设置
- 权限管理

### 4.2 跨平台适配模块

#### 4.2.1 桌面端适配

- 系统托盘
- 通知集成
- 快捷键支持
- 离线存储

#### 4.2.2 移动端适配

- 响应式布局
- 触摸操作优化
- 设备功能集成
- 离线模式

## 5. 组件设计

### 5.1 通用组件

- **AppButton**: 统一按钮样式
- **AppInput**: 输入框组件
- **AppSelect**: 下拉选择组件
- **AppTable**: 数据表格组件
- **AppPagination**: 分页组件
- **AppCard**: 卡片容器组件
- **AppModal**: 模态框组件
- **AppAlert**: 提示组件
- **AppTabs**: 标签页组件
- **AppSearch**: 搜索组件
- **AppUpload**: 文件上传组件
- **AppAvatar**: 头像组件
- **AppSpinner**: 加载动画组件
- **AppBadge**: 徽章组件
- **AppIcon**: 图标组件

### 5.2 布局组件

- **MainLayout**: 主布局
- **HeaderComponent**: 顶部导航栏
- **SidebarComponent**: 侧边导航栏
- **FooterComponent**: 页脚组件
- **BreadcrumbsComponent**: 面包屑导航
- **PageContainer**: 页面容器

### 5.3 业务组件

- **StudentCard**: 学生信息卡片
- **StudentForm**: 学生信息表单
- **QuantItemCard**: 量化项目卡片
- **QuantItemForm**: 量化项目表单
- **RecordForm**: 量化记录表单
- **BatchRecordInput**: 批量记录输入
- **StatisticChart**: 统计图表组件
- **RankingList**: 排名列表组件
- **NotificationItem**: 通知项组件
- **AIAssistantChat**: AI 助手对话组件
- **PermissionSelector**: 权限选择组件

## 6. 状态管理设计

### 6.1 Pinia Store 设计

#### 6.1.1 核心 Store

- **UserStore**: 用户信息和认证状态
- **PermissionStore**: 权限控制
- **AppStore**: 应用全局状态

#### 6.1.2 业务 Store

- **StudentStore**: 学生数据管理
- **ClassStore**: 班级数据管理
- **QuantItemStore**: 量化项目数据管理
- **RecordStore**: 量化记录数据管理
- **NotificationStore**: 通知数据管理
- **StatisticsStore**: 统计数据管理
- **AIAssistantStore**: AI 助手状态管理

### 6.2 状态管理原则

- 使用 Composition API 与 TypeScript 结合
- 遵循状态分层原则，避免状态泄漏
- 采用标准化的 actions/mutations 模式
- 合理使用 getters 派生计算状态
- 利用 Pinia 的持久化功能实现状态本地存储

## 7. 路由设计

### 7.1 基础路由

```javascript
const routes = [
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: DashboardPage,
        meta: { title: '仪表盘' }
      },
      // 其他需要 MainLayout 的路由
    ]
  },
  {
    path: '/auth',
    component: AuthLayout,
    meta: { requiresAuth: false },
    children: [
      {
        path: 'login',
        name: 'Login',
        component: LoginPage,
        meta: { title: '登录' }
      },
      // 其他认证相关路由
    ]
  },
  // 错误页面路由
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundPage
  }
]
```

### 7.2 功能模块路由

```javascript
const moduleRoutes = [
  // 学生管理
  {
    path: 'students',
    name: 'Students',
    component: StudentsPage,
    meta: { title: '学生管理', permission: 'view:students' }
  },
  {
    path: 'students/:id',
    name: 'StudentDetail',
    component: StudentDetailPage,
    meta: { title: '学生详情', permission: 'view:students' }
  },
  
  // 量化项目管理
  {
    path: 'quant-items',
    name: 'QuantItems',
    component: QuantItemsPage,
    meta: { title: '量化项目', permission: 'view:quant-items' }
  },
  
  // 量化记录管理
  {
    path: 'records',
    name: 'Records',
    component: RecordsPage,
    meta: { title: '量化记录', permission: 'view:records' }
  },
  {
    path: 'records/create',
    name: 'CreateRecord',
    component: CreateRecordPage,
    meta: { title: '创建记录', permission: 'create:records' }
  },
  
  // 统计分析
  {
    path: 'statistics',
    name: 'Statistics',
    component: StatisticsPage,
    meta: { title: '统计分析', permission: 'view:statistics' }
  },
  
  // 通知管理
  {
    path: 'notifications',
    name: 'Notifications',
    component: NotificationsPage,
    meta: { title: '通知管理', permission: 'view:notifications' }
  },
  
  // AI 助手
  {
    path: 'ai-assistant',
    name: 'AIAssistant',
    component: AIAssistantPage,
    meta: { title: 'AI 助手', permission: 'use:ai-assistant' }
  },
  
  // 系统设置
  {
    path: 'settings',
    name: 'Settings',
    component: SettingsPage,
    meta: { title: '系统设置', permission: 'view:settings' }
  }
]
```

### 7.3 路由守卫设计

```javascript
router.beforeEach(async (to, from, next) => {
  // 权限验证
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - AuraClass` : 'AuraClass'
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }
  
  // 检查权限
  if (to.meta.permission && !permissionStore.hasPermission(to.meta.permission)) {
    return next({ name: 'Forbidden' })
  }
  
  // 正常导航
  next()
})
```

## 8. API 通信设计

### 8.1 HTTP 请求服务

```typescript
// services/http.ts
import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
http.interceptors.response.use(
  response => response.data,
  error => {
    // 统一错误处理
    if (error.response && error.response.status === 401) {
      // 处理未授权错误
    }
    return Promise.reject(error)
  }
)

export default http
```

### 8.2 API 服务

```typescript
// services/api/students.ts
import http from '../http'
import type { Student, CreateStudentPayload, UpdateStudentPayload } from '@/types'

export const getStudents = async (params = {}) => {
  return http.get<Student[]>('/api/v1/students', { params })
}

export const getStudent = async (id: number) => {
  return http.get<Student>(`/api/v1/students/${id}`)
}

export const createStudent = async (data: CreateStudentPayload) => {
  return http.post<Student>('/api/v1/students', data)
}

export const updateStudent = async (id: number, data: UpdateStudentPayload) => {
  return http.put<Student>(`/api/v1/students/${id}`, data)
}

export const deleteStudent = async (id: number) => {
  return http.delete(`/api/v1/students/${id}`)
}

export const getStudentRecords = async (id: number, params = {}) => {
  return http.get(`/api/v1/students/${id}/records`, { params })
}
```

### 8.3 WebSocket 服务

```typescript
// services/websocket/index.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'

export function useWebSocket(endpoint: string) {
  const userStore = useUserStore()
  const socket = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const messages = ref<any[]>([])
  
  const connect = () => {
    const baseUrl = import.meta.env.VITE_WS_BASE_URL
    const token = userStore.token
    
    socket.value = new WebSocket(`${baseUrl}${endpoint}?token=${token}`)
    
    socket.value.onopen = () => {
      isConnected.value = true
    }
    
    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      messages.value.push(data)
    }
    
    socket.value.onclose = () => {
      isConnected.value = false
    }
    
    socket.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }
  
  const disconnect = () => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.close()
    }
  }
  
  const send = (data: any) => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify(data))
    }
  }
  
  onMounted(() => {
    if (userStore.isLoggedIn) {
      connect()
    }
  })
  
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    socket,
    isConnected,
    messages,
    connect,
    disconnect,
    send
  }
}
```

## 9. 页面设计

### 9.1 仪表盘页面

**功能**:
- 数据概览卡片
- 近期活动列表
- 量化记录快速录入
- 待办事项
- 班级排名
- 通知提醒

**组件**:
- DashboardStatCard
- RecentActivityList
- QuickRecordForm
- TodoList
- ClassRankingChart
- NotificationPanel

### 9.2 学生管理页面

**功能**:
- 学生列表
- 筛选和搜索
- 分页
- 批量操作
- 添加/编辑/删除学生

**组件**:
- StudentTable
- StudentFilterForm
- StudentActionBar
- StudentFormModal

### 9.3 量化项目管理页面

**功能**:
- 量化项目列表
- 分类视图
- 添加/编辑/删除项目
- 项目状态管理

**组件**:
- QuantItemTable
- CategoryFilter
- QuantItemFormModal
- StatusToggleButton

### 9.4 量化记录管理页面

**功能**:
- 记录列表
- 高级筛选
- 单条记录录入
- 批量记录录入
- 记录导入/导出

**组件**:
- RecordTable
- RecordFilterForm
- RecordFormModal
- BatchRecordForm
- ImportExportPanel

### 9.5 统计分析页面

**功能**:
- 总体统计概览
- 学生排名
- 班级对比
- 时间序列分析
- 数据导出

**组件**:
- StatisticsSummary
- StudentRankingTable
- ClassComparisonChart
- TimeSeriesChart
- ExportOptions

### 9.6 通知管理页面

**功能**:
- 通知列表
- 通知创建
- 通知详情
- 已读/未读状态管理

**组件**:
- NotificationList
- NotificationFormModal
- NotificationDetailModal
- ReadStatusFilter

### 9.7 AI 助手页面

**功能**:
- 查询输入
- 对话历史
- 智能建议
- 数据分析结果展示

**组件**:
- QueryInputBox
- ConversationHistory
- SuggestionPanel
- AnalysisResultDisplay

## 10. UI/UX 设计规范

### 10.1 设计原则

- **一致性**: 确保界面元素、交互模式和视觉设计保持一致
- **简洁性**: 专注于核心功能，避免视觉杂乱
- **反馈性**: 为用户操作提供明确的反馈
- **可访问性**: 确保界面对不同能力的用户友好
- **用户中心**: 将用户需求和体验放在设计的中心

### 10.2 色彩系统

- **主色调**: #3366FF (主要操作、强调内容)
- **次要色**: #52C41A (成功状态)、#FAAD14 (警告状态)、#F5222D (错误状态)
- **中性色**: #000000 (文本)、#8C8C8C (次要文本)、#D9D9D9 (边框)、#F5F5F5 (背景)
- **主题支持**: 亮色主题和暗色主题

### 10.3 排版

- **主要字体**: 系统默认字体栈
- **标题层级**:
  - H1: 24px, 粗体
  - H2: 20px, 粗体
  - H3: 18px, 粗体
  - H4: 16px, 粗体
- **正文文本**: 14px, 常规
- **小号文本**: 12px, 常规

### 10.4 交互设计

- **按钮状态**: 默认、悬停、激活、禁用
- **表单交互**: 输入验证、错误提示、成功反馈
- **加载状态**: 骨架屏、进度指示器
- **过渡动画**: 页面切换、组件加载/卸载

### 10.5 响应式设计

- 断点设计:
  - 移动端: < 768px
  - 平板: 768px - 1024px
  - 桌面: > 1024px
- 使用弹性布局和网格系统
- 内容优先级调整

## 11. 性能优化策略

### 11.1 代码层面优化

- 使用 Vue 3 的 `defineAsyncComponent` 实现组件懒加载
- 使用 Tree Shaking 减少打包体积
- 避免不必要的组件渲染和重渲染
- 使用虚拟滚动优化长列表性能
- 图片懒加载

### 11.2 网络请求优化

- 请求数据缓存
- 数据预加载
- 使用 HTTP/2
- 启用 Gzip/Brotli 压缩
- API 响应结果缓存

### 11.3 资源加载优化

- 静态资源 CDN 分发
- 图片优化 (WebP 格式, 适当压缩)
- 关键 CSS 内联
- 字体优化

### 11.4 测量与监控

- 使用 Lighthouse 评估性能
- Performance API 监控运行时性能
- 错误监控与上报
- 用户体验指标收集 (CLS, FID, LCP)

## 12. 测试策略

### 12.1 单元测试

- 使用 Vitest 进行组件和工具函数测试
- 测试覆盖率目标: 70%+

### 12.2 组件测试

- 使用 Testing Library 测试组件行为
- 模拟用户交互和事件

### 12.3 集成测试

- 测试组件之间的交互
- API 集成测试

### 12.4 端到端测试

- 使用 Cypress 进行端到端测试
- 关键用户流程测试

### 12.5 性能测试

- 首屏加载时间测试
- 交互响应时间测试

## 13. 部署流程

### 13.1 构建过程

- 使用 Vite 构建优化
- 环境变量配置
- 资源优化 (压缩, Tree Shaking)

### 13.2 版本管理

- 语义化版本控制
- 自动化版本发布

### 13.3 CI/CD 流程

- Pull Request 构建检查
- 自动化测试
- 自动化部署

### 13.4 多平台部署

- Web 版本部署
- Electron 桌面版打包
- Capacitor Android 版构建

## 14. 开发规范

### 14.1 代码风格

- 使用 ESLint 和 Prettier 保持代码风格一致
- 遵循 Vue 3 推荐的最佳实践

### 14.2 命名规范

- 组件名使用 PascalCase
- 文件名使用 kebab-case
- 变量和函数使用 camelCase
- 常量使用 UPPER_SNAKE_CASE

### 14.3 提交规范

- 使用 Conventional Commits 规范
- 提交前运行 lint 检查和测试

### 14.4 文档规范

- 组件文档
- API 文档
- 项目维护文档

## 15. 实施计划

### 15.1 阶段划分

#### 阶段一: 基础框架搭建 (2周)

- 项目初始化
- 核心架构实现
- 基础组件开发
- 路由和状态管理设置

#### 阶段二: 功能模块开发 (6周)

- 认证模块
- 学生管理模块
- 量化项目模块
- 量化记录模块
- 统计分析模块
- 通知模块

#### 阶段三: AI 助手与高级功能 (2周)

- AI 助手实现
- 高级数据分析
- 性能优化

#### 阶段四: 桌面端适配 (2周)

- Electron 集成
- 本地功能实现
- 自动更新机制

#### 阶段五: 移动端适配 (2周)

- Capacitor 集成
- 响应式优化
- 设备功能集成

#### 阶段六: 测试与优化 (2周)

- 单元测试
- 集成测试
- 性能优化
- 用户体验改进

### 15.2 里程碑

1. 基础框架完成 (第2周末)
2. 核心功能模块完成 (第8周末)
3. AI 助手功能完成 (第10周末)
4. 桌面端版本发布 (第12周末)
5. 移动端版本发布 (第14周末)
6. 项目全部完成 (第16周末)

## 16. 风险管理

### 16.1 技术风险

- **WebSocket 性能**：大量并发连接可能导致性能问题
- **移动端兼容性**：不同设备的适配问题
- **离线存储同步**：数据一致性挑战

### 16.2 应对策略

- 进行早期性能测试和负载测试
- 使用渐进式功能检测和优雅降级
- 实现强健的数据同步机制和冲突解决策略

## 17. 总结

本前端设计文档全面描述了 AuraClass 班级量化管理软件的前端设计方案，包括技术选型、架构设计、功能模块、UI/UX 规范和实施计划。遵循本文档的指导，项目团队将能够有序地开展前端开发工作，构建一个功能完善、用户体验良好的现代化 Web 应用。 