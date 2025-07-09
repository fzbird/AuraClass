<template>
  <n-card
    :bordered="bordered"
    :hoverable="hoverable"
    :size="size"
    class="class-card"
    :class="[
      `class-card--${size || 'medium'}`,
      { 'class-card--hoverable': hoverable }
    ]"
  >
    <!-- 班级信息头部 -->
    <template v-if="showHeader" #header>
      <div class="class-card__header">
        <div class="class-card__avatar">
          <n-avatar
            v-if="classInfo.avatar"
            :src="classInfo.avatar"
            :size="avatarSize"
            round
          />
          <n-avatar
            v-else
            :size="avatarSize"
            round
            :color="generateAvatarColor(classInfo.id || 0)"
          >
            {{ generateAvatarText(classInfo.name) }}
          </n-avatar>
        </div>
        <div class="class-card__info">
          <div class="class-card__name">
            {{ classInfo.name }}
            <n-badge v-if="classInfo.isActive" dot color="#18a058" class="class-card__status" />
          </div>
          <div class="class-card__meta">
            <span v-if="classInfo.gradeLevel">{{ classInfo.gradeLevel }}级</span>
            <n-divider v-if="classInfo.gradeLevel && classInfo.teacherName" vertical />
            <span v-if="classInfo.teacherName">班主任: {{ classInfo.teacherName }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- 班级统计信息 -->
    <div v-if="showStats" class="class-card__stats">
      <div class="class-card__stat-item">
        <div class="class-card__stat-value">
          {{ classInfo.stats?.studentCount || 0 }}
        </div>
        <div class="class-card__stat-label">学生数</div>
      </div>
      <n-divider vertical />
      <div class="class-card__stat-item">
        <div class="class-card__stat-value">
          {{ formatScore(classInfo.stats?.averageScore) }}
        </div>
        <div class="class-card__stat-label">平均分</div>
      </div>
      <n-divider vertical />
      <div class="class-card__stat-item">
        <div class="class-card__stat-value">
          {{ classInfo.stats?.recordCount || 0 }}
        </div>
        <div class="class-card__stat-label">记录数</div>
      </div>
    </div>

    <!-- 班级标签 -->
    <div v-if="showTags && classInfo.tags?.length" class="class-card__tags">
      <n-tag 
        v-for="tag in classInfo.tags" 
        :key="tag.id || tag.name" 
        :type="tag.type || 'default'"
        size="small"
        class="class-card__tag"
      >
        {{ tag.name }}
      </n-tag>
    </div>

    <!-- 默认插槽内容 -->
    <slot></slot>

    <!-- 班级操作按钮 -->
    <div v-if="showActions && hasActions" class="class-card__actions">
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
        v-if="actions?.students" 
        quaternary 
        size="small"
        @click="emitAction('students')"
      >
        <template #icon>
          <n-icon><people-icon /></n-icon>
        </template>
        学生
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
import PeopleIcon from '@vicons/ionicons5/es/PeopleOutline';
import TrashIcon from '@vicons/ionicons5/es/TrashOutline';

interface ClassTag {
  id?: number | string;
  name: string;
  type?: 'default' | 'primary' | 'info' | 'success' | 'warning' | 'error';
}

interface ClassStats {
  studentCount?: number;
  averageScore?: number;
  recordCount?: number;
}

interface ClassInfo {
  id?: number | string;
  name: string;
  gradeLevel?: string;
  teacherName?: string;
  teacherId?: number | string;
  avatar?: string;
  isActive?: boolean;
  stats?: ClassStats;
  tags?: ClassTag[];
}

interface ActionsConfig {
  view?: boolean;
  edit?: boolean;
  students?: boolean;
  delete?: boolean;
}

const props = defineProps<{
  classInfo: ClassInfo;
  showHeader?: boolean;
  showStats?: boolean;
  showTags?: boolean;
  showActions?: boolean;
  actions?: ActionsConfig;
  bordered?: boolean;
  hoverable?: boolean;
  size?: 'small' | 'medium' | 'large';
}>();

const emit = defineEmits<{
  (e: 'action', payload: { action: string; classInfo: ClassInfo }): void;
}>();

const defaultProps = {
  showHeader: true,
  showStats: true,
  showTags: true,
  showActions: true,
  actions: {
    view: true,
    edit: false,
    students: false,
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

// 计算头像大小
const avatarSize = computed(() => {
  switch (props.size || defaultProps.size) {
    case 'small': return 'medium';
    case 'large': return 'large';
    default: return 'medium';
  }
});

// 生成头像文本
const generateAvatarText = (className: string): string => {
  if (!className) return '';
  return className.substring(0, 2);
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

// 格式化分数显示
const formatScore = (score?: number): string => {
  if (score === undefined || score === null) return '-';
  return score.toFixed(1);
};

// 发出操作事件
const emitAction = (action: string) => {
  emit('action', { action, classInfo: props.classInfo });
};
</script>

<style scoped>
.class-card {
  transition: all 0.3s;
}

.class-card--hoverable:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.class-card--small {
  max-width: 280px;
}

.class-card--medium {
  max-width: 320px;
}

.class-card--large {
  max-width: 380px;
}

.class-card__header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.class-card__info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.class-card__name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.class-card__meta {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
}

.class-card__stats {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin: 16px 0;
  padding: 8px 0;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}

.class-card__stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.class-card__stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #2080f0;
}

.class-card__stat-label {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.6);
  margin-top: 4px;
}

.class-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.class-card__tag {
  margin-right: 0 !important;
}

.class-card__actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  gap: 8px;
}
</style> 