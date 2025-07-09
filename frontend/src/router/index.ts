import { createRouter, createWebHistory } from 'vue-router';
import { h } from 'vue';
import { useUserStore } from '@/stores/user';
import { usePermissionStore } from '@/stores/permission';

// 布局组件
import MainLayout from '@/components/layout/MainLayout.vue';
import AuthLayout from '@/components/layout/AuthLayout.vue';

// 懒加载页面组件
const IndexPage = () => import('@/pages/Index.vue');
const DashboardPage = () => import('@/pages/dashboard/index.vue');
const LoginPage = () => import('@/pages/auth/LoginPage.vue');
const StudentsPage = () => import('@/pages/students/StudentsPage.vue');
const StudentDetailPage = () => import('@/pages/students/StudentDetailPage.vue');
const QuantItemsPage = () => import('@/pages/quant-items/QuantItemsPage.vue');
const RecordsPage = () => import('@/pages/records/RecordsPage.vue');
const CreateRecordPage = () => import('@/pages/records/CreateRecordPage.vue');
const StatisticsPage = () => import('@/pages/statistics/StatisticsPage.vue');
const NotificationsPage = () => import('@/pages/notifications/NotificationsPage.vue');
const AIAssistantPage = () => import('@/pages/ai-assistant/AIAssistantPage.vue');
const SettingsPage = () => import('@/pages/settings/SettingsPage.vue');
const NotFoundPage = () => import('@/pages/errors/NotFoundPage.vue');
const ForbiddenPage = () => import('@/pages/errors/ForbiddenPage.vue');

// 在Vue Router 4.5.0+中，我们不需要显式导入RouteRecordRaw类型
const routes = [
  {
    path: '/',
    component: IndexPage,
    meta: { requiresAuth: false, title: '首页' }
  },
  // 应用主布局的路由组
  {
    path: '/app',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: DashboardPage,
        meta: { title: '仪表盘' }
      },
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
        props: true,
        meta: { 
          title: '学生详情', 
          permission: 'view:students',
          keepAlive: false 
        }
      },
      {
        path: 'quant-items',
        name: 'QuantItems',
        component: QuantItemsPage,
        meta: { title: '量化项目', permission: 'view:quant-items' }
      },
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
      {
        path: 'statistics',
        name: 'Statistics',
        component: StatisticsPage,
        meta: { title: '统计分析', permission: 'view:statistics' }
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: NotificationsPage,
        meta: { title: '通知管理', permission: 'view:notifications' }
      },
      {
        path: 'ai-assistant',
        name: 'AIAssistant',
        component: AIAssistantPage,
        meta: { title: 'AI 助手', permission: 'use:ai-assistant' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: SettingsPage,
        meta: { title: '系统设置', permission: 'view:settings' }
      }
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
      }
    ]
  },
  // 独立错误页面
  {
    path: '/forbidden',
    name: 'Forbidden',
    component: ForbiddenPage,
    meta: { title: '访问受限', requiresAuth: false }
  },
  // 重定向旧的直接路径到新的嵌套路由
  {
    path: '/dashboard',
    redirect: '/app/dashboard',
  },
  // 错误页面路由
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundPage,
    meta: { title: '页面未找到', requiresAuth: false }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: (to, from, savedPosition) => {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();
  const permissionStore = usePermissionStore();
  
  // 检查路由是否需要验证
  if (to.meta.requiresAuth) {
    try {
      // 使用正确的函数名
      if (!permissionStore.isInitialized) {
        console.log('权限未初始化，正在获取用户信息...');
        // 使用正确的方法名
        await userStore.fetchUserInfo();
        await permissionStore.loadPermissions(); // 而不是waitForInitialization
      }
      
      // 检查权限
      const requiredPermission = to.meta.permission as string | undefined;
      if (requiredPermission && !permissionStore.hasPermission(requiredPermission)) {
        console.log('权限不足，重定向到403页面');
        next('/forbidden');
        return;
      }
      
      // 有权限继续访问
      next();
    } catch (error) {
      console.error('权限验证失败:', error);
      next('/login');
    }
  } else {
    // 不需要认证的路由直接放行
    next();
  }
});

// 全局后置钩子 - 设置页面标题
router.afterEach((to) => {
  // 应用名称和版本
  const appName = 'AuraClass v1.0';
  
  // 默认标题
  let pageTitle = appName;
  
  // 如果路由元数据中包含标题，则使用该标题
  if (to.meta.title) {
    pageTitle = `${to.meta.title} — ${appName}`;
  } else if (to.name) {
    // 如果没有标题但有路由名称，则使用路由名称
    pageTitle = `${String(to.name)} — ${appName}`;
  }
  
  // 更新文档标题
  document.title = pageTitle;
  
  // 记录页面访问（可用于分析）
  console.debug(`访问页面: ${pageTitle}`);
});

export default router;
