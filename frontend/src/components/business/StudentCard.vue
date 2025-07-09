<template>
  <app-card
    :class="['student-card', className]"
    :style="style"
    :bordered="bordered"
    :hoverable="hoverable"
    :size="size"
  >
    <template #header v-if="showHeader">
      <div class="student-card-header">
        <app-avatar
          :src="student.avatar"
          :text="getAvatarText(student.name)"
          :color="getAvatarColor(student.id)"
          size="medium"
          round
          class="student-card-avatar"
        />
        <div class="student-card-info">
          <div class="student-card-name">
            {{ student.name }}
            <app-badge v-if="student.role" :value="student.role" type="info" class="student-card-role" />
          </div>
          <div class="student-card-meta">
            <span class="student-card-id">{{ student.studentId }}</span>
            <span class="student-card-class">{{ student.className }}</span>
          </div>
        </div>
      </div>
    </template>

    <div class="student-card-content">
      <div v-if="showScore" class="student-card-score">
        <div class="student-card-score-value">{{ student.score || 0 }}</div>
        <div class="student-card-score-label">量化分</div>
      </div>
      
      <div v-if="showStats" class="student-card-stats">
        <div class="student-card-stat-item">
          <div class="stat-value">{{ student.stats?.positive || 0 }}</div>
          <div class="stat-label">加分</div>
        </div>
        <div class="student-card-stat-item">
          <div class="stat-value">{{ student.stats?.negative || 0 }}</div>
          <div class="stat-label">减分</div>
        </div>
        <div class="student-card-stat-item">
          <div class="stat-value">{{ student.stats?.records || 0 }}</div>
          <div class="stat-label">记录数</div>
        </div>
      </div>

      <div v-if="showTags && student.tags && student.tags.length > 0" class="student-card-tags">
        <app-badge 
          v-for="tag in student.tags" 
          :key="tag.id"
          :value="tag.name"
          :color="tag.color"
          :type="tag.type"
          class="student-card-tag"
        />
      </div>

      <div v-if="$slots.default" class="student-card-custom">
        <slot></slot>
      </div>
    </div>

    <template #footer v-if="$slots.footer || showActions">
      <div class="student-card-footer">
        <slot name="footer">
          <div v-if="showActions" class="student-card-actions">
            <app-button 
              v-if="actions.view" 
              size="small" 
              @click="handleAction('view', student)"
            >
              查看
            </app-button>
            <app-button 
              v-if="actions.edit" 
              size="small" 
              type="info" 
              @click="handleAction('edit', student)"
            >
              编辑
            </app-button>
            <app-button 
              v-if="actions.records" 
              size="small" 
              type="success" 
              @click="handleAction('records', student)"
            >
              量化记录
            </app-button>
            <app-button 
              v-if="actions.delete" 
              size="small" 
              type="error" 
              @click="handleAction('delete', student)"
            >
              删除
            </app-button>
          </div>
        </slot>
      </div>
    </template>
  </app-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { AppCard, AppAvatar, AppBadge, AppButton } from '../common';
import type { PropType, CSSProperties } from 'vue';

// 学生信息类型
interface StudentStats {
  positive: number;  // 加分
  negative: number;  // 减分
  records: number;   // 记录数
}

interface StudentTag {
  id: string | number;
  name: string;
  color?: string;
  type?: 'default' | 'success' | 'info' | 'warning' | 'error';
}

interface Student {
  id: number;
  name: string;
  studentId: string;
  className: string;
  role?: string;
  avatar?: string;
  score?: number;
  total_score?: number; // 添加总分字段
  rank?: number; // 添加排名字段
  is_active?: boolean; // 添加是否激活字段
  stats?: StudentStats;
  tags?: StudentTag[];
  birth_date?: string; // 添加出生日期字段
  contact_info?: string; // 添加联系信息字段
  [key: string]: any;
}

const props = defineProps({
  // 学生信息
  student: {
    type: Object as PropType<Student>,
    required: true
  },
  // 是否显示头部
  showHeader: {
    type: Boolean,
    default: true
  },
  // 是否显示分数
  showScore: {
    type: Boolean,
    default: true
  },
  // 是否显示统计信息
  showStats: {
    type: Boolean,
    default: true
  },
  // 是否显示标签
  showTags: {
    type: Boolean,
    default: true
  },
  // 是否显示操作按钮
  showActions: {
    type: Boolean,
    default: true
  },
  // 显示哪些操作按钮
  actions: {
    type: Object as PropType<{
      view?: boolean;
      edit?: boolean;
      records?: boolean;
      delete?: boolean;
    }>,
    default: () => ({
      view: true,
      edit: false,
      records: false,
      delete: false
    })
  },
  // 是否显示边框
  bordered: {
    type: Boolean,
    default: true
  },
  // 是否可悬停
  hoverable: {
    type: Boolean,
    default: true
  },
  // 卡片大小
  size: {
    type: String as PropType<'small' | 'medium' | 'large'>,
    default: 'medium'
  },
  // 自定义样式
  style: {
    type: [String, Object] as PropType<string | CSSProperties>,
    default: null
  },
  // 自定义类名
  className: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['action']);

// 获取头像文本
const getAvatarText = (name: string): string => {
  return name ? name.substring(0, 1) : '?';
};

// 根据ID生成随机头像颜色
const getAvatarColor = (id: number): string => {
  const colors = [
    '#1890ff', '#52c41a', '#faad14', '#f5222d', 
    '#722ed1', '#13c2c2', '#eb2f96', '#fadb14'
  ];
  // 保证同一个ID总是生成相同的颜色
  return colors[id % colors.length];
};

// 处理操作按钮点击
const handleAction = (action: string, student: Student) => {
  emit('action', { action, student });
};
</script>

<style scoped>
.student-card {
  transition: all 0.3s;
}

.student-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.student-card-avatar {
  margin-right: 12px;
  flex-shrink: 0;
}

.student-card-info {
  flex: 1;
  min-width: 0;
}

.student-card-name {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.student-card-role {
  margin-left: 8px;
}

.student-card-meta {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
}

.student-card-id {
  margin-right: 8px;
}

.student-card-class {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.student-card-content {
  padding: 4px 0;
}

.student-card-score {
  text-align: center;
  padding: 8px 0;
  margin-bottom: 12px;
}

.student-card-score-value {
  font-size: 24px;
  font-weight: 500;
  color: #1890ff;
}

.student-card-score-label {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
}

.student-card-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.student-card-stat-item {
  text-align: center;
  padding: 0 8px;
}

.stat-value {
  font-size: 18px;
  font-weight: 500;
}

.stat-label {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.student-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.student-card-tag {
  margin-right: 4px;
}

.student-card-custom {
  margin-top: 12px;
}

.student-card-footer {
  margin-top: 8px;
}

.student-card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style> 