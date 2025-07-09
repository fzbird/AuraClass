<template>
  <n-modal
    v-model:show="visible"
    :title="title"
    :mask-closable="maskClosable"
    :preset="preset"
    :auto-focus="autoFocus"
    :show-icon="showIcon"
    :style="style"
    :class="[className, modalClass]"
    :to="to"
    :transform-origin="transformOrigin"
    :width="width"
    :z-index="zIndex"
    :trap-focus="trapFocus"
    :close-on-esc="closeOnEsc"
    :bordered="bordered"
    :segmented="segmented"
    @update:show="handleShowChange"
    @close="handleClose"
    @after-enter="handleAfterEnter"
    @after-leave="handleAfterLeave"
    @esc="handleEsc"
  >
    <template #header v-if="$slots.header">
      <slot name="header" />
    </template>
    <template #header-extra v-if="$slots['header-extra']">
      <slot name="header-extra" />
    </template>
    <template #default>
      <slot />
    </template>
    <template #action v-if="!hideActionButtons || $slots.action">
      <slot name="action">
        <div class="app-modal-actions">
          <n-button @click="handleCancel" :disabled="loading">{{ cancelText }}</n-button>
          <n-button type="primary" @click="handleConfirm" :loading="loading">{{ confirmText }}</n-button>
        </div>
      </slot>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { NModal, NButton } from 'naive-ui';
import { ref, watch } from 'vue';
import type { CSSProperties } from 'vue';

const props = defineProps({
  // 是否显示模态框
  show: {
    type: Boolean,
    default: false
  },
  // 标题
  title: {
    type: String,
    default: ''
  },
  // 点击蒙层是否可关闭
  maskClosable: {
    type: Boolean,
    default: true
  },
  // 预设模式（dialog, card）
  preset: {
    type: String,
    default: 'dialog'
  },
  // 是否自动获取焦点
  autoFocus: {
    type: Boolean,
    default: true
  },
  // 是否显示图标
  showIcon: {
    type: Boolean,
    default: false
  },
  // 确认按钮文本
  confirmText: {
    type: String,
    default: '确认'
  },
  // 取消按钮文本
  cancelText: {
    type: String,
    default: '取消'
  },
  // 是否隐藏操作按钮
  hideActionButtons: {
    type: Boolean,
    default: false
  },
  // 加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 自定义样式
  style: {
    type: [String, Object] as unknown as () => string | CSSProperties,
    default: () => ({})
  },
  // 自定义类名
  className: {
    type: String,
    default: ''
  },
  // 模态框类名
  modalClass: {
    type: String,
    default: ''
  },
  // 挂载节点
  to: {
    type: [String, Object],
    default: undefined
  },
  // 变换原点
  transformOrigin: {
    type: String,
    default: 'center'
  },
  // 宽度
  width: {
    type: [Number, String],
    default: undefined
  },
  // z-index
  zIndex: {
    type: Number,
    default: undefined
  },
  // 是否限制焦点在模态框内
  trapFocus: {
    type: Boolean,
    default: true
  },
  // 是否支持ESC关闭
  closeOnEsc: {
    type: Boolean,
    default: true
  },
  // 是否显示边框
  bordered: {
    type: Boolean,
    default: false
  },
  // 分段设置
  segmented: {
    type: [Object, Boolean],
    default: false
  }
});

const emit = defineEmits([
  'update:show',
  'confirm',
  'cancel',
  'close',
  'after-enter',
  'after-leave',
  'esc'
]);

// 内部可见状态
const visible = ref(props.show);

// 同步外部 show 变化到内部状态
watch(() => props.show, (newVal) => {
  visible.value = newVal;
});

// 处理显示状态变化
const handleShowChange = (value: boolean) => {
  visible.value = value;
  emit('update:show', value);
};

// 处理确认
const handleConfirm = (e: MouseEvent) => {
  emit('confirm', e);
};

// 处理取消
const handleCancel = (e: MouseEvent) => {
  emit('cancel', e);
  handleShowChange(false);
};

// 处理关闭
const handleClose = () => {
  emit('close');
  handleShowChange(false);
};

// 处理进入后事件
const handleAfterEnter = () => {
  emit('after-enter');
};

// 处理离开后事件
const handleAfterLeave = () => {
  emit('after-leave');
};

// 处理ESC事件
const handleEsc = (e: KeyboardEvent) => {
  emit('esc', e);
};
</script>

<style scoped>
.app-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 