/**
 * 表单验证工具函数
 * 提供通用的表单字段验证功能
 */

// 基础验证类型
type ValidationResult = true | string;
type ValidationOptions = Record<string, any>;

/**
 * 验证必填字段
 * @param value 要验证的值
 * @param message 可选的错误消息
 * @returns 成功返回true，失败返回错误消息
 */
export function validateRequired(
  value: any,
  message = '此字段为必填项'
): ValidationResult {
  if (value === null || value === undefined) {
    return message;
  }
  
  if (typeof value === 'string' && value.trim() === '') {
    return message;
  }
  
  return true;
}

/**
 * 验证邮箱格式
 * @param value 要验证的邮箱
 * @param options 验证选项
 * @returns 成功返回true，失败返回错误消息
 */
export function validateEmail(
  value: string | null | undefined,
  options: { required?: boolean; message?: string } = {}
): ValidationResult {
  const { required = false, message = '请输入有效的邮箱地址' } = options;
  
  // 空值检查
  if (value === null || value === undefined || value === '') {
    return required ? '请输入邮箱地址' : true;
  }
  
  // 邮箱格式正则表达式
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  
  return emailRegex.test(value) ? true : message;
}

/**
 * 验证字符串长度
 * @param value 要验证的字符串
 * @param options 验证选项
 * @returns 成功返回true，失败返回错误消息
 */
export function validateLength(
  value: string | null | undefined,
  options: { min?: number; max?: number; required?: boolean; message?: string } = {}
): ValidationResult {
  const { min, max, required = false } = options;
  
  // 空值检查
  if (value === null || value === undefined || value === '') {
    return required ? '此字段为必填项' : true;
  }
  
  const length = value.length;
  
  // 最小长度检查
  if (min !== undefined && length < min) {
    return options.message || `长度不能少于${min}个字符`;
  }
  
  // 最大长度检查
  if (max !== undefined && length > max) {
    return options.message || `长度不能超过${max}个字符`;
  }
  
  return true;
}

/**
 * 验证手机号格式（中国大陆）
 * @param value 要验证的手机号
 * @param options 验证选项
 * @returns 成功返回true，失败返回错误消息
 */
export function validatePhone(
  value: string | null | undefined,
  options: { required?: boolean; message?: string } = {}
): ValidationResult {
  const { required = false, message = '请输入有效的手机号码' } = options;
  
  // 空值检查
  if (value === null || value === undefined || value === '') {
    return required ? '请输入手机号码' : true;
  }
  
  // 中国大陆手机号正则表达式
  const phoneRegex = /^1[3-9]\d{9}$/;
  
  return phoneRegex.test(value) ? true : message;
}

/**
 * 验证数字（整数或小数）
 * @param value 要验证的数字
 * @param options 验证选项
 * @returns 成功返回true，失败返回错误消息
 */
export function validateNumber(
  value: string | number | null | undefined,
  options: { min?: number; max?: number; required?: boolean; message?: string } = {}
): ValidationResult {
  const { min, max, required = false, message = '请输入有效的数字' } = options;
  
  // 空值检查
  if (value === null || value === undefined || value === '') {
    return required ? '请输入数字' : true;
  }
  
  // 转换为数字并检查有效性
  const num = Number(value);
  if (isNaN(num)) {
    return message;
  }
  
  // 范围检查
  if (min !== undefined && num < min) {
    return options.message || `不能小于${min}`;
  }
  
  if (max !== undefined && num > max) {
    return options.message || `不能大于${max}`;
  }
  
  return true;
}

/**
 * 验证整数
 * @param value 要验证的整数
 * @param options 验证选项
 * @returns 成功返回true，失败返回错误消息
 */
export function validateInteger(
  value: string | number | null | undefined,
  options: { min?: number; max?: number; required?: boolean; message?: string } = {}
): ValidationResult {
  const { required = false, message = '请输入有效的整数' } = options;
  
  // 空值检查
  if (value === null || value === undefined || value === '') {
    return required ? '请输入整数' : true;
  }
  
  // 整数正则表达式
  const intRegex = /^-?\d+$/;
  if (!intRegex.test(String(value))) {
    return message;
  }
  
  // 使用validateNumber进行范围检查
  return validateNumber(value, options);
}

/**
 * 验证密码强度
 * @param value 要验证的密码
 * @param options 验证选项
 * @returns 成功返回true，失败返回错误消息
 */
export function validatePassword(
  value: string | null | undefined,
  options: {
    min?: number;
    requireUppercase?: boolean;
    requireLowercase?: boolean;
    requireNumber?: boolean;
    requireSpecial?: boolean;
    message?: string;
  } = {}
): ValidationResult {
  const {
    min = 6,
    requireUppercase = false,
    requireLowercase = true,
    requireNumber = true,
    requireSpecial = false,
    message = '密码不符合要求'
  } = options;
  
  // 空值视为错误，密码通常是必填项
  if (value === null || value === undefined || value === '') {
    return '请输入密码';
  }
  
  // 长度检查
  if (value.length < min) {
    return `密码长度不能少于${min}个字符`;
  }
  
  // 字符类型检查
  const hasUppercase = /[A-Z]/.test(value);
  const hasLowercase = /[a-z]/.test(value);
  const hasNumber = /\d/.test(value);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value);
  
  // 验证各类字符要求
  if (requireUppercase && !hasUppercase) {
    return '密码需要包含大写字母';
  }
  
  if (requireLowercase && !hasLowercase) {
    return '密码需要包含小写字母';
  }
  
  if (requireNumber && !hasNumber) {
    return '密码需要包含数字';
  }
  
  if (requireSpecial && !hasSpecial) {
    return '密码需要包含特殊字符';
  }
  
  return true;
}

/**
 * 验证两个值是否匹配（如密码确认）
 * @param value 要验证的值
 * @param compareValue 要比较的值
 * @param message 可选的错误消息
 * @returns 成功返回true，失败返回错误消息
 */
export function validateMatch(
  value: any,
  compareValue: any,
  message = '两次输入不一致'
): ValidationResult {
  if (value === compareValue) {
    return true;
  }
  
  return message;
}

/**
 * 验证URL格式
 * @param value 要验证的URL
 * @param options 验证选项
 * @returns 成功返回true，失败返回错误消息
 */
export function validateUrl(
  value: string | null | undefined,
  options: { required?: boolean; message?: string } = {}
): ValidationResult {
  const { required = false, message = '请输入有效的URL' } = options;
  
  // 空值检查
  if (value === null || value === undefined || value === '') {
    return required ? '请输入URL' : true;
  }
  
  try {
    new URL(value);
    return true;
  } catch (e) {
    return message;
  }
}

/**
 * 验证中文姓名
 * @param value 要验证的姓名
 * @param options 验证选项
 * @returns 成功返回true，失败返回错误消息
 */
export function validateChineseName(
  value: string | null | undefined,
  options: { required?: boolean; message?: string } = {}
): ValidationResult {
  const { required = false, message = '请输入有效的中文姓名' } = options;
  
  // 空值检查
  if (value === null || value === undefined || value === '') {
    return required ? '请输入姓名' : true;
  }
  
  // 中文姓名正则（2-15个汉字）
  const nameRegex = /^[\u4e00-\u9fa5]{2,15}$/;
  
  return nameRegex.test(value) ? true : message;
}

/**
 * 验证身份证号（中国大陆）
 * @param value 要验证的身份证号
 * @param options 验证选项
 * @returns 成功返回true，失败返回错误消息
 */
export function validateIdCard(
  value: string | null | undefined,
  options: { required?: boolean; message?: string } = {}
): ValidationResult {
  const { required = false, message = '请输入有效的身份证号' } = options;
  
  // 空值检查
  if (value === null || value === undefined || value === '') {
    return required ? '请输入身份证号' : true;
  }
  
  // 身份证号正则（18位）
  const idCardRegex = /(^\d{17}[\dXx]$)/;
  
  if (!idCardRegex.test(value)) {
    return message;
  }
  
  // 简单的校验，实际应用中可能需要更复杂的验证逻辑
  return true;
} 