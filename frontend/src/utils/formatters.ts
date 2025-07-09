/**
 * 格式化工具函数
 * 提供日期、时间、分数等数据的格式化功能
 */
import dayjs from 'dayjs';

/**
 * 格式化日期
 * @param date 日期对象、时间戳或日期字符串
 * @param format 格式化模板，默认为YYYY-MM-DD
 * @returns 格式化后的日期字符串，无效日期返回空字符串
 */
export const formatDate = (
  date: Date | string | number | null | undefined,
  format = 'YYYY-MM-DD'
): string => {
  if (date === null || date === undefined) {
    return '';
  }
  
  try {
    const parsedDate = dayjs(date);
    return parsedDate.isValid() ? parsedDate.format(format) : '';
  } catch (error) {
    console.error('格式化日期错误:', error);
    return '';
  }
};

/**
 * 格式化日期时间
 * @param date 日期对象、时间戳或日期字符串
 * @param format 格式化模板，默认为YYYY-MM-DD HH:mm:ss
 * @returns 格式化后的日期时间字符串，无效日期返回空字符串
 */
export const formatDateTime = (
  date: Date | string | number | null | undefined,
  format = 'YYYY-MM-DD HH:mm:ss'
): string => {
  if (date === null || date === undefined) {
    return '';
  }
  
  try {
    const parsedDate = dayjs(date);
    return parsedDate.isValid() ? parsedDate.format(format) : '';
  } catch (error) {
    console.error('格式化日期时间错误:', error);
    return '';
  }
};

/**
 * 格式化分数
 * @param score 分数值
 * @param precision 小数位数，默认为2
 * @param defaultValue 无效分数时的默认值，默认为'-'
 * @returns 格式化后的分数字符串
 */
export const formatScore = (
  score: number | null | undefined,
  precision = 2,
  defaultValue = '-'
): string => {
  if (score === null || score === undefined || isNaN(score)) {
    return defaultValue;
  }
  
  // 处理分数范围，确保在0-100之间
  let validScore = Math.max(0, Math.min(100, score));
  
  // 根据精度进行四舍五入
  if (precision === 0) {
    return Math.round(validScore).toString();
  } else {
    const factor = Math.pow(10, precision);
    return (Math.round(validScore * factor) / factor).toFixed(precision);
  }
};

/**
 * 格式化金额为带千分位的字符串
 */
export function formatCurrency(amount: number): string {
  return amount.toLocaleString('zh-CN', { 
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

/**
 * 将蛇形命名(snake_case)转换为小驼峰命名(camelCase)
 */
export function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

/**
 * 将小驼峰命名(camelCase)转换为蛇形命名(snake_case)
 */
export function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
} 