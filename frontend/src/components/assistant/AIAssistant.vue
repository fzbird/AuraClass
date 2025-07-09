<template>
  <div class="ai-assistant">
    <div class="assistant-toggle" @click="toggleAssistant">
      <n-button quaternary circle :class="{ active: isOpen }">
        <template #icon>
          <icon-assistant />
        </template>
      </n-button>
    </div>
    
    <n-drawer
      v-model:show="isOpen"
      :width="360"
      placement="right"
      :auto-focus="false"
    >
      <n-drawer-content title="AI助手">
        <template #header>
          <div class="drawer-header">
            <span>AI助手</span>
            <div class="connection-status">
              <n-badge :type="isConnected ? 'success' : 'error'" dot />
              <span class="status-text">{{ isConnected ? '已连接' : '未连接' }}</span>
              <n-tooltip v-if="!isConnected && connectionError" trigger="hover">
                <template #trigger>
                  <n-icon style="margin-left: 4px; cursor: help;">
                    <warning-outlined />
                  </n-icon>
                </template>
                {{ connectionError }}
              </n-tooltip>
              <n-button v-if="!isConnected" size="tiny" @click="handleReconnect" style="margin-left: 8px;">
                重连
              </n-button>
            </div>
            <n-button size="small" quaternary @click="clearChat">
              清空对话
            </n-button>
          </div>
        </template>
        
        <div class="assistant-chat">
          <div ref="chatContainerRef" class="chat-messages">
            <template v-if="messages.length === 0">
              <div class="welcome-message">
                <div class="assistant-avatar">
                  <icon-assistant :size="32" />
                </div>
                <div class="message-content ai-message-content">
                  <p>你好，我是AuraClass的AI助手。请问有什么可以帮助你的？</p>
                  <div class="suggestion-chips">
                    <n-button 
                      v-for="(suggestion, index) in suggestions" 
                      :key="index"
                      size="small"
                      quaternary
                      @click="sendMessage(suggestion)"
                    >
                      {{ suggestion }}
                    </n-button>
                  </div>
                </div>
              </div>
            </template>
            
            <div v-for="(msg, index) in messages" :key="index" class="message-item" :class="msg.role">
              <div v-if="msg.role === 'assistant'" class="assistant-avatar">
                <icon-assistant :size="24" />
              </div>
              <div v-else class="user-avatar">
                <icon-user :size="24" />
              </div>
              <div class="message-content" :class="{ 'error': isErrorMessage(msg), 'ai-message-content': msg.role === 'assistant' }">
                <!-- 错误提示图标 -->
                <n-icon v-if="isErrorMessage(msg)" class="error-icon" size="20">
                  <warning-outlined />
                </n-icon>
                
                <!-- 正在加载/思考中 -->
                <div v-if="msg.loading || msg.is_thinking">
                  <n-skeleton text :repeat="2" />
                </div>
                
                <!-- 普通消息 -->
                <div v-else>
                  <div v-if="isDatetimeError(msg)" class="datetime-error">
                    <p>{{ msg.content }}</p>
                    <n-collapse>
                      <n-collapse-item title="技术细节与修复方案">
                        <div class="fix-suggestion">
                          <p><strong>错误原因:</strong> 后端尝试将Python datetime对象序列化为JSON时失败</p>
                          <p><strong>修复建议:</strong> 后端需要使用自定义的JSON序列化器处理datetime对象</p>
                          <pre class="code-block">
from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# 在WebSocket响应中使用此编码器
await websocket.send_json(
    data_with_datetime_objects,
    encoder=DateTimeEncoder
)
                          </pre>
                        </div>
                      </n-collapse-item>
                    </n-collapse>
                  </div>
                  <div v-else v-html="formatMessage(msg.content)"></div>
                </div>
              </div>
              <div class="message-time">{{ msg.timestamp ? formatTimestamp(msg.timestamp) : '' }}</div>
            </div>
            
            <n-alert v-if="connectionError" type="warning" closable style="margin-top: 16px;">
              {{ connectionError }}
            </n-alert>
          </div>
          
          <div class="chat-input">
            <n-input
              v-model:value="inputMessage"
              type="textarea"
              placeholder="发送消息给AI助手..."
              :autosize="{ minRows: 1, maxRows: 4 }"
              @keydown.enter.prevent="handleEnterPress"
            />
            <n-button 
              type="primary" 
              circle 
              :disabled="isLoading || !inputMessage.trim()" 
              @click="sendMessage()"
            >
              <template #icon>
                <icon-send />
              </template>
            </n-button>
          </div>
        </div>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { 
  NDrawer, 
  NDrawerContent, 
  NButton, 
  NInput, 
  NSkeleton,
  NBadge,
  NAlert,
  NTooltip,
  NIcon,
  useMessage,
  NPopover,
  NCollapse,
  NCollapseItem,
  NSpin
} from 'naive-ui';
import { sendMessageToAssistant } from '@/services/api/assistant';
import { useAIAssistantWebSocket } from '@/services/websocket/ai-assistant';
import IconAssistant from '@/components/icons/IconAssistant.vue';
import IconUser from '@/components/icons/IconUser.vue';
import IconSend from '@/components/icons/IconSend.vue';
import { WarningOutlined, QuestionCircleOutlined } from '@vicons/antd';

// 定义消息类型
interface Message {
  role: 'user' | 'assistant';
  content: string;
  loading?: boolean;
  is_thinking?: boolean;
  timestamp?: string;
  error?: string;
  details?: Record<string, any> | string | null;
}

const isOpen = ref(false);
const inputMessage = ref('');
const messages = ref<Message[]>([]);
const isLoading = ref(false);
const chatContainerRef = ref<HTMLElement | null>(null);
const message = useMessage();

// 初始化WebSocket AI助手服务
const { 
  isConnected, 
  connectionError, 
  isProcessing, 
  latestResponse, 
  latestSuggestions,
  sendQuery, 
  requestSuggestions,
  reconnect
} = useAIAssistantWebSocket();

// 预设建议问题
const suggestions = ref([
  '如何使用量化考核功能？',
  '怎样导出统计数据？',
  '系统支持哪些图表类型？',
  '如何管理班级和学生？'
]);

// 手动重连
const handleReconnect = () => {
  message.info('正在尝试重新连接AI助手服务...');
  
  // 先检查网络连接
  if (!navigator.onLine) {
    message.error('网络连接已断开，请检查您的网络连接后重试');
    return;
  }

  // 清除现有错误状态
  connectionError.value = null;
  
  // 执行重连
  reconnect();
  
  // 设置延时检查
  setTimeout(() => {
    if (!isConnected.value) {
      message.warning('连接尝试未成功，可能是服务器暂时不可用，请稍后再试');
    }
  }, 3000);
};

// 监听WebSocket连接状态
watch(connectionError, (error) => {
  if (error) {
    message.error(`AI助手连接错误: ${error}`);
  }
});

// 监听AI助手响应
watch(latestResponse, (response) => {
  if (!response) return;
  
  console.log('处理AI助手响应:', response);
  
  if (messages.value.length > 0) {
    // 找到最后一条助手消息
    const lastAssistantMessageIndex = [...messages.value].reverse().findIndex(
      msg => msg.role === 'assistant' && msg.loading
    );
    
    if (lastAssistantMessageIndex !== -1) {
      const actualIndex = messages.value.length - 1 - lastAssistantMessageIndex;
      
      // 检查是否包含特定错误
      let content = response.response || '';
      let shouldWarn = false;
      let errorDetails: string | undefined = undefined;
      
      if (response.error) {
        // 根据不同错误类型提供友好消息
        if (response.error.includes("datetime") || response.error.includes("JSON serializable")) {
          content = "由于服务器处理问题，无法正确显示完整回复。请稍后再试或联系管理员。";
          shouldWarn = true;
          errorDetails = response.error;
        } else if (response.error.includes("connection")) {
          content = "AI服务连接失败。可能是服务暂时不可用，请稍后再试。";
          shouldWarn = true;
          errorDetails = response.error;
        } else {
          // 一般错误处理
          content = response.response || "服务器处理请求时出现问题";
          shouldWarn = true;
          errorDetails = response.error;
        }
      }
      
      // 如果没有内容但有错误，确保显示一些内容
      if (!content && errorDetails) {
        content = "处理请求时出现问题，请稍后再试";
      }
      
      // 更新助手消息
      messages.value[actualIndex] = {
        role: 'assistant',
        content: content || "服务器未返回内容，请稍后再试",
        error: errorDetails,
        timestamp: new Date().toISOString()
      };
      
      if (shouldWarn) {
        console.warn('AI助手响应中包含错误:', errorDetails);
        message.warning('AI助手处理查询时遇到问题');
      }
      
      scrollToBottom();
    } else {
      console.warn('未找到带有loading状态的助手消息');
    }
  } else {
    console.warn('消息列表为空，无法更新助手回复');
  }
});

// 监听AI助手建议
watch(latestSuggestions, (newSuggestions) => {
  if (newSuggestions && newSuggestions.length > 0) {
    suggestions.value = newSuggestions;
  }
});

// 监听处理状态变化
watch(isProcessing, (processing) => {
  isLoading.value = processing;
});

// 切换助手显示状态
const toggleAssistant = () => {
  isOpen.value = !isOpen.value;
  
  // 当助手打开时，请求建议
  if (isOpen.value) {
    if (isConnected.value) {
      requestSuggestions();
    } else {
      // 尝试重连
      reconnect();
    }
  }
};

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (chatContainerRef.value) {
    chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight;
  }
};

// 处理Enter键按下
const handleEnterPress = (e: KeyboardEvent) => {
  // 如果是单纯的回车键，发送消息
  if (!e.shiftKey && !e.ctrlKey && !e.altKey) {
    sendMessage();
  }
};

// 将文本中的换行符转换为格式化的HTML
const formatMessage = (text: string) => {
  if (!text) return '';
  
  // 处理代码块
  text = text.replace(/```([^`]+)```/g, '<pre class="code-block">$1</pre>');
  
  // 处理行内代码
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // 处理列表 (匹配以 - 或 * 或 数字+点 开头的行)
  text = text.replace(/^([\s]*)[*-] (.+)$/gm, '$1<li>$2</li>');
  text = text.replace(/^([\s]*)\d+\. (.+)$/gm, '$1<li>$2</li>');
  
  // 将连续的列表项包装在ul或ol中
  let inList = false;
  const lines = text.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const currentLine = lines[i];
    const nextLine = i < lines.length - 1 ? lines[i + 1] : '';
    
    if (currentLine.includes('<li>') && !inList) {
      lines[i] = '<ul>' + currentLine;
      inList = true;
    } else if (!nextLine.includes('<li>') && inList) {
      lines[i] = currentLine + '</ul>';
      inList = false;
    }
  }
  text = lines.join('\n');
  
  // 处理引用块
  text = text.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
  
  // 处理段落：将连续的换行符转换为段落
  return text
    // 先替换连续多个换行为特殊标记
    .replace(/\n{2,}/g, '<paragraph-break>')
    // 替换单个换行为<br>（除非在列表或代码块中）
    .replace(/\n(?![<\/](?:ul|ol|pre|code|blockquote))/g, '<br>')
    // 将段落标记转换为实际的段落标签
    .replace(/<paragraph-break>/g, '</p><p>')
    // 包装整个内容在段落标签中
    .replace(/^(.+(?:\n.+)*)$/, '<p>$1</p>');
};

// 添加全局样式
const globalStyle = document.createElement('style');
globalStyle.innerHTML = `
  .ai-message-content p {
    margin: 0.5em 0;
  }
  .ai-message-content p:first-child {
    margin-top: 0;
  }
  .ai-message-content p:last-child {
    margin-bottom: 0;
  }
  
  /* 列表样式 */
  .ai-message-content ul, 
  .ai-message-content ol {
    margin: 0.5em 0;
    padding-left: 1.5em;
  }
  
  .ai-message-content li {
    margin-bottom: 0.25em;
  }
  
  .ai-message-content li:last-child {
    margin-bottom: 0;
  }
  
  /* 代码块 */
  .ai-message-content code {
    background-color: #f5f5f5;
    padding: 0.1em 0.4em;
    border-radius: 3px;
    font-family: monospace;
    font-size: 0.9em;
  }
  
  /* 引用块 */
  .ai-message-content blockquote {
    border-left: 3px solid #ddd;
    margin: 0.5em 0;
    padding-left: 1em;
    color: #666;
  }
`;
document.head.appendChild(globalStyle);

// 发送消息
const sendMessage = async (text?: string) => {
  const content = text || inputMessage.value.trim();
  if (!content || isLoading.value) return;
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content
  });
  
  // 清空输入框
  if (!text) {
    inputMessage.value = '';
  }
  
  // 添加助手正在加载的消息
  messages.value.push({
    role: 'assistant',
    content: '',
    loading: true
  });
  
  scrollToBottom();
  
  // 优先使用WebSocket发送查询
  if (isConnected.value) {
    sendQuery(content);
  } else {
    // 回退到HTTP API
    isLoading.value = true;
    
    try {
      // 发送API请求
      const response = await sendMessageToAssistant(content);
      
      // 更新助手消息
      const lastIndex = messages.value.length - 1;
      messages.value[lastIndex] = {
        role: 'assistant',
        content: response.content
      };
    } catch (error) {
      // 移除加载消息
      messages.value.pop();
      
      // 显示错误消息
      message.error('发送消息失败，请稍后重试');
      console.error('Failed to send message to assistant:', error);
    } finally {
      isLoading.value = false;
      scrollToBottom();
    }
  }
};

// 清空对话
const clearChat = () => {
  messages.value = [];
};

// 当抽屉打开时滚动到底部
watch(isOpen, (value) => {
  if (value) {
    scrollToBottom();
  }
});

// 保存和恢复聊天记录
onMounted(() => {
  const savedMessages = localStorage.getItem('ai-assistant-messages');
  if (savedMessages) {
    try {
      messages.value = JSON.parse(savedMessages);
    } catch (e) {
      console.error('Failed to parse saved messages:', e);
    }
  }
});

// 监听消息变化，保存到本地存储
watch(messages, (value) => {
  // 过滤掉加载中的消息，只保存完成的消息
  const messagesToSave = value.filter(msg => !msg.loading);
  localStorage.setItem('ai-assistant-messages', JSON.stringify(messagesToSave));
}, { deep: true });

// 判断是否为错误消息
const isErrorMessage = (msg: Message) => {
  return msg.content && (
    msg.content.includes('错误') || 
    msg.content.includes('服务器') && msg.content.includes('出错') ||
    msg.content.includes('序列化')
  );
};

// 判断是否为datetime序列化错误
const isDatetimeError = (msg: Message) => {
  return msg.content && (
    msg.content.includes('datetime序列化') || 
    msg.content.includes('JSON serializable')
  );
};

// 添加时间戳格式化函数
const formatTimestamp = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    if (isNaN(date.getTime())) {
      return '';
    }
    
    // 格式为：HH:MM:SS 或 YYYY-MM-DD HH:MM:SS
    const today = new Date();
    const isToday = date.getDate() === today.getDate() && 
                    date.getMonth() === today.getMonth() && 
                    date.getFullYear() === today.getFullYear();
                    
    if (isToday) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleString([], { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit', 
        minute: '2-digit'
      });
    }
  } catch (e) {
    console.error('时间戳格式化错误:', e);
    return '';
  }
};
</script>

<style scoped>
.ai-assistant {
  position: relative;
}

.assistant-toggle {
  cursor: pointer;
}

.assistant-toggle button.active {
  color: var(--primary-color);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 10px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.status-text {
  margin-right: 4px;
}

.assistant-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message,
.message-item {
  display: flex;
  gap: 8px;
}

.welcome-message {
  margin-bottom: 16px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.assistant-avatar,
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.assistant-avatar {
  background-color: var(--primary-color, #18a058);
  color: white;
}

.user-avatar {
  background-color: #e6f4ff;
  color: #2080f0;
}

.message-content {
  padding: 12px;
  border-radius: 8px;
  max-width: 80%;
  overflow-wrap: break-word;
  word-break: break-word;
}

.message-item.assistant .message-content {
  background-color: #f5f5f5;
}

.message-item.user .message-content {
  background-color: #e6f4ff;
  margin-right: 8px;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.chat-input {
  padding: 12px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.chat-input :deep(.n-input) {
  flex: 1;
}

.message-content.error {
  background-color: #fff2f0;
  border-left: 4px solid #ff4d4f;
  padding-left: 12px;
}

.error-icon {
  color: #ff4d4f;
  margin-right: 8px;
}

.datetime-error {
  color: #cf1322;
}

.fix-suggestion {
  background-color: #f8f8f8;
  padding: 12px;
  border-radius: 4px;
  font-size: 0.9em;
}

/* 代码块样式 */
.message-content pre.code-block {
  background-color: #292c2e;
  color: #fff;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.85em;
  margin: 0.75em 0;
  white-space: pre-wrap;
}
</style> 