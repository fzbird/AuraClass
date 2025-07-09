<template>
  <div :class="['app-data-list', className]" :style="style">
    <!-- 列表头部 -->
    <div v-if="$slots.header || title" class="app-data-list-header">
      <div v-if="title" class="app-data-list-title">{{ title }}</div>
      <slot name="header"></slot>
    </div>

    <!-- 数据列表 -->
    <div class="app-data-list-content">
      <div v-if="loading" class="app-data-list-loading">
        <n-spin size="medium" />
        <span v-if="loadingText" class="app-data-list-loading-text">{{ loadingText }}</span>
      </div>
      <template v-else-if="!data || data.length === 0">
        <div class="app-data-list-empty">
          <slot name="empty">
            <n-empty :description="emptyText" />
          </slot>
        </div>
      </template>
      <template v-else>
        <div class="app-data-list-items">
          <template v-for="(item, index) in data" :key="getItemKey(item, index)">
            <div
              :class="[
                'app-data-list-item',
                { 'app-data-list-item-bordered': bordered && index !== data.length - 1 },
                { 'app-data-list-item-hoverable': hoverable },
                getItemClass ? getItemClass(item, index) : ''
              ]"
              @click="handleItemClick(item, index)"
            >
              <slot name="item" :item="item" :index="index">
                {{ item[labelField] || item.label || item.name || item.title || JSON.stringify(item) }}
              </slot>
            </div>
          </template>
        </div>
      </template>
    </div>

    <!-- 列表底部 -->
    <div v-if="$slots.footer || showPagination" class="app-data-list-footer">
      <slot name="footer"></slot>
      <n-pagination
        v-if="showPagination"
        v-model:page="currentPage"
        v-model:page-size="currentPageSize"
        :item-count="total"
        :page-sizes="pageSizes"
        :show-size-picker="showSizePicker"
        :disabled="paginationDisabled"
        :page-slot="pageSlot"
        :on-update:page="handlePageChange"
        :on-update:page-size="handlePageSizeChange"
        :simple="simple"
        class="app-data-list-pagination"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { NSpin, NEmpty, NPagination } from 'naive-ui';
import type { PropType, CSSProperties } from 'vue';

interface PaginationInfo {
  page: number;
  pageSize: number;
  total: number;
}

const props = defineProps({
  // 数据列表
  data: {
    type: Array as PropType<any[]>,
    default: () => []
  },
  // 列表标题
  title: {
    type: String,
    default: ''
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
  // 是否处于加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 加载状态文本
  loadingText: {
    type: String,
    default: '加载中...'
  },
  // 空状态文本
  emptyText: {
    type: String,
    default: '暂无数据'
  },
  // 用于显示的字段名
  labelField: {
    type: String,
    default: 'label'
  },
  // 用于唯一标识的字段名
  keyField: {
    type: String,
    default: 'id'
  },
  // 是否显示分页
  showPagination: {
    type: Boolean,
    default: false
  },
  // 分页大小选项
  pageSizes: {
    type: Array as PropType<number[]>,
    default: () => [10, 20, 30, 40, 50]
  },
  // 是否显示分页大小选择器
  showSizePicker: {
    type: Boolean,
    default: true
  },
  // 分页是否禁用
  paginationDisabled: {
    type: Boolean,
    default: false
  },
  // 当前页码
  page: {
    type: Number,
    default: 1
  },
  // 每页显示条数
  pageSize: {
    type: Number,
    default: 10
  },
  // 数据总数
  total: {
    type: Number,
    default: 0
  },
  // 是否使用简单分页
  simple: {
    type: Boolean,
    default: false
  },
  // 分页页码按钮数量
  pageSlot: {
    type: Number,
    default: 7
  },
  // 获取列表项类名的函数
  getItemClass: {
    type: Function as PropType<(item: any, index: number) => string>,
    default: null
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

const emit = defineEmits([
  'update:page',
  'update:pageSize',
  'pageChange',
  'pageSizeChange',
  'itemClick'
]);

// 当前页码
const currentPage = ref(props.page);
// 当前每页条数
const currentPageSize = ref(props.pageSize);

// 监听页码变化
watch(() => props.page, (newVal) => {
  currentPage.value = newVal;
});

// 监听每页条数变化
watch(() => props.pageSize, (newVal) => {
  currentPageSize.value = newVal;
});

// 获取列表项的唯一标识
const getItemKey = (item: any, index: number): string | number => {
  if (item[props.keyField] !== undefined) {
    return item[props.keyField];
  }
  return index;
};

// 处理列表项点击
const handleItemClick = (item: any, index: number) => {
  emit('itemClick', { item, index });
};

// 处理页码变化
const handlePageChange = (page: number) => {
  currentPage.value = page;
  emit('update:page', page);
  emit('pageChange', { page, pageSize: currentPageSize.value });
};

// 处理每页条数变化
const handlePageSizeChange = (pageSize: number) => {
  currentPageSize.value = pageSize;
  emit('update:pageSize', pageSize);
  emit('pageSizeChange', { page: currentPage.value, pageSize });
};
</script>

<style scoped>
.app-data-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 3px;
  background-color: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.app-data-list-header {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f0f0f0;
}

.app-data-list-title {
  font-size: 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.app-data-list-content {
  flex: 1;
  padding: 0;
  position: relative;
}

.app-data-list-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 0;
  color: rgba(0, 0, 0, 0.45);
}

.app-data-list-loading-text {
  margin-top: 8px;
}

.app-data-list-empty {
  padding: 32px 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-data-list-items {
  width: 100%;
}

.app-data-list-item {
  padding: 12px 16px;
  transition: background-color 0.2s;
}

.app-data-list-item-bordered {
  border-bottom: 1px solid #f0f0f0;
}

.app-data-list-item-hoverable:hover {
  background-color: rgba(0, 0, 0, 0.02);
  cursor: pointer;
}

.app-data-list-footer {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid #f0f0f0;
}

.app-data-list-pagination {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}
</style> 