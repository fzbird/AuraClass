<template>
  <div :class="className">
    <n-popover
      v-model:show="showValue"
      :title="useDefaultSlot || useHeaderSlot ? undefined : title"
      :content="useDefaultSlot ? undefined : content"
      :trigger="trigger"
      :placement="placement"
      :width="width"
      :raw="raw || useDefaultSlot || useHeaderSlot"
      :show-arrow="showArrow"
      :delay="delay"
      :duration="duration"
      :disabled="disabled"
      :header-style="headerStyle"
      :to="to"
      :flip="flip"
      :keep-alive-on-hover="keepAliveOnHover"
      :dark="dark"
      @update:show="handleUpdateShow"
      @clickoutside="handleClickOutside"
    >
      <!-- 触发器插槽 -->
      <template #trigger>
        <slot name="trigger"></slot>
      </template>
      
      <!-- 自定义内容插槽 -->
      <template v-if="useDefaultSlot || useHeaderSlot">
        <!-- 自定义标题插槽 -->
        <template v-if="useHeaderSlot" #header>
          <slot name="header"></slot>
        </template>
        
        <!-- 当使用默认插槽时，渲染默认插槽内容 -->
        <slot v-if="useDefaultSlot"></slot>
      </template>
    </n-popover>
  </div>
</template>

<script setup lang="ts">
import { NPopover } from 'naive-ui';
import { ref, computed, useSlots, watch } from 'vue';

const props = defineProps({
  // 标题
  title: {
    type: String,
    default: ''
  },
  // 内容
  content: {
    type: String,
    default: ''
  },
  // 气泡卡片是否可见
  show: {
    type: Boolean,
    default: undefined
  },
  // 触发方式
  trigger: {
    type: String,
    default: 'click',
    validator: (val: string) => ['click', 'hover', 'focus', 'manual'].includes(val)
  },
  // 弹出位置
  placement: {
    type: String,
    default: 'bottom',
    validator: (val: string) => [
      'top', 'top-start', 'top-end',
      'right', 'right-start', 'right-end',
      'bottom', 'bottom-start', 'bottom-end',
      'left', 'left-start', 'left-end'
    ].includes(val)
  },
  // 宽度
  width: {
    type: [Number, String],
    default: 'trigger'
  },
  // 是否使用raw模式
  raw: {
    type: Boolean,
    default: false
  },
  // 是否显示箭头
  showArrow: {
    type: Boolean,
    default: true
  },
  // 触发后延时显示的时间 (毫秒)
  delay: {
    type: Number,
    default: 100
  },
  // 关闭后的持续时间 (毫秒)
  duration: {
    type: Number,
    default: 100
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 头部样式
  headerStyle: {
    type: Object,
    default: () => ({})
  },
  // 弹出位置的DOM元素
  to: {
    type: [String, Object, Boolean],
    default: 'body'
  },
  // 是否在放置不下时自动翻转
  flip: {
    type: Boolean,
    default: true
  },
  // 悬停时保持展开
  keepAliveOnHover: {
    type: Boolean,
    default: true
  },
  // 是否使用暗色主题
  dark: {
    type: Boolean,
    default: false
  },
  // 自定义类名
  className: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:show', 'clickoutside']);
const slots = useSlots();

// 检查是否使用了默认插槽和标题插槽
const useDefaultSlot = computed(() => !!slots.default);
const useHeaderSlot = computed(() => !!slots.header);

// 双向绑定状态
const showValue = ref(props.show);

// 监听外部传入的show变化
watch(() => props.show, (newVal: boolean | undefined) => {
  if (newVal !== undefined && newVal !== showValue.value) {
    showValue.value = newVal;
  }
}, { immediate: true });

// 处理显示状态变化
const handleUpdateShow = (value: boolean) => {
  showValue.value = value;
  emit('update:show', value);
};

// 处理点击外部事件
const handleClickOutside = (e: MouseEvent) => {
  emit('clickoutside', e);
};
</script>

<style scoped>
/* 可根据需要添加样式 */
</style> 