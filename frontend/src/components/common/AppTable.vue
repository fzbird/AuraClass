<template>
  <div :class="[className, 'app-table-wrapper']">
    <n-data-table
      :columns="columns"
      :data="data"
      :pagination="paginationConfig"
      :bordered="bordered"
      :bottom-bordered="bottomBordered"
      :striped="striped"
      :size="size"
      :loading="loading"
      :row-key="rowKey"
      :row-class-name="rowClassName"
      :scroll-x="scrollX"
      :virtual-scroll="virtualScroll"
      :max-height="maxHeight"
      :min-height="minHeight"
      :flex-height="flexHeight"
      :summary="summary"
      :remote="remote"
      :paginate-single-page="paginateSinglePage"
      :render-cell="renderCell"
      :style="style"
      :class="tableClass"
      @update:sorter="handleSorterChange"
      @update:filters="handleFiltersChange"
      @update:page="handlePageChange"
      @update:page-size="handlePageSizeChange"
      @update:checked-row-keys="handleCheckedRowKeysChange"
    />
    <slot name="pagination" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { NDataTable } from 'naive-ui';
import type { CSSProperties, PropType } from 'vue';

type TableSize = 'small' | 'medium' | 'large';
type TableColumn = {
  title: string;
  key: string;
  width?: number;
  minWidth?: number;
  ellipsis?: boolean;
  fixed?: 'left' | 'right';
  sortable?: boolean;
  sortOrder?: 'ascend' | 'descend' | false;
  sorter?: (a: any, b: any) => number;
  filter?: boolean | any[];
  filterMultiple?: boolean;
  filterOptions?: Array<{ label: string; value: string | number }>;
  filterOptionValue?: string | number | Array<string | number>;
  align?: 'left' | 'center' | 'right';
  [key: string]: any;
};

const props = defineProps({
  // 表格列配置
  columns: {
    type: Array as PropType<TableColumn[]>,
    required: true
  },
  // 表格数据
  data: {
    type: Array as PropType<any[]>,
    default: () => []
  },
  // 是否显示边框
  bordered: {
    type: Boolean,
    default: false
  },
  // 是否显示底部边框
  bottomBordered: {
    type: Boolean,
    default: true
  },
  // 是否显示斑马纹
  striped: {
    type: Boolean,
    default: false
  },
  // 表格尺寸
  size: {
    type: String as () => TableSize,
    default: 'medium'
  },
  // 加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 行数据的 key
  rowKey: {
    type: [String, Function] as PropType<string | ((row: any) => string)>,
    default: 'id'
  },
  // 行的 class 名称
  rowClassName: {
    type: [String, Function] as PropType<string | ((row: any, index: number) => string)>,
    default: undefined
  },
  // 水平滚动宽度
  scrollX: {
    type: [Number, String],
    default: undefined
  },
  // 是否启用虚拟滚动
  virtualScroll: {
    type: Boolean,
    default: false
  },
  // 表格最大高度
  maxHeight: {
    type: [Number, String],
    default: undefined
  },
  // 表格最小高度
  minHeight: {
    type: [Number, String],
    default: undefined
  },
  // 是否使用 flex 高度
  flexHeight: {
    type: Boolean,
    default: false
  },
  // 是否显示分页
  pagination: {
    type: Boolean,
    default: false
  },
  // 分页当前页
  page: {
    type: Number,
    default: 1
  },
  // 分页每页条数
  pageSize: {
    type: Number,
    default: 10
  },
  // 数据总数
  itemCount: {
    type: Number,
    default: 0
  },
  // 分页可选的每页条数
  pageSizes: {
    type: Array as PropType<number[]>,
    default: () => [10, 20, 30, 40, 50]
  },
  // 是否显示分页切换器
  showSizePicker: {
    type: Boolean,
    default: false
  },
  // 是否显示快速跳转
  showQuickJumper: {
    type: Boolean,
    default: false
  },
  // 表格摘要
  summary: {
    type: Function as PropType<(pageData: any[]) => any[]>,
    default: undefined
  },
  // 是否使用远程数据
  remote: {
    type: Boolean,
    default: false
  },
  // 只有一页时是否显示分页
  paginateSinglePage: {
    type: Boolean,
    default: false
  },
  // 自定义单元格渲染
  renderCell: {
    type: Function as PropType<(value: any, rowData: any, rowIndex: number) => any>,
    default: undefined
  },
  // 自定义样式
  style: {
    type: [String, Object] as unknown as PropType<string | CSSProperties>,
    default: () => ({})
  },
  // 自定义类名
  className: {
    type: String,
    default: ''
  },
  // 表格类名
  tableClass: {
    type: String,
    default: ''
  }
});

const emit = defineEmits([
  'update:sorter',
  'update:filters',
  'update:page',
  'update:pageSize',
  'update:checkedRowKeys',
  'pageSizeChange',
  'pageChange'
]);

// 配置分页
const paginationConfig = computed(() => {
  if (!props.pagination) return false;
  
  return {
    page: props.page,
    pageSize: props.pageSize,
    itemCount: props.itemCount,
    pageSizes: props.pageSizes,
    showSizePicker: props.showSizePicker,
    showQuickJumper: props.showQuickJumper,
    onChange: handlePageChange,
    onUpdatePageSize: handlePageSizeChange
  };
});

// 处理排序变更
const handleSorterChange = (sorter: any) => {
  emit('update:sorter', sorter);
};

// 处理筛选变更
const handleFiltersChange = (filters: any, sourceColumn: any) => {
  emit('update:filters', filters, sourceColumn);
};

// 处理页码变更
const handlePageChange = (page: number) => {
  emit('update:page', page);
  emit('pageChange', page);
};

// 处理每页条数变更
const handlePageSizeChange = (pageSize: number) => {
  emit('update:pageSize', pageSize);
  emit('pageSizeChange', pageSize);
};

// 处理选中行变更
const handleCheckedRowKeysChange = (keys: any[]) => {
  emit('update:checkedRowKeys', keys);
};
</script>

<style scoped>
.app-table-wrapper {
  width: 100%;
  position: relative;
}
</style> 