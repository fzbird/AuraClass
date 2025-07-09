import dayjs from 'dayjs';

/**
 * 格式化日期
 * @param date 日期字符串、Date对象或时间戳
 * @param format 格式化模式，默认为 'YYYY-MM-DD'
 * @returns 格式化后的日期字符串
 */
export const formatDate = (
  date: string | Date | number | null | undefined,
  format: string = 'YYYY-MM-DD'
): string => {
  if (!date) return '';
  
  try {
    return dayjs(date).format(format);
  } catch (error) {
    console.error('Date format error:', error);
    return '';
  }
};

/**
 * 格式化日期时间
 * @param date 日期字符串、Date对象或时间戳
 * @param format 格式化模式，默认为 'YYYY-MM-DD HH:mm:ss'
 * @returns 格式化后的日期时间字符串
 */
export const formatDateTime = (
  date: string | Date | number | null | undefined,
  format: string = 'YYYY-MM-DD HH:mm:ss'
): string => {
  return formatDate(date, format);
};

/**
 * 格式化分数
 * @param score 分数值，可以是数字或数字字符串
 * @returns 格式化后的分数字符串，保留1位小数（如果有小数部分）
 */
export const formatScore = (
  score: number | string | null | undefined
): string => {
  if (score === null || score === undefined || isNaN(Number(score))) {
    return '0';
  }
  
  const num = Number(score);
  
  // 如果是整数，直接返回整数字符串
  if (Number.isInteger(num)) {
    return num.toString();
  }
  
  // 否则保留1位小数
  return num.toFixed(1);
}; 