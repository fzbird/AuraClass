/**
 * HTML净化工具函数
 * 用于处理用户输入的HTML内容，防止XSS攻击
 */

/**
 * 净化HTML字符串，移除潜在的恶意脚本
 * 
 * @param {string} html 输入的HTML字符串
 * @returns {string} 净化后的HTML字符串
 */
export const sanitizeHTML = (html: string): string => {
  if (!html) return '';
  
  // 创建一个DOMParser实例
  const parser = new DOMParser();
  
  // 将HTML字符串解析为DOM文档
  const doc = parser.parseFromString(html, 'text/html');
  
  // 移除所有script标签
  const scripts = doc.querySelectorAll('script');
  scripts.forEach(script => script.remove());
  
  // 移除所有事件属性(on*)
  const allElements = doc.querySelectorAll('*');
  allElements.forEach(el => {
    const attributes = el.attributes;
    for (let i = attributes.length - 1; i >= 0; i--) {
      const attrName = attributes[i].name;
      if (attrName.startsWith('on') || attrName === 'href' && attributes[i].value.startsWith('javascript:')) {
        el.removeAttribute(attrName);
      }
    }
  });
  
  // 移除iframe、object、embed等可能执行外部代码的元素
  const dangerousElements = doc.querySelectorAll('iframe, object, embed, base');
  dangerousElements.forEach(el => el.remove());
  
  // 返回净化后的HTML
  return doc.body.innerHTML;
};

/**
 * 完全删除所有HTML标签，只返回纯文本内容
 * 
 * @param {string} html 输入的HTML字符串
 * @returns {string} 提取的纯文本内容
 */
export const stripHTML = (html: string): string => {
  if (!html) return '';
  
  // 创建临时元素
  const temp = document.createElement('div');
  temp.innerHTML = html;
  
  // 返回元素中的纯文本内容
  return temp.textContent || temp.innerText || '';
}; 