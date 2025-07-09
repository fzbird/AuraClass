import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import relativeTime from 'dayjs/plugin/relativeTime';

// 初始化dayjs插件
dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

/**
 * 格式化日期时间
 * @param date 日期字符串或Date对象
 * @param format 格式化模式，默认为YYYY-MM-DD HH:mm:ss
 * @returns 格式化后的日期字符串
 */
export function formatTime(date: string | Date, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  if (!date) return '';
  
  try {
    return dayjs(date).format(format);
  } catch (error) {
    console.error('日期格式化错误:', error);
    return typeof date === 'string' ? date : date.toString();
  }
}

/**
 * 计算相对时间（例如"3小时前"）
 * @param date 日期字符串或Date对象
 * @returns 相对时间字符串
 */
export function timeFromNow(date: string | Date): string {
  if (!date) return '';
  
  try {
    return dayjs(date).fromNow();
  } catch (error) {
    console.error('相对时间计算错误:', error);
    return typeof date === 'string' ? date : date.toString();
  }
}

/**
 * 检查日期是否是今天
 * @param date 日期字符串或Date对象
 * @returns 是否为今天
 */
export function isToday(date: string | Date): boolean {
  if (!date) return false;
  
  try {
    return dayjs(date).isSame(dayjs(), 'day');
  } catch (error) {
    console.error('日期比较错误:', error);
    return false;
  }
}

/**
 * 智能格式化日期（今天显示时间，非今天显示日期）
 * @param date 日期字符串或Date对象
 * @returns 格式化后的日期时间
 */
export function smartFormatTime(date: string | Date): string {
  if (!date) return '';
  
  try {
    return isToday(date) 
      ? dayjs(date).format('HH:mm:ss') 
      : dayjs(date).format('YYYY-MM-DD');
  } catch (error) {
    console.error('智能日期格式化错误:', error);
    return typeof date === 'string' ? date : date.toString();
  }
} 