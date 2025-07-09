<template>
  <span
    :class="['app-time-label', className]"
    :style="style"
    @mouseover="hoverable ? (isShowingAbsolute = true) : null"
    @mouseleave="hoverable ? (isShowingAbsolute = false) : null"
  >
    {{ formattedTime }}
  </span>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import type { PropType, CSSProperties } from 'vue';

type TimeFormat = 'relative' | 'absolute' | 'auto';

interface TimeOptions {
  locale?: string;
  showSeconds?: boolean;
  showYear?: boolean;
  showTime?: boolean;
  defaultFormat?: TimeFormat;
}

const props = defineProps({
  // 时间值，可以是日期对象、时间戳或日期字符串
  time: {
    type: [Date, Number, String],
    required: true
  },
  // 显示格式: 'relative' - 相对时间（如"5分钟前"）, 'absolute' - 绝对时间（如"2023-01-01 12:00:00"）, 'auto' - 自动选择
  format: {
    type: String as PropType<TimeFormat>,
    default: 'auto'
  },
  // 是否可悬停切换格式
  hoverable: {
    type: Boolean,
    default: true
  },
  // 配置选项
  options: {
    type: Object as PropType<TimeOptions>,
    default: () => ({})
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

// 控制是否显示绝对时间
const isShowingAbsolute = ref(props.format === 'absolute');

// 设置默认选项
const defaultOptions: TimeOptions = {
  locale: 'zh-CN',
  showSeconds: false,
  showYear: true,
  showTime: true,
  defaultFormat: 'auto'
};

// 合并选项
const mergedOptions = computed(() => {
  return { ...defaultOptions, ...props.options };
});

// 解析时间为 Date 对象
const parseTime = (time: Date | number | string): Date => {
  if (time instanceof Date) {
    return time;
  }
  
  if (typeof time === 'number') {
    return new Date(time);
  }
  
  return new Date(time);
};

// 时间对象
const timeDate = computed(() => parseTime(props.time));

// 检查时间是否有效
const isValidTime = computed(() => {
  return !isNaN(timeDate.value.getTime());
});

// 获取相对时间文本
const getRelativeTimeText = (date: Date): string => {
  if (!isValidTime.value) {
    return '无效时间';
  }

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);
  const diffMonths = Math.floor(diffDays / 30);
  const diffYears = Math.floor(diffDays / 365);

  if (diffSeconds < 0) {
    // 未来时间处理
    const absDiffSeconds = Math.abs(diffSeconds);
    const absDiffMinutes = Math.floor(absDiffSeconds / 60);
    const absDiffHours = Math.floor(absDiffMinutes / 60);
    const absDiffDays = Math.floor(absDiffHours / 24);

    if (absDiffSeconds < 60) {
      return `${absDiffSeconds}秒后`;
    } else if (absDiffMinutes < 60) {
      return `${absDiffMinutes}分钟后`;
    } else if (absDiffHours < 24) {
      return `${absDiffHours}小时后`;
    } else if (absDiffDays < 30) {
      return `${absDiffDays}天后`;
    } else {
      // 超过30天，显示绝对时间
      return getAbsoluteTimeText(date);
    }
  } else {
    // 过去时间处理
    if (diffSeconds < 60) {
      return diffSeconds <= 5 ? '刚刚' : `${diffSeconds}秒前`;
    } else if (diffMinutes < 60) {
      return `${diffMinutes}分钟前`;
    } else if (diffHours < 24) {
      return `${diffHours}小时前`;
    } else if (diffDays < 30) {
      return `${diffDays}天前`;
    } else if (diffMonths < 12) {
      return `${diffMonths}个月前`;
    } else {
      return `${diffYears}年前`;
    }
  }
};

// 获取绝对时间文本
const getAbsoluteTimeText = (date: Date): string => {
  if (!isValidTime.value) {
    return '无效时间';
  }

  const options: Intl.DateTimeFormatOptions = {};
  
  if (mergedOptions.value.showYear) {
    options.year = 'numeric';
  }
  
  options.month = '2-digit';
  options.day = '2-digit';
  
  if (mergedOptions.value.showTime) {
    options.hour = '2-digit';
    options.minute = '2-digit';
    if (mergedOptions.value.showSeconds) {
      options.second = '2-digit';
    }
    options.hour12 = false;
  }
  
  try {
    return new Intl.DateTimeFormat(mergedOptions.value.locale, options).format(date);
  } catch (error) {
    console.error('格式化时间出错:', error);
    return '格式化错误';
  }
};

// 根据格式和悬停状态计算显示的时间
const formattedTime = computed(() => {
  if (!isValidTime.value) {
    return '无效时间';
  }
  
  if (props.format === 'absolute' || isShowingAbsolute.value) {
    return getAbsoluteTimeText(timeDate.value);
  }
  
  if (props.format === 'relative') {
    return getRelativeTimeText(timeDate.value);
  }
  
  // 'auto' 格式: 7天内显示相对时间，否则显示绝对时间
  const now = new Date();
  const diffMs = now.getTime() - timeDate.value.getTime();
  const diffDays = Math.abs(Math.floor(diffMs / (1000 * 60 * 60 * 24)));
  
  if (diffDays < 7) {
    return getRelativeTimeText(timeDate.value);
  } else {
    return getAbsoluteTimeText(timeDate.value);
  }
});

// 监听格式变化
watch(() => props.format, (newFormat) => {
  isShowingAbsolute.value = newFormat === 'absolute';
});

// 挂载时检查格式
onMounted(() => {
  isShowingAbsolute.value = props.format === 'absolute';
});
</script>

<style scoped>
.app-time-label {
  display: inline-block;
  cursor: default;
  transition: opacity 0.2s;
}

.app-time-label:hover {
  opacity: 0.8;
}
</style> 