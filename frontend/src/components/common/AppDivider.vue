<template>
  <n-divider
    :title-placement="titlePlacement"
    :dashed="dashed"
    :vertical="vertical"
    :style="style"
    :class="[className, customDividerClass]"
  >
    <slot />
  </n-divider>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { NDivider } from 'naive-ui';
import type { PropType, CSSProperties } from 'vue';

type TitlePlacement = 'left' | 'right' | 'center';

const props = defineProps({
  // 标题位置
  titlePlacement: {
    type: String as PropType<TitlePlacement>,
    default: 'center'
  },
  // 是否虚线
  dashed: {
    type: Boolean,
    default: false
  },
  // 是否垂直分割线
  vertical: {
    type: Boolean,
    default: false
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
  },
  // 自定义分隔线颜色
  color: {
    type: String,
    default: ''
  },
  // 自定义分隔线粗细
  thickness: {
    type: [String, Number],
    default: null
  },
  // 自定义间距
  margin: {
    type: [String, Number],
    default: null
  }
});

// 根据属性计算分隔线自定义样式类
const customDividerClass = computed(() => {
  const classes = ['app-divider'];
  
  if (props.vertical) {
    classes.push('app-divider-vertical');
  } else {
    classes.push('app-divider-horizontal');
  }
  
  if (props.dashed) {
    classes.push('app-divider-dashed');
  }
  
  return classes.join(' ');
});

// 处理自定义样式
const dividerStyle = computed(() => {
  const styleObj: Record<string, any> = {};
  
  if (props.color) {
    styleObj['--divider-color'] = props.color;
  }
  
  if (props.thickness !== null) {
    styleObj['--divider-thickness'] = typeof props.thickness === 'number' 
      ? `${props.thickness}px` 
      : props.thickness;
  }
  
  if (props.margin !== null) {
    styleObj['--divider-margin'] = typeof props.margin === 'number' 
      ? `${props.margin}px` 
      : props.margin;
  }
  
  return styleObj;
});
</script>

<style scoped>
.app-divider {
  --divider-color: var(--divider-color, #e5e5e5);
  --divider-thickness: var(--divider-thickness, 1px);
  --divider-margin: var(--divider-margin, 16px);
}

.app-divider-horizontal {
  margin: var(--divider-margin) 0;
}

.app-divider-vertical {
  margin: 0 var(--divider-margin);
}

/* 覆盖默认样式 */
:deep(.n-divider__line) {
  border-color: var(--divider-color);
}

:deep(.n-divider--horizontal .n-divider__line) {
  border-width: var(--divider-thickness);
}

:deep(.n-divider--vertical .n-divider__line) {
  border-width: var(--divider-thickness);
}
</style> 