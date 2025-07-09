<template>
  <n-card
    :bordered="bordered"
    :hoverable="hoverable"
    :size="size"
    class="teacher-card"
    :class="[
      `teacher-card--${size || 'medium'}`,
      { 'teacher-card--hoverable': hoverable }
    ]"
  >
    <!-- 教师信息头部 -->
    <template v-if="showHeader" #header>
      <div class="teacher-card__header">
        <div class="teacher-card__avatar">
          <n-avatar
            v-if="teacher.avatar"
            :src="teacher.avatar"
            :size="avatarSize"
            round
          />
          <n-avatar
            v-else
            :size="avatarSize"
            round
            :color="generateAvatarColor(teacher.id || 0)"
          >
            {{ generateAvatarText(teacher.name) }}
          </n-avatar>
        </div>
        <div class="teacher-card__info">
          <div class="teacher-card__title">
            {{ teacher.name }}
            <n-badge v-if="teacher.role" size="small" :type="getRoleType(teacher.role)" processing class="teacher-card__role">
              {{ teacher.role }}
            </n-badge>
          </div>
          <div class="teacher-card__meta">
            <span v-if="teacher.teacherId">工号: {{ teacher.teacherId }}</span>
            <n-divider v-if="teacher.teacherId && teacher.subject" vertical />
            <span v-if="teacher.subject">{{ teacher.subject }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- 教师联系信息 -->
    <div v-if="showContact" class="teacher-card__contact">
      <div v-if="teacher.email" class="teacher-card__contact-item">
        <n-icon size="18" class="teacher-card__contact-icon">
          <mail-icon />
        </n-icon>
        <span class="teacher-card__contact-text">{{ teacher.email }}</span>
      </div>
      <div v-if="teacher.phone" class="teacher-card__contact-item">
        <n-icon size="18" class="teacher-card__contact-icon">
          <call-icon />
        </n-icon>
        <span class="teacher-card__contact-text">{{ teacher.phone }}</span>
      </div>
    </div>

    <!-- 教师统计信息 -->
    <div v-if="showStats && hasStats" class="teacher-card__stats">
      <div v-if="typeof teacher.stats?.classCount !== 'undefined'" class="teacher-card__stat-item">
        <div class="teacher-card__stat-value">
          {{ teacher.stats.classCount }}
        </div>
        <div class="teacher-card__stat-label">班级数</div>
      </div>
      <n-divider v-if="typeof teacher.stats?.classCount !== 'undefined' && typeof teacher.stats?.studentCount !== 'undefined'" vertical />
      <div v-if="typeof teacher.stats?.studentCount !== 'undefined'" class="teacher-card__stat-item">
        <div class="teacher-card__stat-value">
          {{ teacher.stats.studentCount }}
        </div>
        <div class="teacher-card__stat-label">学生数</div>
      </div>
      <n-divider v-if="typeof teacher.stats?.studentCount !== 'undefined' && typeof teacher.stats?.recordCount !== 'undefined'" vertical />
      <div v-if="typeof teacher.stats?.recordCount !== 'undefined'" class="teacher-card__stat-item">
        <div class="teacher-card__stat-value">
          {{ teacher.stats.recordCount }}
        </div>
        <div class="teacher-card__stat-label">记录数</div>
      </div>
    </div>

    <!-- 教师标签 -->
    <div v-if="showTags && teacher.tags?.length" class="teacher-card__tags">
      <n-tag 
        v-for="tag in teacher.tags" 
        :key="tag.id || tag.name" 
        :type="tag.type || 'default'"
        size="small"
        class="teacher-card__tag"
      >
        {{ tag.name }}
      </n-tag>
    </div>

    <!-- 默认插槽内容 -->
    <slot></slot>

    <!-- 班主任班级列表 -->
    <div v-if="showClasses && teacher.classes?.length" class="teacher-card__classes">
      <div class="teacher-card__classes-title">担任班主任</div>
      <div class="teacher-card__classes-list">
        <n-tag 
          v-for="classItem in teacher.classes" 
          :key="classItem.id || classItem.name" 
          type="info"
          size="small"
          class="teacher-card__class-tag"
          @click="emitClassAction('view', classItem)"
        >
          {{ classItem.name }}
        </n-tag>
      </div>
    </div>

    <!-- 教师操作按钮 -->
    <div v-if="showActions && hasActions" class="teacher-card__actions">
      <n-button 
        v-if="actions?.view" 
        quaternary 
        size="small"
        @click="emitAction('view')"
      >
        <template #icon>
          <n-icon><eye-icon /></n-icon>
        </template>
        查看
      </n-button>
      <n-button 
        v-if="actions?.edit" 
        quaternary 
        size="small"
        @click="emitAction('edit')"
      >
        <template #icon>
          <n-icon><pencil-icon /></n-icon>
        </template>
        编辑
      </n-button>
      <n-button 
        v-if="actions?.classes" 
        quaternary 
        size="small"
        @click="emitAction('classes')"
      >
        <template #icon>
          <n-icon><school-icon /></n-icon>
        </template>
        班级
      </n-button>
      <n-button 
        v-if="actions?.message" 
        quaternary 
        size="small"
        @click="emitAction('message')"
      >
        <template #icon>
          <n-icon><chatbox-icon /></n-icon>
        </template>
        留言
      </n-button>
      <n-button 
        v-if="actions?.delete" 
        quaternary 
        size="small"
        @click="emitAction('delete')"
      >
        <template #icon>
          <n-icon><trash-icon /></n-icon>
        </template>
        删除
      </n-button>
      <slot name="actions"></slot>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { 
  NCard, 
  NAvatar, 
  NBadge, 
  NDivider, 
  NTag, 
  NButton,
  NIcon
} from 'naive-ui';
import EyeIcon from '@vicons/ionicons5/es/EyeOutline';
import PencilIcon from '@vicons/ionicons5/es/PencilOutline';
import TrashIcon from '@vicons/ionicons5/es/TrashOutline';
import MailIcon from '@vicons/ionicons5/es/MailOutline';
import CallIcon from '@vicons/ionicons5/es/CallOutline';
import SchoolIcon from '@vicons/ionicons5/es/SchoolOutline';
import ChatboxIcon from '@vicons/ionicons5/es/ChatboxOutline';

interface TeacherTag {
  id?: number | string;
  name: string;
  type?: 'default' | 'primary' | 'info' | 'success' | 'warning' | 'error';
}

interface TeacherStats {
  classCount?: number;
  studentCount?: number;
  recordCount?: number;
}

interface TeacherClass {
  id?: number | string;
  name: string;
}

interface TeacherInfo {
  id?: number | string;
  name: string;
  teacherId?: string;
  subject?: string;
  role?: string;
  email?: string;
  phone?: string;
  avatar?: string;
  stats?: TeacherStats;
  tags?: TeacherTag[];
  classes?: TeacherClass[];
}

interface ActionsConfig {
  view?: boolean;
  edit?: boolean;
  classes?: boolean;
  message?: boolean;
  delete?: boolean;
}

const props = defineProps<{
  teacher: TeacherInfo;
  showHeader?: boolean;
  showContact?: boolean;
  showStats?: boolean;
  showTags?: boolean;
  showClasses?: boolean;
  showActions?: boolean;
  actions?: ActionsConfig;
  bordered?: boolean;
  hoverable?: boolean;
  size?: 'small' | 'medium' | 'large';
}>();

const emit = defineEmits<{
  (e: 'action', payload: { action: string; teacher: TeacherInfo }): void;
  (e: 'class-action', payload: { action: string; classItem: TeacherClass; teacher: TeacherInfo }): void;
}>();

const defaultProps = {
  showHeader: true,
  showContact: true,
  showStats: true,
  showTags: true,
  showClasses: true,
  showActions: true,
  actions: {
    view: true,
    edit: false,
    classes: false,
    message: false,
    delete: false
  },
  bordered: true,
  hoverable: true,
  size: 'medium'
};

// 计算是否有任何操作按钮
const hasActions = computed(() => {
  const actionsConfig = props.actions || defaultProps.actions;
  return Object.values(actionsConfig).some(val => val);
});

// 计算是否有统计信息
const hasStats = computed(() => {
  const stats = props.teacher.stats;
  if (!stats) return false;
  return typeof stats.classCount !== 'undefined' || 
         typeof stats.studentCount !== 'undefined' || 
         typeof stats.recordCount !== 'undefined';
});

// 计算头像大小
const avatarSize = computed(() => {
  switch (props.size || defaultProps.size) {
    case 'small': return 'medium';
    case 'large': return 'large';
    default: return 'medium';
  }
});

// 生成头像文本
const generateAvatarText = (name: string): string => {
  if (!name) return '';
  return name.substring(0, 1);
};

// 生成头像颜色
const generateAvatarColor = (id: number | string): string => {
  const colors = [
    '#2080f0', '#18a058', '#f0a020', '#d03050', 
    '#8a2be2', '#4169e1', '#f44336', '#ff9800'
  ];
  
  const numericId = typeof id === 'string' ? 
    id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) : 
    Number(id);
  
  return colors[numericId % colors.length];
};

// 获取角色标签类型
const getRoleType = (role: string): string => {
  const roleMap: Record<string, string> = {
    '校长': 'error',
    '副校长': 'warning',
    '主任': 'success',
    '班主任': 'info',
    '教师': 'default'
  };
  
  return roleMap[role] || 'default';
};

// 发出操作事件
const emitAction = (action: string) => {
  emit('action', { action, teacher: props.teacher });
};

// 发出班级操作事件
const emitClassAction = (action: string, classItem: TeacherClass) => {
  emit('class-action', { action, classItem, teacher: props.teacher });
};
</script>

<style scoped>
.teacher-card {
  transition: all 0.3s;
}

.teacher-card--hoverable:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.teacher-card--small {
  max-width: 280px;
}

.teacher-card--medium {
  max-width: 320px;
}

.teacher-card--large {
  max-width: 380px;
}

.teacher-card__header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.teacher-card__info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.teacher-card__title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.teacher-card__role {
  font-size: 12px;
}

.teacher-card__meta {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
}

.teacher-card__contact {
  margin-top: 12px;
}

.teacher-card__contact-item {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
  font-size: 13px;
  color: rgba(0, 0, 0, 0.7);
}

.teacher-card__contact-icon {
  margin-right: 8px;
  color: rgba(0, 0, 0, 0.5);
}

.teacher-card__stats {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin: 16px 0;
  padding: 8px 0;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}

.teacher-card__stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.teacher-card__stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #2080f0;
}

.teacher-card__stat-label {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.6);
  margin-top: 4px;
}

.teacher-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.teacher-card__tag {
  margin-right: 0 !important;
}

.teacher-card__classes {
  margin-top: 16px;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
  padding: 8px;
}

.teacher-card__classes-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  color: rgba(0, 0, 0, 0.7);
}

.teacher-card__classes-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.teacher-card__class-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.teacher-card__class-tag:hover {
  opacity: 0.8;
}

.teacher-card__actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  gap: 8px;
}
</style> 