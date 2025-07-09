<template>
  <app-card
    :class="['quant-item-card', className, `quant-item-card--${quantItem.type || 'default'}`]"
    :style="style"
    :bordered="bordered"
    :hoverable="hoverable"
    :size="size"
  >
    <template #header v-if="showHeader">
      <div class="quant-item-card-header">
        <div class="quant-item-card-score" :class="getScoreClass(quantItem.score)">
          {{ quantItem.score > 0 ? '+' : '' }}{{ quantItem.score }}
        </div>
        <div class="quant-item-card-title">
          {{ quantItem.name }}
          <app-badge 
            v-if="showType && quantItem.type" 
            :value="getTypeLabel(quantItem.type)" 
            :type="getTypeColor(quantItem.type)"
            class="quant-item-card-type"
          />
        </div>
      </div>
    </template>

    <div class="quant-item-card-content">
      <div v-if="showDescription && quantItem.description" class="quant-item-card-description">
        {{ quantItem.description }}
      </div>
      
      <div v-if="showCategory && quantItem.category" class="quant-item-card-category">
        <span class="category-label">分类：</span>
        <span class="category-value">{{ quantItem.category.name }}</span>
      </div>
      
      <div v-if="showCreator && quantItem.creator" class="quant-item-card-creator">
        <span class="creator-label">创建者：</span>
        <span class="creator-value">{{ quantItem.creator.name }}</span>
      </div>
      
      <div v-if="showDate && quantItem.createdAt" class="quant-item-card-date">
        <span class="date-label">创建时间：</span>
        <app-time-label :time="quantItem.createdAt" format="auto" />
      </div>

      <div v-if="showTags && quantItem.tags && quantItem.tags.length > 0" class="quant-item-card-tags">
        <app-badge 
          v-for="tag in quantItem.tags" 
          :key="tag.id"
          :value="tag.name"
          :color="tag.color"
          :type="tag.type"
          class="quant-item-card-tag"
        />
      </div>

      <div v-if="$slots.default" class="quant-item-card-custom">
        <slot></slot>
      </div>
    </div>

    <template #footer v-if="$slots.footer || showActions">
      <div class="quant-item-card-footer">
        <slot name="footer">
          <div v-if="showActions" class="quant-item-card-actions">
            <app-button 
              v-if="actions.view" 
              size="small" 
              @click="handleAction('view', quantItem)"
            >
              查看
            </app-button>
            <app-button 
              v-if="actions.edit" 
              size="small" 
              type="info" 
              @click="handleAction('edit', quantItem)"
            >
              编辑
            </app-button>
            <app-button 
              v-if="actions.record" 
              size="small" 
              type="primary" 
              @click="handleAction('record', quantItem)"
            >
              记录
            </app-button>
            <app-button 
              v-if="actions.delete" 
              size="small" 
              type="error" 
              @click="handleAction('delete', quantItem)"
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
import { AppCard, AppBadge, AppButton, AppTimeLabel } from '../common';
import type { PropType, CSSProperties } from 'vue';

// 量化项目标签类型
interface QuantItemTag {
  id: string | number;
  name: string;
  color?: string;
  type?: 'default' | 'success' | 'info' | 'warning' | 'error';
}

// 量化项目类型
interface QuantItemCategory {
  id: number;
  name: string;
}

// 创建者信息
interface Creator {
  id: number;
  name: string;
}

// 量化项目类型
interface QuantItem {
  id: number;
  name: string;
  score: number;
  type: 'positive' | 'negative' | 'neutral';
  description?: string;
  category?: QuantItemCategory;
  creator?: Creator;
  createdAt?: string | Date;
  tags?: QuantItemTag[];
  [key: string]: any;
}

const props = defineProps({
  // 量化项目信息
  quantItem: {
    type: Object as PropType<QuantItem>,
    required: true
  },
  // 是否显示头部
  showHeader: {
    type: Boolean,
    default: true
  },
  // 是否显示类型标签
  showType: {
    type: Boolean,
    default: true
  },
  // 是否显示描述
  showDescription: {
    type: Boolean,
    default: true
  },
  // 是否显示分类
  showCategory: {
    type: Boolean,
    default: true
  },
  // 是否显示创建者
  showCreator: {
    type: Boolean,
    default: false
  },
  // 是否显示创建日期
  showDate: {
    type: Boolean,
    default: false
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
      record?: boolean;
      delete?: boolean;
    }>,
    default: () => ({
      view: true,
      edit: false,
      record: true,
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

// 获取分数样式类
const getScoreClass = (score: number): string => {
  if (score > 0) return 'score-positive';
  if (score < 0) return 'score-negative';
  return 'score-neutral';
};

// 获取类型标签文本
const getTypeLabel = (type: string): string => {
  const typeMap: Record<string, string> = {
    positive: '加分项',
    negative: '减分项',
    neutral: '中性项'
  };
  return typeMap[type] || type;
};

// 获取类型标签颜色
const getTypeColor = (type: string): 'success' | 'error' | 'info' => {
  const typeColorMap: Record<string, 'success' | 'error' | 'info'> = {
    positive: 'success',
    negative: 'error',
    neutral: 'info'
  };
  return typeColorMap[type] || 'info';
};

// 处理操作按钮点击
const handleAction = (action: string, quantItem: QuantItem) => {
  emit('action', { action, quantItem });
};
</script>

<style scoped>
.quant-item-card {
  transition: all 0.3s;
}

.quant-item-card--positive {
  border-left: 3px solid var(--success-color, #52c41a);
}

.quant-item-card--negative {
  border-left: 3px solid var(--error-color, #f5222d);
}

.quant-item-card--neutral {
  border-left: 3px solid var(--info-color, #1890ff);
}

.quant-item-card--default {
  border-left: 3px solid var(--primary-color, #333);
}

.quant-item-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.quant-item-card-score {
  font-size: 20px;
  font-weight: bold;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  margin-right: 12px;
  flex-shrink: 0;
}

.score-positive {
  background-color: rgba(82, 196, 26, 0.1);
  color: #52c41a;
}

.score-negative {
  background-color: rgba(245, 34, 45, 0.1);
  color: #f5222d;
}

.score-neutral {
  background-color: rgba(24, 144, 255, 0.1);
  color: #1890ff;
}

.quant-item-card-title {
  font-size: 16px;
  font-weight: 500;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.quant-item-card-type {
  margin-left: 8px;
}

.quant-item-card-content {
  padding: 4px 0;
}

.quant-item-card-description {
  margin-bottom: 12px;
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
  line-height: 1.5;
}

.quant-item-card-category,
.quant-item-card-creator,
.quant-item-card-date {
  font-size: 13px;
  margin-bottom: 8px;
  color: rgba(0, 0, 0, 0.45);
}

.category-label,
.creator-label,
.date-label {
  margin-right: 4px;
}

.category-value,
.creator-value {
  color: rgba(0, 0, 0, 0.65);
}

.quant-item-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  margin-bottom: 12px;
}

.quant-item-card-tag {
  margin-right: 4px;
}

.quant-item-card-custom {
  margin-top: 12px;
}

.quant-item-card-footer {
  margin-top: 8px;
}

.quant-item-card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style> 