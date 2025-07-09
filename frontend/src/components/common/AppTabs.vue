<template>
  <div :class="[className, 'app-tabs-wrapper']" :style="style">
    <n-tabs
      :value="modelValue"
      :type="type"
      :size="size"
      :tab-style="tabStyle"
      :bar-width="barWidth"
      :closable="closable"
      :justified="justified"
      :animated="animated"
      :pane-style="paneStyle"
      :pane-class="paneClass"
      :tab-class="tabClass"
      :addable="addable"
      :tab-gap="tabGap"
      :on-close="onClose"
      :on-add="onAdd"
      @update:value="handleValueChange"
      @close="handleClose"
      @add="handleAdd"
    >
      <template v-if="tabs && tabs.length">
        <n-tab-pane
          v-for="tab in tabs"
          :key="tab.name"
          :name="tab.name"
          :tab="tab.tab"
          :display-directive="tab.displayDirective"
          :closable="tab.closable ?? closable"
          :disabled="tab.disabled"
          :tab-props="tab.tabProps"
        >
          <slot :name="tab.name" />
        </n-tab-pane>
      </template>
      <slot v-else />
      <template #prefix v-if="$slots.prefix">
        <slot name="prefix" />
      </template>
      <template #suffix v-if="$slots.suffix">
        <slot name="suffix" />
      </template>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { NTabs, NTabPane } from 'naive-ui';
import type { PropType, CSSProperties } from 'vue';

interface TabItem {
  name: string | number;
  tab: string;
  displayDirective?: 'if' | 'show';
  closable?: boolean;
  disabled?: boolean;
  tabProps?: Record<string, any>;
}

type TabsType = 'bar' | 'line' | 'card' | 'segment';
type TabsSize = 'small' | 'medium' | 'large';

const props = defineProps({
  // v-model绑定值
  modelValue: {
    type: [String, Number],
    required: true
  },
  // 标签页风格
  type: {
    type: String as () => TabsType,
    default: 'bar'
  },
  // 标签页大小
  size: {
    type: String as () => TabsSize,
    default: 'medium'
  },
  // 标签样式
  tabStyle: {
    type: [String, Object] as unknown as PropType<string | CSSProperties>,
    default: undefined
  },
  // 滑块宽度
  barWidth: {
    type: Number,
    default: undefined
  },
  // 是否可关闭
  closable: {
    type: Boolean,
    default: false
  },
  // 是否均分宽度
  justified: {
    type: Boolean,
    default: false
  },
  // 是否开启动画
  animated: {
    type: Boolean,
    default: true
  },
  // 面板样式
  paneStyle: {
    type: [String, Object] as unknown as PropType<string | CSSProperties>,
    default: undefined
  },
  // 面板类名
  paneClass: {
    type: String,
    default: undefined
  },
  // 标签类名
  tabClass: {
    type: String,
    default: undefined
  },
  // 是否可添加
  addable: {
    type: Boolean,
    default: false
  },
  // 标签间隔
  tabGap: {
    type: Number,
    default: undefined
  },
  // 标签页配置
  tabs: {
    type: Array as PropType<TabItem[]>,
    default: () => []
  },
  // 关闭处理函数
  onClose: {
    type: Function as PropType<(name: string | number) => boolean | Promise<boolean>>,
    default: undefined
  },
  // 添加处理函数
  onAdd: {
    type: Function as PropType<() => void>,
    default: undefined
  },
  // 容器样式
  style: {
    type: [String, Object] as unknown as PropType<string | CSSProperties>,
    default: () => ({})
  },
  // 容器类名
  className: {
    type: String,
    default: ''
  }
});

const emit = defineEmits([
  'update:modelValue',
  'close',
  'add',
  'change'
]);

// 处理值变更
const handleValueChange = (value: string | number) => {
  emit('update:modelValue', value);
  emit('change', value);
};

// 处理关闭
const handleClose = (name: string | number) => {
  emit('close', name);
};

// 处理添加
const handleAdd = () => {
  emit('add');
};
</script>

<style scoped>
.app-tabs-wrapper {
  width: 100%;
}
</style> 