<template>
  <div>
    <div style="display: flex; align-items: center; margin-bottom: 1.5rem; width: 100%;">
      <!-- 左侧区域 -->
      <div style="display: flex; align-items: center; margin-right: 16px;">
        <h1 style="font-size: 1.5rem; font-weight: bold; margin-right: 24px;">通知管理</h1>

        <n-radio-group v-model:value="readStatus" size="medium" @update:value="fetchNotifications">
          <n-radio-button value="all">全部</n-radio-button>
          <n-radio-button value="read">已读</n-radio-button>
          <n-radio-button value="unread">未读</n-radio-button>
        </n-radio-group>
      </div>

      <!-- 占位区域，强制右侧元素靠右 -->
      <div style="flex-grow: 1;"></div>

      <!-- 右侧区域 -->
      <div style="display: flex; align-items: center;">
        <n-input v-model:value="searchText" :loading="isSearching" placeholder="搜索通知标题或内容" clearable @update:value="handleSearch"
          style="width: 250px; margin-right: 16px;" @keydown.enter="handleSearchEnter">
          <template #prefix>
            <n-icon><search-outlined /></n-icon>
          </template>
        </n-input>

        <n-button type="primary" @click="openCreateNotificationModal">
          <template #icon>
            <n-icon><plus-outlined /></n-icon>
          </template>
          创建通知
        </n-button>
      </div>
    </div>
    <n-card>
      <!-- 搜索状态提示 -->
      <template #header>
        <div v-if="isSearchActive" class="search-indicator">
          搜索 "{{ searchText }}" 的结果：找到 {{ total }} 条通知
          <n-button text type="primary" @click="clearSearch">
            清除搜索
          </n-button>
        </div>
      </template>
      
      <n-spin :show="loading">
        <n-empty v-if="!loading && notifications.length === 0" 
                 :description="isSearchActive ? `没有找到包含 '${searchText}' 的通知` : '暂无通知'" />

        <div v-else>
          <notification-item v-for="notification in notifications" :key="notification.id" :notification="notification"
            :deleting-ids="deletingIds" @mark-read="markNotificationRead" @delete="deleteNotification" @view="viewNotificationDetail" />
        </div>

        <div class="flex justify-center mt-4">
          <n-pagination v-model:page="page" v-model:page-size="pageSize" :item-count="total" :page-sizes="[10, 20, 50]"
            @update:page="fetchNotifications" @update:page-size="handlePageSizeChange" />
        </div>
      </n-spin>
    </n-card>

    <!-- 创建通知模态框 -->
    <notification-form-modal v-model:show="showCreateModal" @success="handleNotificationCreated" />

    <!-- 通知详情模态框 -->
    <notification-detail-modal v-model:show="showDetailModal" :notification="selectedNotification" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import {
  NButton, NCard, NRadioGroup, NRadioButton, NInput,
  NSpin, NPagination, NEmpty, NIcon, useMessage, useDialog
} from 'naive-ui';
import { PlusOutlined, SearchOutlined } from '@vicons/antd';
import debounce from 'lodash-es/debounce';
import { getNotifications, markAsRead } from '@/services/api/notifications';
import { useNotificationStore } from '@/stores/notification';
import NotificationItem from '@/components/business/NotificationItem.vue';
import NotificationFormModal from '@/components/business/NotificationFormModal.vue';
import NotificationDetailModal from '@/components/business/NotificationDetailModal.vue';
import { extractNotificationsFromResponse } from '@/utils/notification-helpers';
import type { Notification as AppNotification } from '@/types/notification';

// 定义API参数接口
interface NotificationParams {
  skip: number;
  limit: number;
  unread_only?: boolean;
  search?: string;
}

// 使用页面特定的通知类型，与API应用中的Notification类型区分
interface PageNotification {
  id: number;
  title: string;
  content: string;
  is_read: boolean;
  created_at: string;
  sender_name?: string;
  [key: string]: any; // 允许其他属性
}

const message = useMessage();
const dialog = useDialog();
const notificationStore = useNotificationStore();
const loading = ref(false);
const isSearching = ref(false); // 搜索中状态
const notifications = ref<PageNotification[]>([]);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const readStatus = ref('all');
const searchText = ref('');
const showCreateModal = ref(false);
const showDetailModal = ref(false);
const selectedNotification = ref<PageNotification | null>(null);
const deletingIds = ref<Set<number>>(new Set()); // 记录正在删除的通知ID

// 计算是否处于搜索状态
const isSearchActive = computed(() => {
  return searchText.value && searchText.value.trim() !== '';
});

onMounted(() => {
  fetchNotifications();
});

const fetchNotifications = async () => {
  loading.value = true;
  
  // 如果是搜索请求，设置搜索中状态
  if (isSearchActive.value) {
    isSearching.value = true;
  }

  try {
    // 构建API参数对象
    const params: NotificationParams = {
      skip: (page.value - 1) * pageSize.value, // 后端API使用skip而不是page
      limit: pageSize.value,
    };

    // 处理已读/未读筛选
    if (readStatus.value === 'unread') {
      params.unread_only = true;
    }
    // 'read'和'all'状态由前端处理，因为后端API不直接支持"仅已读"过滤

    // 处理搜索文本
    if (searchText.value && searchText.value.trim()) {
      params.search = searchText.value.trim();
    }

    console.log('通知查询参数:', params);
    const response = await getNotifications(params);
    console.log('通知响应:', response);

    // 使用工具函数处理响应
    const { notifications: fetchedNotifications, total: totalCount } = 
      extractNotificationsFromResponse(response);
    
    // 转换为页面使用的通知类型
    const pageNotifications = fetchedNotifications.map(n => ({
      id: n.id,
      title: n.title,
      content: n.content,
      is_read: n.isRead,
      created_at: n.createdAt,
      sender_name: n.senderName,
      recipient_user_id: n.recipientId,
      sender_id: n.senderId,
      // 添加其他需要的字段
    }));
    
    // 如果选择了"已读"筛选，后端API不支持直接筛选已读通知，在前端进行筛选
    if (readStatus.value === 'read') {
      notifications.value = pageNotifications.filter(item => item.is_read);
      // 更新总数，反映过滤后的结果
      total.value = notifications.value.length;
    } else {
      notifications.value = pageNotifications;
      total.value = totalCount;
    }
  } catch (error) {
    console.error('获取通知列表失败:', error);
    message.error('获取通知列表失败');
    notifications.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
    isSearching.value = false;
  }
};

const handleSearch = debounce(() => {
  page.value = 1;
  fetchNotifications();
}, 300);

// 处理按下Enter键搜索
const handleSearchEnter = (e: KeyboardEvent) => {
  e.preventDefault();
  // 立即触发搜索，不使用防抖
  page.value = 1;
  fetchNotifications();
};

// 清除搜索
const clearSearch = () => {
  searchText.value = '';
  page.value = 1;
  fetchNotifications();
  message.success('已清除搜索条件');
};

const handlePageSizeChange = () => {
  page.value = 1;
  fetchNotifications();
};

const openCreateNotificationModal = () => {
  showCreateModal.value = true;
};

const handleNotificationCreated = () => {
  message.success('通知创建成功');
  fetchNotifications();
};

const markNotificationRead = async (id: number) => {
  try {
    await markAsRead(id);

    // 更新本地状态
    const index = notifications.value.findIndex(n => n.id === id);
    if (index !== -1) {
      notifications.value[index].is_read = true;
    }

    message.success('标记为已读');
  } catch (error) {
    console.error('标记通知为已读失败:', error);
    message.error('标记为已读失败');
  }
};

const deleteNotification = async (notification: PageNotification) => {
  try {
    // 使用确认对话框
    dialog.warning({
      title: '确认删除',
      content: '确定要删除这条通知吗？',
      positiveText: '确定',
      negativeText: '取消',
      onPositiveClick: async () => {
        loading.value = true;
        deletingIds.value.add(notification.id);
        
        // 使用store的remove方法
        const result = await notificationStore.remove(notification.id);
        
        if (result.success) {
          // 删除成功
          message.success(result.message);
          
          // 从本地列表中移除
          notifications.value = notifications.value.filter(n => n.id !== notification.id);
          
          // 如果当前页没有通知了且不是第一页，则回到上一页
          if (notifications.value.length === 0 && page.value > 1) {
            page.value--;
            fetchNotifications();
          }
        } else {
          // 删除失败，根据错误类型显示不同的提示
          if (result.code === 403) {
            if (result.subtype === 'read_notification') {
              // 已读通知不可删除错误
              dialog.error({
                title: '已读通知不可删除',
                content: '您作为发送者，无法删除已被阅读的通知',
                positiveText: '我知道了'
              });
            } else {
              // 权限不足错误
              dialog.error({
                title: '权限不足',
                content: '您没有删除权限。只有管理员、通知接收者或发送者（限未读通知）可以删除通知。',
                positiveText: '我知道了'
              });
            }
          } else if (result.code === 404) {
            // 通知不存在，可能已被删除
            message.info('通知不存在或已被删除，将从列表中移除');
            // 从本地列表中移除
            notifications.value = notifications.value.filter(n => n.id !== notification.id);
          } else {
            // 其他错误
            message.error(result.message);
          }
        }
        
        deletingIds.value.delete(notification.id);
        loading.value = false;
      }
    });
  } catch (error) {
    console.error('删除通知过程出错:', error);
    message.error('操作失败，请重试');
  }
};

const viewNotificationDetail = (notification: PageNotification) => {
  selectedNotification.value = notification;
  showDetailModal.value = true;

  // 如果未读，则自动标记为已读
  if (!notification.is_read) {
    markNotificationRead(notification.id);
  }
};
</script>

<style scoped>
.search-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #606266;
}
</style>
