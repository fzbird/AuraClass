<template>
  <n-modal
    v-model:show="showModal"
    title="通知详情"
    preset="card"
    :style="{ width: '600px' }"
    class="custom-modal notification-detail-modal"
    :segmented="{ content: true, footer: 'soft' }"
    :title-style="titleStyle"
    :bordered="false"
  >
    <div v-if="notification">
      <h2 class="text-xl font-bold mb-4">{{ notification.title }}</h2>
      
      <div class="flex items-center text-sm text-gray-500 mb-6">
        <span>{{ formatDate(notification.created_at) }}</span>
        <n-divider vertical />
        <span>发送人：{{ notification.sender_name || '系统' }}</span>
        <n-divider vertical />
        <span>状态：{{ notification.is_read ? '已读' : '未读' }}</span>
      </div>
      
      <div class="bg-gray-50 p-4 rounded-lg mb-4 whitespace-pre-wrap">
        {{ notification.content }}
      </div>
      
      <div v-if="notification.meta" class="text-sm text-gray-500">
        <p v-if="notification.meta.recipient_count">
          接收人数：{{ notification.meta.recipient_count }}
        </p>
        <p v-if="notification.meta.read_count">
          已读人数：{{ notification.meta.read_count }}
        </p>
      </div>
    </div>
    
    <template #footer>
      <div class="flex justify-end">
        <n-button @click="showModal = false">关闭</n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { NModal, NButton, NDivider } from 'naive-ui';
import dayjs from 'dayjs';

interface NotificationMeta {
  recipient_count?: number;
  read_count?: number;
}

interface Notification {
  id: number;
  title: string;
  content: string;
  is_read: boolean;
  created_at: string;
  sender_name?: string;
  meta?: NotificationMeta;
}

const props = defineProps<{
  show: boolean;
  notification: Notification | null;
}>();

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void;
}>();

// 直接提供样式对象给模态框标题
const titleStyle = {
  backgroundColor: '#f0f7ff',
  color: '#0052cc',
  fontWeight: 'bold',
  padding: '16px 20px',
  borderBottom: '1px solid #e6f0fd',
  borderLeft: '4px solid #2080f0',
  fontSize: '16px'
};

const showModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
});

const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  
  const date = dayjs(dateString);
  return date.format('YYYY-MM-DD HH:mm:ss');
};
</script>

<style>
/* 全局样式，不使用scoped */
.notification-detail-modal .n-card-header {
  position: relative;
  margin-bottom: 16px;
}

.notification-detail-modal .n-card__content {
  padding: 0 20px 20px;
}

.notification-detail-modal .n-card__footer {
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  margin-top: 16px;
}

/* 调整关闭按钮样式 */
.notification-detail-modal .n-modal__close {
  top: 14px;
  right: 14px;
  transition: all 0.2s;
}

.notification-detail-modal .n-modal__close:hover {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 50%;
}
</style>
