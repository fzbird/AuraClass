import { ref, computed, onMounted, onUnmounted, type ComputedRef } from 'vue';
import { useWindowSize } from '@vueuse/core';

// 断点定义（结合Naive UI和TailwindCSS）
export const breakpoints = {
  xs: 0,     // 超小屏幕，如手机竖屏
  sm: 640,   // 小屏幕，如手机横屏
  md: 768,   // 中等屏幕，如平板
  lg: 1024,  // 大屏幕，如笔记本
  xl: 1280,  // 特大屏幕，如桌面显示器
  '2xl': 1536 // 超大屏幕，如大型显示器
};

export type Breakpoint = keyof typeof breakpoints;
type BreakpointRecord<T> = Partial<Record<Breakpoint, T>>;

/**
 * 使用响应式断点检测 
 * 返回包含各断点判断的响应式对象
 */
export function useBreakpoints() {
  const { width } = useWindowSize();
  
  // 判断当前屏幕是否匹配某个断点
  const isXs = computed(() => width.value >= breakpoints.xs && width.value < breakpoints.sm);
  const isSm = computed(() => width.value >= breakpoints.sm && width.value < breakpoints.md);
  const isMd = computed(() => width.value >= breakpoints.md && width.value < breakpoints.lg);
  const isLg = computed(() => width.value >= breakpoints.lg && width.value < breakpoints.xl);
  const isXl = computed(() => width.value >= breakpoints.xl && width.value < breakpoints['2xl']);
  const is2xl = computed(() => width.value >= breakpoints['2xl']);
  
  // "及以上"组合断点
  const isSmAndUp = computed(() => width.value >= breakpoints.sm);
  const isMdAndUp = computed(() => width.value >= breakpoints.md);
  const isLgAndUp = computed(() => width.value >= breakpoints.lg);
  const isXlAndUp = computed(() => width.value >= breakpoints.xl);
  
  // "及以下"组合断点
  const isSmAndDown = computed(() => width.value < breakpoints.md);
  const isMdAndDown = computed(() => width.value < breakpoints.lg);
  const isLgAndDown = computed(() => width.value < breakpoints.xl);
  const isXlAndDown = computed(() => width.value < breakpoints['2xl']);
  
  // 根据窗口宽度获取当前断点
  const currentBreakpoint = computed<Breakpoint>(() => {
    if (width.value < breakpoints.sm) return 'xs';
    if (width.value < breakpoints.md) return 'sm';
    if (width.value < breakpoints.lg) return 'md';
    if (width.value < breakpoints.xl) return 'lg';
    if (width.value < breakpoints['2xl']) return 'xl';
    return '2xl';
  });
  
  // 断点判断辅助方法
  const isBreakpoint = (bp: Breakpoint) => computed(() => currentBreakpoint.value === bp);
  
  // 判断当前断点是否小于指定断点
  const smallerThan = (bp: Breakpoint) => computed(() => {
    const breakpointValue = breakpoints[bp];
    return width.value < breakpointValue;
  });
  
  // 判断当前断点是否大于等于指定断点
  const largerThan = (bp: Breakpoint) => computed(() => {
    const breakpointValue = breakpoints[bp];
    return width.value >= breakpointValue;
  });
  
  // 判断当前断点是否在指定范围内
  const between = (minBp: Breakpoint, maxBp: Breakpoint) => computed(() => {
    return width.value >= breakpoints[minBp] && width.value < breakpoints[maxBp];
  });
  
  // 设备类型辅助方法
  const isMobile = computed(() => width.value < breakpoints.md);
  const isTablet = computed(() => width.value >= breakpoints.md && width.value < breakpoints.lg);
  const isDesktop = computed(() => width.value >= breakpoints.lg);
  
  return {
    // 窗口宽度和当前断点
    windowWidth: width,
    currentBreakpoint,
    
    // 断点判断方法
    isBreakpoint,
    smallerThan,
    largerThan,
    between,
    
    // 单一断点检测
    isXs,
    isSm,
    isMd,
    isLg,
    isXl,
    is2xl,
    
    // 组合断点检测（向上）
    isSmAndUp,
    isMdAndUp,
    isLgAndUp,
    isXlAndUp,
    
    // 组合断点检测（向下）
    isSmAndDown,
    isMdAndDown,
    isLgAndDown,
    isXlAndDown,
    
    // 设备类型快捷方法
    isMobile,
    isTablet,
    isDesktop
  };
}

/**
 * 根据屏幕大小判断是否隐藏元素
 * 可用于条件渲染
 */
export function useResponsiveDisplay() {
  const { smallerThan, largerThan, between } = useBreakpoints();
  
  return {
    hideOnMobile: smallerThan('md'),
    showOnlyOnMobile: smallerThan('md'),
    hideOnTablet: between('sm', 'lg'),
    showOnlyOnTablet: between('sm', 'lg'),
    hideOnDesktop: largerThan('md'),
    showOnlyOnDesktop: largerThan('md')
  };
}

/**
 * 根据屏幕尺寸动态计算元素样式
 * @param baseSize 基础尺寸(px)
 * @param options 缩放选项
 * @returns 计算后的值作为字符串
 */
export function responsiveSize(
  baseSize: number,
  options?: {
    unit?: string;              // 单位，默认为px
    minSize?: number;           // 最小尺寸
    maxSize?: number;           // 最大尺寸
    scaleFactorMobile?: number; // 移动端缩放因子
    scaleFactorTablet?: number; // 平板缩放因子
  }
): ComputedRef<string> {
  const {
    unit = 'px',
    minSize,
    maxSize,
    scaleFactorMobile = 0.7,
    scaleFactorTablet = 0.85
  } = options || {};
  
  const { isMobile, isTablet } = useBreakpoints();
  
  return computed(() => {
    let size = baseSize;
    
    // 根据屏幕大小应用缩放
    if (isMobile.value) {
      size = baseSize * scaleFactorMobile;
    } else if (isTablet.value) {
      size = baseSize * scaleFactorTablet;
    }
    
    // 应用最小/最大限制
    if (minSize !== undefined) {
      size = Math.max(size, minSize);
    }
    if (maxSize !== undefined) {
      size = Math.min(size, maxSize);
    }
    
    return `${size}${unit}`;
  });
}

/**
 * 根据断点应用不同值
 * @param values 不同断点对应的值
 * @returns 当前断点对应的值
 */
export function useBreakpointValue<T>(values: BreakpointRecord<T>): ComputedRef<T | undefined> {
  const { currentBreakpoint } = useBreakpoints();
  
  return computed(() => {
    // 先尝试获取当前断点的值
    if (values[currentBreakpoint.value] !== undefined) {
      return values[currentBreakpoint.value];
    }
    
    // 如果当前断点没有定义值，则逐级向下查找
    const breakpointOrder: Breakpoint[] = ['2xl', 'xl', 'lg', 'md', 'sm', 'xs'];
    const currentIndex = breakpointOrder.indexOf(currentBreakpoint.value);
    
    // 向下寻找最近的有定义值的断点
    for (let i = currentIndex + 1; i < breakpointOrder.length; i++) {
      const bp = breakpointOrder[i];
      if (values[bp] !== undefined) {
        return values[bp];
      }
    }
    
    // 如果没有找到，向上寻找
    for (let i = currentIndex - 1; i >= 0; i--) {
      const bp = breakpointOrder[i];
      if (values[bp] !== undefined) {
        return values[bp];
      }
    }
    
    return undefined;
  });
}

/**
 * 主动触发页面响应式布局
 * 在某些情况下（如动态内容加载后）需要主动触发
 */
export function triggerResponsiveUpdate(): void {
  window.dispatchEvent(new Event('resize'));
} 