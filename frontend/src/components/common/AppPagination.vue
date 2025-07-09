<template>
  <div :class="[className, paginationClass]" :style="style">
    <n-pagination
      :page="page"
      :page-size="pageSize"
      :item-count="itemCount"
      :page-count="pageCount"
      :page-slot="pageSlot"
      :show-size-picker="showSizePicker"
      :page-sizes="pageSizes"
      :show-quick-jumper="showQuickJumper"
      :size="size"
      :simple="simple"
      :disabled="disabled"
      :prev-text="prevText"
      :next-text="nextText"
      @update:page="handlePageChange"
      @update:page-size="handlePageSizeChange"
    />
  </div>
</template>

<script setup lang="ts">
import { NPagination } from 'naive-ui';
import type { CSSProperties } from 'vue';

const props = defineProps({
  // 当前页码
  page: {
    type: Number,
    default: 1
  },
  // 每页条数
  pageSize: {
    type: Number,
    default: 10
  },
  // 总条目数，与pageCount二选一
  itemCount: {
    type: Number,
    default: 0
  },
  // 总页数，与itemCount二选一
  pageCount: {
    type: Number,
    default: 0
  },
  // 分页插槽
  pageSlot: {
    type: Number,
    default: 9
  },
  // 是否显示分页尺寸切换器
  showSizePicker: {
    type: Boolean,
    default: false
  },
  // 每页条数选项
  pageSizes: {
    type: Array,
    default: () => [10, 20, 30, 40, 50]
  },
  // 是否显示快速跳转
  showQuickJumper: {
    type: Boolean,
    default: false
  },
  // 分页器大小
  size: {
    type: String,
    default: 'medium',
    validator: (val: string) => ['small', 'medium', 'large'].includes(val)
  },
  // 是否使用简洁模式
  simple: {
    type: Boolean,
    default: false
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 上一页文本
  prevText: {
    type: String,
    default: ''
  },
  // 下一页文本
  nextText: {
    type: String,
    default: ''
  },
  // 自定义分页器类名
  paginationClass: {
    type: String,
    default: ''
  },
  // 自定义样式
  style: {
    type: [String, Object] as unknown as () => string | CSSProperties,
    default: () => ({})
  },
  // 组件容器类名
  className: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:page', 'update:pageSize']);

// 处理页码变化
const handlePageChange = (page: number) => {
  emit('update:page', page);
};

// 处理每页条数变化
const handlePageSizeChange = (pageSize: number) => {
  emit('update:pageSize', pageSize);
  // 每页条数变化时，通常将页码重置为1
  emit('update:page', 1);
};
</script>

<style scoped>
/* 可根据需要添加样式 */
</style> 