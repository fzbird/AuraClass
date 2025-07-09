<template>
  <div
    class="message-container relative"
    :class="{
      'user-message': isUser,
      'assistant-message': !isUser,
      'thinking-message': isThinkingMessage
    }"
  >
    <!-- Avatar container - positioned for both user and assistant -->
    <div class="avatar-container" :class="{ 'user-avatar-container': isUser }">
      <div class="avatar" :class="isUser ? 'user-avatar' : 'assistant-avatar'">
        <img :src="isUser ? '/assets/user-avatar.png' : '/assets/assistant-avatar.png'" :alt="isUser ? '用户' : 'AI助手'" />
      </div>
      <div class="avatar-name">{{ isUser ? '我' : 'AI助手' }}</div>
    </div>

    <!-- Message bubble -->
    <div
      class="message-bubble"
      :class="[
        isUser ? 'user-bubble' : 'assistant-bubble',
        compact ? 'compact' : '',
        isThinkingMessage ? 'thinking-bubble' : '',
        (message as any)._replacedAiContent && (message as any)._transitionComplete ? 'transition-out' : ''
      ]"
      ref="messageBubbleRef"
    >
      <!-- 思考中状态显示 -->
      <div 
        v-if="isThinkingMessage" 
        class="thinking-indicator"
        :class="{ 'fade-out': (message as any)._replacedAiContent }"
      >
        <span class="thinking-text">正在思考中</span>
        <span class="thinking-dots">
          <span class="dot dot1"></span>
          <span class="dot dot2"></span>
          <span class="dot dot3"></span>
        </span>
      </div>
      
      <!-- 普通消息内容 -->
      <div v-if="!isThinkingMessage" 
        class="message-content compact-markdown" 
        v-html="formattedContent"
        @click="handleThinkToggleClick"
      ></div>
        
      <!-- 错误提示 - 仅当内容真的为空时显示 -->
      <div v-if="isContentEmpty && !isThinkingMessage" class="error-message text-sm text-red-500 mt-2">
        (消息内容为空，可能是数据加载问题)
      </div>
      
      <!-- 时间戳显示 -->
      <div class="message-status-bar text-xs mt-2 flex items-center justify-between">
        <span class="timestamp text-gray-500">{{ formatTime }}</span>
      
        <!-- 消息操作按钮 -->
        <div class="message-actions">
          <n-button text size="small" @click="copyMessage">
          <template #icon>
              <n-icon size="16"><copy-outlined /></n-icon>
          </template>
            复制
        </n-button>
        
          <n-button v-if="isUser" text size="small" @click="copyToInput">
          <template #icon>
              <n-icon size="16"><edit-outlined /></n-icon>
          </template>
            复制到输入框
        </n-button>
        
          <n-button text size="small" @click="deleteMessage" type="error">
          <template #icon>
              <n-icon size="16"><delete-outlined /></n-icon>
          </template>
            删除
        </n-button>
      </div>
    </div>

      <!-- 调试信息 (开发环境显示) -->
      <div v-if="isDev" class="debug-info text-xs text-gray-400 mb-2">
        {{ debugInfo }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import { useAIAssistantStore } from '@/stores/ai-assistant';
import { useMessage, NButton, NIcon } from 'naive-ui';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import 'dayjs/locale/zh-cn';
import type { UnifiedMessage } from '@/types/assistant'; // 使用type import
import CopyOutlined from '@vicons/antd/es/CopyOutlined';
import EditOutlined from '@vicons/antd/es/EditOutlined';
import DeleteOutlined from '@vicons/antd/es/DeleteOutlined';

dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.locale('zh-cn');

// 内联日期格式化函数
function formatTimeUtil(date: string | Date, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  if (!date) return '';
  
  try {
    // 如果原始时间中包含T，可能是ISO格式的UTC时间
    let dateStr = typeof date === 'string' ? date : date.toString();
    const hasIsoFormat = typeof dateStr === 'string' && dateStr.includes('T');

    // 假设所有从后端接收的时间戳都是UTC时间，无论它们是否包含时区信息
    // 先解析为UTC，然后转换为上海时区
    const parsedDate = hasIsoFormat 
      ? dayjs.utc(dateStr).tz('Asia/Shanghai')
      : dayjs(dateStr).tz('Asia/Shanghai');
    
    // 使用指定格式返回上海时区的时间
    // 确保显示的时间格式不包含T分隔符
    const formattedTime = parsedDate.format(format);
    
    // 调试输出
    console.log(`原始时间: ${dateStr}, 格式化后: ${formattedTime}`);
    
    return formattedTime;
  } catch (error) {
    console.error('日期格式化错误:', error);
    return typeof date === 'string' ? date : date.toString();
  }
}

// 完善清理内容函数，处理可能包含的特殊内容
function cleanContent(content: string): string {
  if (!content) return '';
  
  // 确保是字符串类型
  if (typeof content !== 'string') {
    try {
      content = String(content);
    } catch (e) {
      console.error('内容转换为字符串失败:', e);
      return '';
    }
  }
  
  // 特殊处理AI助手返回的内容
  if (content.includes('[图片:') || content.includes('[文件:')) {
    // 保留文件链接但美化显示
    content = content.replace(/\[图片:\s*([^|]+)\|([^\]]+)\]/g, '<img src="$2" alt="图片: $1" />');
    content = content.replace(/\[文件:\s*([^|]+)\|([^\]]+)\]/g, '<a href="$2" target="_blank">文件: $1</a>');
  }
  
  // 清理消息内容中的时间戳行
  
  // 1. 移除标准日期格式行（如：2025-05-03 09:14:43）
  content = content.replace(/^\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}.*$/gm, '');
  
  // 2. 移除ISO日期格式行（如：2025-05-03T09:14:43.000Z）
  content = content.replace(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*$/gm, '');
  
  // 3. 移除"时间戳:"或"时间化:"开头的行
  content = content.replace(/^时间[戳化][:：].*$/gm, '');
  
  // 4. 移除其他可能格式的日期行
  content = content.replace(/^\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}\s+\d{1,2}:\d{1,2}(:\d{1,2})?.*$/gm, '');
  
  // 5. 移除带有"处理时间"的行
  content = content.replace(/^.*处理时间[:：].*$/gm, '');
  content = content.replace(/^.*(处理|耗时)[:：].*$/gm, '');
  
  // 6. 移除以日期开头的行（比如"2025-05-03..."）
  content = content.replace(/^\d{4}-\d{2}-\d{2}.*$/gm, '');
  
  // 标准化换行符
  content = content.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  
  // 处理连续的空行，保留最多两个换行符
  content = content.replace(/\n{3,}/g, '\n\n');
  
  // 去除两端的空白
  content = content.trim();
  
  return content;
}

// 简单的Markdown转HTML处理
function simpleMarkdownToHtml(markdown: string): string {
  if (!markdown) return '';
  
  // 检查是否需要作为Markdown处理
  const containsMarkdown = /[*#`\[\]\(\)\n\-\|]/.test(markdown);
  
  // 如果是纯文本，不包含任何Markdown标记，仅做基本处理
  if (!containsMarkdown) {
    return `<div class="plain-text">${markdown.replace(/\n/g, '<br>')}</div>`;
  }
  
  let processedMarkdown = markdown;
  
  // 处理代码块 - 先处理代码块以避免干扰其他格式
  processedMarkdown = processedMarkdown.replace(/```([\s\S]*?)```/g, (match, content) => {
    const codeBlockMatch = match.match(/```(?:(\w+))?\n([\s\S]*?)```/);
    const language = codeBlockMatch?.[1] || '';
    const code = codeBlockMatch?.[2] || '';
    
    // 转义HTML字符
    const escapedCode = code
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    return `<pre class="code-block"><code class="language-${language}">${escapedCode}</code></pre>`;
});

  // 处理行内代码
  processedMarkdown = processedMarkdown.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  
  // 处理标题 - 使用更小的标题尺寸
  processedMarkdown = processedMarkdown.replace(/^# (.*$)/gm, '<h4 class="md-h1">$1</h4>');
  processedMarkdown = processedMarkdown.replace(/^## (.*$)/gm, '<h5 class="md-h2">$1</h5>');
  processedMarkdown = processedMarkdown.replace(/^### (.*$)/gm, '<h6 class="md-h3">$1</h6>');
  processedMarkdown = processedMarkdown.replace(/^#### (.*$)/gm, '<h6 class="md-h4">$1</h6>');

  // 处理引用
  processedMarkdown = processedMarkdown.replace(/^>\s+(.*$)/gm, '<blockquote class="md-quote">$1</blockquote>');
  
  // 处理水平线
  processedMarkdown = processedMarkdown.replace(/^---+$/gm, '<hr class="md-hr">');
  processedMarkdown = processedMarkdown.replace(/^\*\*\*+$/gm, '<hr class="md-hr">');

  // 处理链接
  processedMarkdown = processedMarkdown.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="md-link" target="_blank" rel="noopener noreferrer">$1</a>');
  
  // 处理图片
  processedMarkdown = processedMarkdown.replace(/!\[([^\]]+)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="md-image" />');
  
  // 处理粗体和斜体 - 确保样式一致
  processedMarkdown = processedMarkdown.replace(/\*\*([^*]+)\*\*/g, '<strong class="md-bold">$1</strong>');
  processedMarkdown = processedMarkdown.replace(/\*([^*]+)\*/g, '<em class="md-italic">$1</em>');
  processedMarkdown = processedMarkdown.replace(/_([^_]+)_/g, '<em class="md-italic">$1</em>');
  
  // 更紧凑的列表处理
  const lines = processedMarkdown.split('\n');
  let inList = false;
  let listType = '';
  
  for (let i = 0; i < lines.length; i++) {
    // 无序列表项
    if (lines[i].match(/^\s*[\*\-]\s+(.*)/)) {
      const content = lines[i].match(/^\s*[\*\-]\s+(.*)/)?.[1] || '';
      if (!inList || listType !== 'ul') {
        inList = true;
        listType = 'ul';
        lines[i] = `<ul class="md-ul"><li class="md-li">${content}</li>`;
      } else {
        lines[i] = `<li class="md-li">${content}</li>`;
      }
      continue;
    }
    
    // 有序列表项
    if (lines[i].match(/^\s*(\d+)[\.\)]\s+(.*)/)) {
      const content = lines[i].match(/^\s*(\d+)[\.\)]\s+(.*)/)?.[2] || '';
      if (!inList || listType !== 'ol') {
        inList = true;
        listType = 'ol';
        lines[i] = `<ol class="md-ol"><li class="md-li">${content}</li>`;
      } else {
        lines[i] = `<li class="md-li">${content}</li>`;
      }
      continue;
    }
    
    // 非列表项，结束当前列表
    if (inList) {
      const endTag = listType === 'ul' ? '</ul>' : '</ol>';
      lines[i-1] += endTag;
      inList = false;
      listType = '';
    }
  }
  
  // 确保最后一个列表被关闭
  if (inList) {
    const endTag = listType === 'ul' ? '</ul>' : '</ol>';
    lines[lines.length-1] += endTag;
}

  // 重新组合处理后的行
  processedMarkdown = lines.join('\n');
  
  // 紧凑的段落处理
  processedMarkdown = processedMarkdown.replace(/\n\n+/g, '\n\n');
  const segments = processedMarkdown.split(/\n\n/);
  
  let result = [];
  for (let i = 0; i < segments.length; i++) {
    const segment = segments[i].trim();
    if (!segment) continue;
    
    // 跳过已经是HTML标签的内容
    if (/<\/?[a-z][\s\S]*>/i.test(segment)) {
      result.push(segment);
    } else {
      // 把每段文本包装成段落
      const cleanedText = segment.replace(/\n/g, '<br>').trim();
      result.push(`<p class="md-p">${cleanedText}</p>`);
    }
  }
  
  // 重新连接处理后的片段
  processedMarkdown = result.join('');
  
  // 清理多余空白
  processedMarkdown = processedMarkdown.replace(/(<\/[^>]+>)(\s*)(<[^>]+>)/g, '$1$3');
  
  return `<div class="markdown-content compact-markdown">${processedMarkdown}</div>`;
}

// 组件类型定义
type MessageType = UnifiedMessage;

// 添加消息操作事件
const emit = defineEmits(['copy-to-input', 'delete']);

// 添加类型声明
const props = defineProps<{
  message: MessageType;
  isUser: boolean;
  compact?: boolean;
}>();

const message = useMessage();
const aiAssistantStore = useAIAssistantStore();
const userStore = useUserStore();

// 确保开发环境下显示调试信息
const isDev = import.meta.env.DEV || import.meta.env.MODE === 'development';

// 准备调试信息
const debugInfo = computed(() => {
  const msgInfo = props.message;
  if (!msgInfo) return 'Empty message';
  
  // 基本信息，不包含时间戳信息
  return `ID: ${msgInfo.id}, 角色: ${msgInfo.role}${msgInfo.processing_time ? ', 处理时间: ' + msgInfo.processing_time + 'ms' : ''}${msgInfo.is_thinking ? ', 思考中: true' : ''}${(msgInfo as any).is_timeout_message ? ', 超时: true' : ''}`;
});

// 日志
console.log('消息内容:', props.message);

// 获取用户名称
const userName = computed(() => {
  // @ts-ignore - 忽略属性检查，实际运行时会有正确属性
  return userStore.user?.username || userStore.user?.full_name || '用户';
});

// 添加状态变量
const initialThinkingState = ref<boolean | null>(null);
const canEndThinking = ref(false);

// 判断是否是思考中消息
const isThinkingMessage = computed(() => {
  // 检查是否已被标记为AI内容替换和过渡完成
  if ((props.message as any)._replacedAiContent && (props.message as any)._transitionComplete) {
    // 已被替换为AI回复且过渡动画已完成，不再是思考中消息
    return false;
  }
  
  // 如果是从思考中状态转换到内容状态但尚未完成过渡，保持思考状态的外观
  if ((props.message as any)._replacedAiContent && !(props.message as any)._transitionComplete) {
    // 消息内容已替换但过渡尚未完成，保持思考状态的样式
    return true;
  }
  
  // 添加额外条件并强制延迟识别，确保消息即使属性变了也保持思考状态足够长时间
  // 使用ref保存初始状态，防止状态被快速更改
  if (initialThinkingState.value === null) {
    initialThinkingState.value = !!props.message.is_thinking || 
      !!(props.message as any)._forceThinking || // 使用类型断言
         props.message.content === '正在思考中...' ||
      (typeof props.message.content === 'string' && props.message.content.includes('思考中')) ||
      (props.message.role === 'assistant' && props.message.content && 
       typeof props.message.content === 'string' && props.message.content.startsWith('正在思考')) ||
      (props.message.role === 'assistant' && props.message.is_timeout_message === true);
      
    // 如果初始状态是思考中，设置一个强制延迟结束计时器
    if (initialThinkingState.value) {
      // 确保思考状态至少显示6秒，即使后端快速响应
      setTimeout(() => {
        canEndThinking.value = true;
      }, 6000);
    }
  }
  
  // 如果消息已明确标记为不是思考状态，则直接返回false
  if (props.message.is_thinking === false || (props.message as any)._forceThinking === false) {
    return false;
  }
  
  // 当前实际状态
  const currentThinking = !!props.message.is_thinking || 
    !!(props.message as any)._forceThinking || // 使用类型断言
         props.message.content === '正在思考中...' ||
    (typeof props.message.content === 'string' && props.message.content.includes('思考中')) ||
    (props.message.role === 'assistant' && props.message.content && 
     typeof props.message.content === 'string' && props.message.content.startsWith('正在思考')) ||
    (props.message.role === 'assistant' && props.message.is_timeout_message === true);

  // 如果初始状态是思考中，但计时器还没到，则保持思考状态
  const isThinking = initialThinkingState.value && !canEndThinking.value ? true : currentThinking;
  
  // 在开发环境下输出调试信息
  if(isDev) {
    console.log(`消息ID:${props.message.id} 判断思考中状态:${isThinking}, `, 
      `is_thinking标志:${props.message.is_thinking}, 强制标记:${(props.message as any)._forceThinking}, `,
      `初始状态:${initialThinkingState.value}, 可结束:${canEndThinking.value}, `,
      `替换标记:${(props.message as any)._replacedAiContent || false}, `,
      `过渡完成:${(props.message as any)._transitionComplete || false}, `,
      `内容:"${props.message.content?.substring(0, 20)}..."`, 
      `角色:${props.message.role}`);
  }
  
  return isThinking;
});

// 判断内容是否为真正的空
const isContentEmpty = computed(() => {
  // 如果是思考消息，不要显示空内容提示
  if (isThinkingMessage.value) return false;
  
  // 获取原始内容
  const rawContent = props.message.content;
  
  // 严格检查内容是否为空
  return rawContent === null || rawContent === undefined || rawContent.trim() === '';
});

// 加强消息显示逻辑
const formattedContent = computed(() => {
  // 处理思考状态转换为内容状态的特殊情况
  if ((props.message as any)._replacedAiContent && !(props.message as any)._transitionComplete) {
    // 已替换内容但过渡动画尚未完成，返回空内容以保持思考动画显示
    return '';
  }
  
  // 如果是思考中状态，不显示内容（已由thinking-indicator组件处理）
  if (isThinkingMessage.value) {
    return '';
  }
  
  // 确保内容非空
  let content = props.message.content || '';
  if (!content || content.trim() === '') {
    console.warn(`消息内容为空: ID=${props.message.id}, 角色=${props.message.role}`);
    return ''; // 返回空字符串，让空消息提示显示
  }
  
  // 清理内容，移除可能包含的时间戳行
  content = cleanContent(content);
  
  // 移除可能存在的时间戳行 - 格式为日期时间格式
  content = content.replace(/^\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}.*$/gm, '');
  
  // 再次检查清理后的内容是否为空
  if (!content || content.trim() === '') {
    return '';
  }
  
  try {
    // 使用简单的Markdown转HTML实现
    return simpleMarkdownToHtml(content);
  } catch (e) {
    console.error('渲染消息内容失败:', e);
    // 异常时返回纯文本格式，确保安全显示
    const safeContent = content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br>');
    return `<div class="plain-text">${safeContent}</div>`;
  }
});

// 格式化时间戳
const formatTime = computed(() => {
  if (!props.message.timestamp) return '';
  
  // 基础时间戳 - 使用更简洁的格式
  let timeStr = formatTimeUtil(props.message.timestamp, 'YYYY-MM-DD HH:mm:ss');
  
  // 如果有处理时间，添加显示（仅针对AI消息）
  if (!props.isUser && props.message.processing_time !== undefined && props.message.processing_time > 0) {
    // 使用更简洁的格式
    const processingTime = props.message.processing_time.toFixed(2);
    timeStr += ` · 处理: ${processingTime}秒`;
  }
  
  return timeStr;
});

// 添加思考开关控制
const isThinkDetailsVisible = ref(false);
const thinkingDetails = ref('');

// 处理思考切换点击
const handleThinkToggleClick = (e: MouseEvent) => {
  // 只有AI消息才能点击查看思考
  if (props.isUser || isThinkingMessage.value) return;
  
  // 检查是否有id
  if (!props.message.id) {
    console.warn('消息没有ID，无法获取思考过程');
    message.warning('无法获取思考过程');
    return;
  }
}

// 复制消息内容到剪贴板
const copyMessage = () => {
  if (!props.message.content) return;
  
  navigator.clipboard.writeText(props.message.content)
    .then(() => {
      message.success('已复制到剪贴板');
    })
    .catch(err => {
    console.error('复制失败:', err);
    message.error('复制失败');
  });
};

// 复制消息内容到输入框
const copyToInput = () => {
  emit('copy-to-input', props.message.content);
};

// 删除消息
const deleteMessage = () => {
  // Make sure the message has an ID and conversation_id
  if (!props.message.id) {
    message.error('无法删除：消息ID无效');
    return;
  }
  
  // Get the conversation_id from either conversation_id or conversationId property
  const conversationId = props.message.conversation_id || (props.message as any).conversationId;
  
  if (!conversationId) {
    message.error('无法删除：对话ID无效');
    return;
  }
  
  // Emit the delete event with the necessary parameters
  emit('delete', props.message.id, conversationId);
};

onMounted(() => {
  console.log('消息气泡组件挂载:', props.message);

  // 特别记录思考中状态
  if (isThinkingMessage.value) {
    console.log(`思考中消息挂载成功 - ID: ${props.message.id}, 内容: ${props.message.content}`);
  }
});
</script>

<style scoped>
/* 基本布局样式 */
.message-container {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in-out;
  align-items: flex-start;
  transition: all 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 用户消息和AI消息的布局方向 */
.user-message {
  flex-direction: row-reverse;
}

.assistant-message {
  flex-direction: row;
}

.thinking-message {
  opacity: 0.85;
  transition: opacity 0.4s ease-in-out;
}

/* 头像容器的基本样式 */
.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

/* 助手消息的头像容器 */
.assistant-message .avatar-container {
  margin-right: 12px;
}

/* 用户消息的头像容器 */
.user-message .avatar-container {
  margin-left: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 4px;
}

.user-avatar {
  /* background-color: #3498db; */
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-name {
  font-size: 12px;
  color: #666;
}

.message-bubble {
  padding: 10px 14px;
  border-radius: 12px;
  max-width: 75%;
  position: relative;
  word-break: break-word;
  flex: 1;
  transition: all 0.3s ease-in-out;
}

/* 处理不同消息类型的气泡样式 */
.user-bubble {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
  margin-left: auto;
  margin-right: 0;
  color: #333;
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

.assistant-bubble {
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  margin-right: auto;
  margin-left: 0;
  color: #333;
  transition: background-color 0.4s ease-in-out, border 0.4s ease-in-out, box-shadow 0.4s ease-in-out, color 0.3s ease;
}

/* 添加深色模式样式 */
:root.dark .user-bubble {
  background-color: #0c2a43;
  border-color: #1668dc;
  color: #e5e5e5;
}

:root.dark .assistant-bubble {
  background-color: #1f1f23;
  border-color: #333;
  color: #e5e5e5;
}

:root.dark .avatar-name {
  color: #a0aec0;
}

:root.dark .message-status-bar .timestamp {
  color: #a0aec0;
}

.thinking-bubble {
  background-color: #e6f7ff !important;
  border: 2px dashed #1890ff !important;
  animation: thinking-pulse 2.5s infinite ease-in-out, appear 0.5s ease-in-out !important;
  transition: all 0.3s ease-in-out !important; /* 确保从思考状态到正常状态有平滑过渡 */
}

/* 专门处理从思考状态到内容状态的过渡 */
.thinking-bubble.transition-out {
  animation: none !important;
  background-color: #f5f5f5 !important;
  border: 1px solid #e0e0e0 !important;
  box-shadow: none !important;
  transition: all 0.4s ease-in-out !important;
}

@keyframes thinking-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(24, 144, 255, 0.6);
  }
  70% {
    box-shadow: 0 0 0 12px rgba(24, 144, 255, 0);
}
  100% {
    box-shadow: 0 0 0 0 rgba(24, 144, 255, 0);
  }
}

.thinking-indicator {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 12px 5px;
  animation: appear 0.5s ease-in-out;
  transition: opacity 0.3s ease-out; /* 添加淡出过渡效果 */
}

/* 思考指示器的淡出效果 */
.thinking-indicator.fade-out {
  opacity: 0;
  transition: opacity 0.3s ease-out;
}

.thinking-text {
  margin-right: 12px;
  color: #1890ff;
  font-weight: 600;
  font-size: 16px;
  transition: opacity 0.3s ease-out;
}

.thinking-dots {
  display: flex;
  align-items: center;
  transition: opacity 0.3s ease-out;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #1890ff;
  margin: 0 5px;
  display: inline-block;
  animation: dot-pulse 1.5s infinite ease-in-out;
}

.dot1 {
  animation-delay: 0s;
}

.dot2 {
  animation-delay: 0.25s;
}

.dot3 {
  animation-delay: 0.5s;
}

@keyframes dot-pulse {
  0% {
    transform: scale(0.7);
    opacity: 0.5;
}
  50% {
    transform: scale(1.6);
    opacity: 1;
  }
  100% {
    transform: scale(0.7);
    opacity: 0.5;
}
}

@keyframes appear {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 消息内容的出现动画 */
.message-content {
  white-space: pre-wrap;
  line-height: 1.5;
  font-size: 14px;
  word-break: break-word;
  animation: content-appear 0.3s ease-in-out;
}

@keyframes content-appear {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
}
}

/* 普通文本样式 */
.plain-text {
  font-size: 14px;
  font-weight: normal;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 其他辅助样式 */
.empty-message {
  color: #f5222d;
  font-size: 14px;
  margin-top: 5px;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  user-select: none;
}

.user-message .message-time {
  text-align: right;
}

.assistant-message .message-time {
  text-align: left;
}

.compact {
  padding: 8px 12px;
  font-size: 12px;
}

.compact .message-time {
  font-size: 10px;
}

/* 特殊时间标识样式 */
.processing-time {
  margin-left: 8px;
  color: #888;
  font-size: 12px;
}

/* 错误消息样式 */
.error-message {
  color: #ff4d4f;
  margin-top: 8px;
  font-size: 12px;
}

/* 超时消息样式 */
.timeout-indicator {
  background-color: #fff1f0;
  border: 1px solid #ffccc7;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #ff4d4f;
  margin-top: 8px;
  display: inline-flex;
  align-items: center;
}

/* 调试信息样式 */
.debug-info {
  color: #999;
  font-size: 10px;
  margin-top: 8px;
  padding: 4px 8px;
  background-color: #f9f9f9;
  border-radius: 4px;
  white-space: pre-wrap;
  transition: background-color 0.3s ease, color 0.3s ease;
}

:root.dark .debug-info {
  background-color: #1a1a1a;
  color: #a0aec0;
}

/* Global styles for markdown content - applied to all markdown elements */
.compact-markdown {
  font-size: 14px !important;
}

/* Reset all margins for markdown elements */
.compact-markdown * {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1.4 !important;
  font-size: inherit !important;
}

/* Paragraph styling */
.compact-markdown p,
.compact-markdown .md-p {
  margin: 0 0 4px 0 !important;
}

/* Ensure the last paragraph has no bottom margin */
.compact-markdown p:last-child,
.compact-markdown .md-p:last-child {
  margin-bottom: 0 !important;
}

/* Header styling - smaller than default */
.compact-markdown h1, .compact-markdown h2, .compact-markdown h3, 
.compact-markdown h4, .compact-markdown h5, .compact-markdown h6,
.compact-markdown .md-h1, .compact-markdown .md-h2, 
.compact-markdown .md-h3, .compact-markdown .md-h4 {
  margin: 6px 0 4px 0 !important;
  font-weight: bold !important;
}

.compact-markdown h1, .compact-markdown .md-h1 {
  font-size: 1.2em !important;
}

.compact-markdown h2, .compact-markdown .md-h2 {
  font-size: 1.1em !important;
}

.compact-markdown h3, .compact-markdown .md-h3,
.compact-markdown h4, .compact-markdown .md-h4 {
  font-size: 1em !important;
}

/* Lists styling */
.compact-markdown ul, 
.compact-markdown ol,
.compact-markdown .md-ul,
.compact-markdown .md-ol {
  margin: 2px 0 4px 0 !important;
  padding-left: 20px !important;
}

.compact-markdown li,
.compact-markdown .md-li {
  margin: 1px 0 !important;
  line-height: 1.4 !important;
}

/* Code blocks */
.compact-markdown pre,
.compact-markdown .code-block {
  margin: 4px 0 !important;
  padding: 8px !important;
  background-color: #f5f5f5 !important;
  border-radius: 4px !important;
  overflow-x: auto !important;
  transition: background-color 0.3s ease !important;
}

.compact-markdown code,
.compact-markdown .inline-code {
  padding: 2px 4px !important;
  background-color: #f5f5f5 !important;
  border-radius: 3px !important;
  font-family: monospace !important;
  font-size: 0.9em !important;
  transition: background-color 0.3s ease, color 0.3s ease !important;
}

/* 深色模式代码块 */
:root.dark .compact-markdown pre,
:root.dark .compact-markdown .code-block {
  background-color: #282c34 !important;
  border: 1px solid #3e4451 !important;
}

:root.dark .compact-markdown code,
:root.dark .compact-markdown .inline-code {
  background-color: #282c34 !important;
  color: #e5e5e5 !important;
}

/* Blockquotes */
.compact-markdown blockquote,
.compact-markdown .md-quote {
  margin: 4px 0 !important;
  padding: 0 0 0 10px !important;
  border-left: 3px solid #ddd !important;
  color: #666 !important;
  transition: border-color 0.3s ease, color 0.3s ease !important;
}

:root.dark .compact-markdown blockquote,
:root.dark .compact-markdown .md-quote {
  border-left-color: #4a5568 !important;
  color: #a0aec0 !important;
}

/* Bold and italic */
.compact-markdown strong,
.compact-markdown .md-bold {
  font-weight: bold !important;
  font-size: inherit !important;
}

.compact-markdown em,
.compact-markdown .md-italic {
  font-style: italic !important;
  font-size: inherit !important;
}

/* Links */
.compact-markdown a,
.compact-markdown .md-link {
  color: #1890ff !important;
  text-decoration: none !important;
  transition: color 0.3s ease !important;
}

.compact-markdown a:hover,
.compact-markdown .md-link:hover {
  text-decoration: underline !important;
}

:root.dark .compact-markdown a,
:root.dark .compact-markdown .md-link {
  color: #4dabf7 !important;
}

:root.dark .compact-markdown a:hover,
:root.dark .compact-markdown .md-link:hover {
  color: #74c0fc !important;
}

/* Images */
.compact-markdown img,
.compact-markdown .md-image {
  max-width: 100% !important;
  margin: 4px 0 !important;
}

/* Force smaller spacing in message bubbles */
.message-bubble p,
.message-bubble ul,
.message-bubble ol,
.message-bubble li,
.message-bubble blockquote {
  margin-top: 0 !important;
  margin-bottom: 4px !important;
  line-height: 1.4 !important;
}

/* Compact plain text */
.plain-text {
  margin: 0 !important;
  line-height: 1.4 !important;
}

/* Force tighter paragraph spacing with more specific selectors */
.message-bubble .markdown-content p,
.message-bubble .markdown-content > p,
.message-bubble .compact-markdown p,
.message-bubble .compact-markdown > p,
.message-bubble p {
  margin: 0 !important;
  padding: 0 !important;
  margin-bottom: 4px !important;
  line-height: 1.4 !important;
  font-size: 14px !important;
}

/* Force very tight list spacing */
.message-bubble .markdown-content ul,
.message-bubble .markdown-content ol,
.message-bubble .compact-markdown ul,
.message-bubble .compact-markdown ol {
  margin: 0 0 4px 0 !important;
  padding-left: 18px !important;
}

.message-bubble .markdown-content li,
.message-bubble .compact-markdown li {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1.4 !important;
}

/* Target direct HTML to ensure spacing is controlled */
.assistant-bubble div > p {
  margin: 0 0 4px 0 !important;
}

.assistant-bubble div > p:last-child {
  margin-bottom: 0 !important;
}

/* Compact any HTML in a message bubble */
.message-content > * {
  margin-top: 0 !important;
  margin-bottom: 4px !important;
}

.message-content > *:last-child {
  margin-bottom: 0 !important;
}

/* 状态条样式优化 */
.message-status-bar {
  padding: 2px 0;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  margin-top: 8px;
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timestamp {
  font-size: 11px;
  color: #888;
}

.user-bubble .timestamp {
  color: #0078d4;
}

.assistant-bubble .timestamp {
  color: #555;
}

/* 消息操作按钮相关样式 */
.message-bubble {
  position: relative;
}

.message-actions {
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, visibility 0.2s ease;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  }

.message-bubble:hover .message-actions {
    opacity: 1;
  visibility: visible;
}

/* 思考中动画适配深色模式 */
:root.dark .thinking-bubble {
  background-color: #0c2a43 !important;
  border: 2px dashed #4dabf7 !important;
}

:root.dark .thinking-text {
  color: #4dabf7;
}

:root.dark .dot {
  background-color: #4dabf7;
}

:root.dark .thinking-bubble.transition-out {
  background-color: #1f1f23 !important;
  border: 1px solid #333 !important;
}

/* 消息操作按钮深色模式 */
:root.dark .message-actions .n-button {
  color: #a0aec0;
}

:root.dark .message-actions .n-button:hover {
  color: #e5e5e5;
}

:root.dark .message-actions .n-button[type="error"] {
  color: #f56c6c;
}

/* 处理错误消息的深色模式 */
:root.dark .error-message {
  color: #ff6b6b;
}
</style>
