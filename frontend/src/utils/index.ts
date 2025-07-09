import dayjs from 'dayjs';

/**
 * 格式化日期
 */
export const formatDate = (date: string | Date, format = 'YYYY-MM-DD'): string => {
  return dayjs(date).format(format);
};

/**
 * 格式化日期时间
 */
export const formatDateTime = (date: string | Date): string => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss');
};

/**
 * 计算时间差
 */
export const timeAgo = (date: string | Date): string => {
  const now = dayjs();
  const past = dayjs(date);
  const diffMinutes = now.diff(past, 'minute');
  
  if (diffMinutes < 1) return '刚刚';
  if (diffMinutes < 60) return `${diffMinutes}分钟前`;
  
  const diffHours = now.diff(past, 'hour');
  if (diffHours < 24) return `${diffHours}小时前`;
  
  const diffDays = now.diff(past, 'day');
  if (diffDays < 30) return `${diffDays}天前`;
  
  const diffMonths = now.diff(past, 'month');
  if (diffMonths < 12) return `${diffMonths}个月前`;
  
  return `${now.diff(past, 'year')}年前`;
};

/**
 * 格式化数字，添加千位分隔符
 */
export const formatNumber = (num: number): string => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

/**
 * 将分数值格式化为带一位小数的字符串
 */
export const formatScore = (score: number): string => {
  return Number(score).toFixed(1);
};

/**
 * 截断文本
 */
export const truncateText = (text: string, length = 30): string => {
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
};

/**
 * 生成随机颜色
 */
export const randomColor = (): string => {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
};

/**
 * 获取文件扩展名
 */
export const getFileExtension = (filename: string): string => {
  return filename.substring(filename.lastIndexOf('.') + 1);
};

/**
 * 文件大小格式化
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i];
};
