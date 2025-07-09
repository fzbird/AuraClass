<template>
  <div class="flex flex-col h-full">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">AI 助手</h1>
    </div>
    
    <n-card class="flex-1 flex flex-col" content-style="height: 100%;">
      <div class="flex h-full">
        <!-- 左侧历史记录和分析功能切换 -->
        <div class="w-64 border-r border-gray-200 pr-4 h-full flex flex-col">
          <n-tabs type="line" :default-value="activeTab" @update:value="handleTabChange">
            <n-tab-pane name="history" tab="会话历史">
              <div class="mb-4">
                <n-button block type="primary" @click="createNewConversation">
                  <template #icon>
                    <n-icon><plus-outlined /></n-icon>
                  </template>
                  新对话
                </n-button>
              </div>
              
              <div class="mb-2 text-sm text-gray-500">历史对话</div>
              
              <div v-if="historicalConversations.length === 0" class="text-center text-gray-400 py-4">
                无历史对话
              </div>
              
              <div v-else>
                <!-- 历史会话折叠控制 -->
                <div class="flex justify-between items-center mb-2">
                  <span class="text-xs text-gray-500">最近 {{ historicalConversations.length }} 条会话</span>
                  <n-button text size="small" style="margin-left: 8px;" @click="isHistoryExpanded = !isHistoryExpanded">
                    {{ isHistoryExpanded ? '收起' : '展开' }}
                  </n-button>
                </div>
                
                <n-collapse v-if="isHistoryExpanded" :default-expanded-names="defaultExpandedNames"
                  @update:expanded-names="handleExpandChange">
                  <n-collapse-item v-for="conv in historicalConversations" :key="conv.id" :name="conv.id"
                    :title="conv.title || '未命名对话'">
                    <template #header>
                      <div class="flex justify-between items-center w-full pr-4">
                  <div class="truncate font-medium">{{ conv.title || '未命名对话' }}</div>
                        <div class="text-xs text-gray-500 whitespace-nowrap ml-2">{{ formatDate(conv.updated_at) }}
                        </div>
                </div>
                    </template>
                    
                    <div class="conversation-messages pb-2">
                      <div v-if="loadingMessages.has(conv.id!)" class="py-2 text-center">
                        <n-spin size="small" />
                        <span class="ml-2 text-sm">加载消息中...</span>
                      </div>
                      <div 
                        v-else-if="conversationMessages.has(conv.id!) && (conversationMessages.get(conv.id!) || []).length > 0"
                        class="max-h-60 overflow-y-auto py-2">
                        <!-- 使用与当前会话相同的消息气泡样式 -->
                        <n-space vertical size="medium">
                          <template v-for="(msg, msgIndex) in (conversationMessages.get(conv.id!) || [])"
                            :key="msgIndex">
                            <MessageBubble :message="msg" :is-user="isUserMessage(msg.role)" :compact="true"
                              @copy-to-input="copyToInput" @delete="confirmDeleteMessage" />
                          </template>
                        </n-space>
                      </div>
                      <div v-else-if="!conversationMessages.has(conv.id!)" class="py-2 text-center">
                        <n-button text @click="selectConversation(conv)">加载消息</n-button>
                      </div>
                      <div v-else class="py-2 text-center text-gray-400">
                        无消息记录
                      </div>
                    </div>
                  </n-collapse-item>
                </n-collapse>
              </div>
            </n-tab-pane>
            
            <n-tab-pane name="analysis" tab="数据分析">
              <div class="mb-4">
                <n-select v-model:value="analysisContext" :options="contextOptions" placeholder="选择分析上下文" />
              </div>
              
              <div v-if="analysisContext" class="mb-2 text-sm text-gray-500">
                {{ getContextTitle(analysisContext) }}
              </div>
              
              <div v-if="analysisContext === 'student'" class="mb-4">
                <n-select v-model:value="analysisContextId" :options="studentOptions" placeholder="选择学生" filterable
                  clearable />
              </div>
              
              <div v-else-if="analysisContext === 'class'" class="mb-4">
                <n-select v-model:value="analysisContextId" :options="classOptions" placeholder="选择班级" filterable
                  clearable />
              </div>
              
              <n-button block type="primary" :disabled="!isAnalysisValid" @click="generateAnalysis">
                <template #icon>
                  <n-icon><line-chart-outlined /></n-icon>
                </template>
                生成分析
              </n-button>
            </n-tab-pane>
          </n-tabs>
        </div>
        
        <!-- 右侧聊天区域或分析结果 -->
        <div class="flex-1 flex flex-col ml-4 h-full">
          <!-- 历史会话与当前会话之间的分隔线 -->
          <div v-if="activeTab === 'history'" class="w-full border-b-2 border-gray-200 mb-4 pb-1">
            <n-divider dashed>当前会话</n-divider>
          </div>
          <template v-if="activeTab === 'history'">
            <!-- 当前会话标题 -->
            <div v-if="currentConversation" class="flex justify-between items-center mb-3 pb-2 border-b">
              <h2 class="text-lg font-medium">{{ currentConversation.title || '未命名对话' }}</h2>
              <div class="text-sm text-gray-500">{{ formatDate(currentConversation.updated_at) }}</div>
            </div>
            
            <!-- 消息历史 -->
            <div ref="messagesContainerRef" class="flex-1 overflow-y-auto conversation-container"
              style="padding-bottom: 40px !important;">
              <!-- 无对话提示 -->
              <div v-if="!currentConversation" class="h-full flex flex-col items-center justify-center text-gray-400">
                <n-icon size="48" class="mb-4">
                  <message-outlined />
                </n-icon>
                <p class="mb-2">欢迎使用 AI 助手</p>
                <p class="text-sm">你可以询问关于班级管理、统计数据等问题</p>
              </div>
              
              <!-- 消息列表 -->
              <template v-else>
                <div v-if="isLoadingCurrentMessages" class="flex justify-center items-center py-4">
                  <n-spin size="small" />
                  <span class="ml-2">加载消息中...</span>
                </div>
                <template v-else-if="currentMessages.length > 0">
                  <!-- 消息列表容器 -->
                  <n-space vertical size="large" style="width: 100%">
                    <template v-for="(msg, index) in currentMessages" :key="msg.id || index">
                      <MessageBubble :message="msg" :is-user="isUserMessage(msg.role)" :compact="false"
                        @copy-to-input="copyToInput" @delete="confirmDeleteMessage" />
                    </template>
                  </n-space>
                </template>
                <div v-else class="flex justify-center items-center py-4 text-gray-400">
                  暂无消息，请开始新的对话
                </div>
              </template>
            </div>
            
            <!-- 修改输入框容器，使用内联样式确保样式优先级 -->
            <div
              style="margin-top: 30px !important; padding-top: 20px !important; border-top: 2px solid #e5e7eb !important;"
              class="message-input-container">
              <!-- 添加文件预览区域 -->
              <div v-if="uploadedFiles.length > 0" class="uploaded-files-preview">
                <div v-for="(file, index) in uploadedFiles" :key="file.id" class="uploaded-file-item">
                  <!-- 图片预览 -->
                  <div v-if="file.type.startsWith('image/')" class="image-preview">
                    <n-spin v-if="file.loading" size="small" />
                    <img v-else :src="file.url" :alt="file.name" />
                  </div>
                  <!-- 普通文件预览 -->
                  <div v-else class="file-preview">
                    <n-spin v-if="file.loading" size="small" />
                    <template v-else>
                      <n-icon size="24" class="file-icon">
                        <component :is="getFileTypeIcon(file.type)" />
                      </n-icon>
                      <span class="file-name">{{ file.name }}</span>
                      <span class="file-size">{{ formatFileSize(file.size) }}</span>
                    </template>
                  </div>
                  <!-- 移除按钮 -->
                  <n-button circle quaternary size="small" class="remove-file-btn" @click="removeFile(index)">
                    <template #icon>
                      <n-icon><close-outlined /></n-icon>
                    </template>
                  </n-button>
                </div>
              </div>

              <!-- 输入区域容器修复 -->
              <div class="input-area-container">
                <!-- 文件上传按钮 -->
                <div class="file-upload-button">
                  <n-tooltip trigger="hover" placement="top" :show-arrow="true">
                    <template #trigger>
                      <n-upload ref="uploadRef" :show-file-list="false" :max="5" :multiple="true" 
                        @change="handleFileChange" :before-upload="beforeUpload"
                        @update:file-list="handleUpdateFileList" :disabled="isProcessing"
                        accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt" :default-upload="false">
                        <n-button circle :disabled="isProcessing">
                          <template #icon>
                            <n-icon><attachment-outlined /></n-icon>
                          </template>
                        </n-button>
                      </n-upload>
                    </template>
                    上传文件或图片
                  </n-tooltip>
                </div>

                <n-input v-model:value="inputMessage" type="textarea" placeholder="输入你的问题..."
                :autosize="{ minRows: 1, maxRows: 4 }"
                  @keydown.enter.exact.prevent="handleEnterKey"
                  class="flex-1" />

                <n-button circle type="primary" :disabled="!inputMessage && uploadedFiles.length === 0 || isProcessing"
                  @click="handleSendClick" class="send-button">
                    <template #icon>
                      <n-icon>
                        <send-outlined />
                      </n-icon>
                    </template>
                  </n-button>
              </div>
              
              <!-- 思考模式控制和按键提示放在同一行 -->
              <div class="input-controls-row">
                <!-- 思考模式控制 -->
                <div class="think-mode-control">
                  <n-tag type="success" size="small" class="mr-2">思考模式</n-tag>
                  <n-switch v-model:value="useThinkMode" @update:value="handleThinkModeToggle" size="small">
                    <template #checked>开启</template>
                    <template #unchecked>关闭</template>
                  </n-switch>
                </div>
                
                <!-- 按键提示 -->
                <div class="keyboard-tips">
                <span>按 Enter 发送消息，Shift + Enter 换行</span>
                </div>
              </div>
              
              <!-- 模型设置 -->
              <div class="mt-4 pt-4 border-t border-gray-200 flex items-center">
                <div class="flex items-center">
                  <n-tag type="info" size="medium" class="mr-2">{{ aiAssistantStore.aiModelSource }}</n-tag>
                  <n-switch v-model:value="useLocalOllama" @update:value="handleModelSourceChange" disabled>
                    <template #checked>本地 Ollama</template>
                    <template #unchecked>远程 API</template>
                  </n-switch>
                  <n-dropdown v-if="useLocalOllama" trigger="hover" :options="modelOptions" @select="handleModelSelect">
                    <n-button quaternary size="small" class="ml-2">
                      模型: {{ selectedModel }}
                      <template #icon>
                        <n-icon><down-outlined /></n-icon>
                      </template>
                    </n-button>
                  </n-dropdown>
                  
                  <n-tooltip trigger="hover" placement="top">
                    <template #trigger>
                      <n-icon class="ml-2 text-gray-500" size="16">
                        <question-outlined />
                      </n-icon>
                    </template>
                    已保存模型选择，下次使用时将自动应用
                  </n-tooltip>
                </div>
              </div>
            </div>
          </template>
          
          <template v-else-if="activeTab === 'analysis'">
            <!-- 分析结果 -->
            <div class="flex-1 overflow-y-auto pb-4">
              <div v-if="!showAnalysisResult" class="h-full flex flex-col items-center justify-center text-gray-400">
                <n-icon size="48" class="mb-4">
                  <line-chart-outlined />
                </n-icon>
                <p class="mb-2">选择分析参数并点击"生成分析"</p>
                <p class="text-sm">AI 助手会为您提供智能数据分析和洞察</p>
              </div>
              
              <div v-else>
                <a-i-data-analysis ref="dataAnalysisRef" :title="analysisTitle" :context="analysisContext"
                  :context-id="analysisContextId" @insight-action="handleInsightAction" />
                
                <div class="mt-4">
                  <div class="flex items-center mb-2">
                    <div class="text-base font-medium">数据查询</div>
                  </div>
                  
                  <n-input v-model:value="queryInput" type="textarea" placeholder="用自然语言描述您想了解的数据，例如：'本月各班级量化项目统计对比'"
                    :autosize="{ minRows: 2, maxRows: 4 }">
                    <template #suffix>
                      <n-button circle type="primary" :disabled="!queryInput || isNaturalQueryLoading"
                        @click="handleNaturalLanguageQuery">
                        <template #icon>
                          <n-icon>
                            <search-outlined />
                          </n-icon>
                        </template>
                      </n-button>
                    </template>
                  </n-input>
                  
                  <div v-if="isNaturalQueryLoading" class="mt-2 flex items-center justify-center">
                    <n-spin size="small" />
                    <span class="ml-2 text-sm">分析数据中...</span>
                  </div>
                  
                  <div v-if="naturalQueryResult" class="mt-4 p-4 bg-gray-50 rounded-lg">
                    <div class="mb-2 font-medium">查询结果</div>
                    <div class="query-result">
                      <div v-if="naturalQueryResult.text" class="mb-3">
                        {{ naturalQueryResult.text }}
                      </div>
                      
                      <div v-if="naturalQueryResult.chart" class="h-60">
                        <component :is="naturalQueryResult.chart.type" :data="naturalQueryResult.chart.data"
                          :config="naturalQueryResult.chart.config" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </n-card>
  </div>

  <!-- Image Preview Modal -->
  <n-modal v-model:show="previewVisible" preset="card" style="width: auto; max-width: 90%;" :z-index="1000">
    <div class="image-preview-container">
      <img :src="previewImageUrl" class="preview-image" />
      <n-button circle tertiary class="close-preview-button" @click="closeImagePreview">
        <template #icon>
          <n-icon>
            <close-outlined />
          </n-icon>
        </template>
      </n-button>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, computed, onUnmounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { 
  NCard, NButton, NInput, NIcon, NSpin, useMessage, 
  NTabs, NTabPane, NSelect, NSpace, NCollapse, NCollapseItem,
  NAvatar, NTag, NDivider, NText, NSwitch, NDropdown,
  NModal, NPopconfirm, NUpload, NUploadTrigger, NTooltip, useDialog,
  type SelectOption,
  type UploadFileInfo
} from 'naive-ui';
import PlusOutlined from '@vicons/antd/es/PlusOutlined';
import MessageOutlined from '@vicons/antd/es/MessageOutlined';
import SendOutlined from '@vicons/antd/es/SendOutlined';
import LineChartOutlined from '@vicons/antd/es/LineChartOutlined';
import SearchOutlined from '@vicons/antd/es/SearchOutlined';
import UserOutlined from '@vicons/antd/es/UserOutlined';
import RobotOutlined from '@vicons/antd/es/RobotOutlined';
import DownOutlined from '@vicons/antd/es/DownOutlined';
import CopyOutlined from '@vicons/antd/es/CopyOutlined';
import DeleteOutlined from '@vicons/antd/es/DeleteOutlined';
import EditOutlined from '@vicons/antd/es/EditOutlined';
import QuestionOutlined from '@vicons/antd/es/QuestionOutlined';
import AttachmentOutlined from '@vicons/antd/es/PaperClipOutlined';
import FileOutlined from '@vicons/antd/es/FileOutlined';
import CloseOutlined from '@vicons/antd/es/CloseOutlined';
import FilePdfOutlined from '@vicons/antd/es/FilePdfOutlined';
import FileTextOutlined from '@vicons/antd/es/FileTextOutlined';
import FileExcelOutlined from '@vicons/antd/es/FileExcelOutlined';
import FileWordOutlined from '@vicons/antd/es/FileWordOutlined';
import PictureOutlined from '@vicons/antd/es/PictureOutlined';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import { useAIAssistantStore } from '@/stores/ai-assistant';
import { useUserStore } from '@/stores/user';
import MessageBubble from '@/components/business/MessageBubble.vue';
import AIDataAnalysis from '@/components/assistant/AIDataAnalysis.vue';
import { getNaturalLanguageQueryResult } from '@/services/api/assistant';
import {
  SimpleAreaChart,
  SimpleBarChart,
  SimplePieChart,
  SimpleLineChart
} from '@/components/business/charts';
import MarkdownIt from 'markdown-it';
import { getAvailableModels } from '@/services/api/ollama';
// 添加http导入
import http from '@/services/http';
import axios from 'axios';
import type { AIMessageResponse, UnifiedMessage } from '@/types/assistant';
import type { Message as StoreMessage } from '@/stores/ai-assistant';

// Initialize dayjs plugins
dayjs.extend(utc);
dayjs.extend(timezone);

// 使用非类型化变量
const mdLib: any = MarkdownIt;
const md = new mdLib({
  html: false,
  breaks: true,
  linkify: true
});

// 添加文件上传类型定义
interface UploadedFile {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  file?: File; // 添加file属性
  rawFile: File;
  loading?: boolean;
}

// 扩展AIDataAnalysis组件类型，确保refreshAnalysis方法可用
interface AIDataAnalysisInstance extends InstanceType<typeof AIDataAnalysis> {
  refreshAnalysis: () => void;
}

interface Conversation {
  id: number;
  title: string;
  updated_at: string;
}

// 本组件中的Message接口
interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  is_thinking?: boolean;
  conversation_id?: number;
  is_timeout_message?: boolean;
  processing_time?: number; // 确保是number类型
  _forceThinking?: boolean; // 添加强制标记，确保前端始终识别为思考中状态
  willBeReplaced?: boolean; // 添加状态标记，表示此消息即将被替换
  _originalAiMsgId?: number; // 保存原始AI消息ID
  _replacedAiContent?: boolean; // 标记消息内容已被替换
  is_completed?: boolean; // 添加完成标记，表示AI已完成回答
}

// 文件上传组件回调中使用的文件信息
interface UploadFile {
  id: string;
  name: string;
  status: string;
  percentage?: number;
  file: File;
}

const message = useMessage();
const dialog = useDialog();
const aiAssistantStore = useAIAssistantStore();
const userStore = useUserStore();

const conversations = ref<Conversation[]>([]);
const currentConversation = ref<Conversation | null>(null);
const messages = ref<Message[]>([]);
const inputMessage = ref('');
const isProcessing = ref(false);
const messagesContainerRef = ref<HTMLElement | null>(null);

// 分析功能
const activeTab = ref('history');
const analysisContext = ref('');
const analysisContextId = ref<string | number | undefined>(undefined);
const showAnalysisResult = ref(false);
const dataAnalysisRef = ref<AIDataAnalysisInstance | null>(null);
const naturalQueryResult = ref<any>(null);
const queryInput = ref('');
const isNaturalQueryLoading = ref(false);

// 上下文选项
const contextOptions = [
  { label: '全局', value: 'global' },
  { label: '学生', value: 'student' },
  { label: '班级', value: 'class' },
  { label: '量化项目', value: 'quant-item' },
  { label: '量化记录', value: 'record' }
];

// 模拟数据，实际项目中应该从API获取
const studentOptions = [
  { label: '张三', value: 1 },
  { label: '李四', value: 2 },
  { label: '王五', value: 3 }
];

const classOptions = [
  { label: '一年级一班', value: 1 },
  { label: '一年级二班', value: 2 },
  { label: '二年级一班', value: 3 }
];

// 创建带时区的ISO时间戳
const createTimestamp = (): string => {
  // 直接创建UTC时间戳，这是后端预期的格式
  // 但用于显示时会转换为上海时区
  return dayjs().utc().format('YYYY-MM-DDTHH:mm:ss.SSS[Z]');
};

// 获取当前时间的毫秒数（上海时区）
const getCurrentTimeMs = (): number => {
  return dayjs().tz('Asia/Shanghai').valueOf();
};

// 修改消息类型转换函数，确保处理processing_time
const convertMessageFormat = (msg: any): Message => {
  // 规范化处理时间
  let processingTime: number | undefined = undefined;
  if (msg.processing_time !== undefined) {
    // 确保处理时间是数字类型
    if (typeof msg.processing_time === 'string') {
      processingTime = parseFloat(msg.processing_time);
      if (isNaN(processingTime)) processingTime = undefined;
    } else {
      processingTime = msg.processing_time;
    }
  }
  
  return {
    id: msg.id || Date.now(),
    role: msg.role,
    content: msg.content || '',
    timestamp: msg.timestamp || createTimestamp(),
    conversation_id: msg.conversation_id || msg.conversationId,
    processing_time: processingTime,
    is_thinking: msg.is_thinking || false,
    is_timeout_message: msg.is_timeout_message || false
  };
};

// 修改conversationMessages的类型定义
const conversationMessages = ref<Map<number, Message[]>>(new Map());
const loadingMessages = ref<Set<number>>(new Set());
const thinkingMessageMap = ref(new Map()); // 临时ID -> 用户消息ID的映射

// 获取用户名
const userName = computed(() => {
  return userStore.user?.full_name || userStore.user?.username || '我';
});

// 计算属性：分析标题
const analysisTitle = computed(() => {
  if (!analysisContext.value) return 'AI 智能分析';
  
  if (analysisContext.value === 'global') return '全局数据分析';
  
  if (analysisContext.value === 'student') {
    const student = studentOptions.find(s => s.value === analysisContextId.value);
    return student ? `学生分析：${student.label}` : '学生分析';
  }
  
  if (analysisContext.value === 'class') {
    const cls = classOptions.find(c => c.value === analysisContextId.value);
    return cls ? `班级分析：${cls.label}` : '班级分析';
  }
  
  const contextMap: Record<string, string> = {
    'quant-item': '量化项目分析',
    'record': '量化记录分析'
  };
  
  return contextMap[analysisContext.value] || 'AI 智能分析';
});

// 检查分析参数是否有效
const isAnalysisValid = computed(() => {
  if (!analysisContext.value) return false;
  
  if (analysisContext.value === 'global') return true;
  
  if (analysisContext.value === 'student' || analysisContext.value === 'class') {
    return !!analysisContextId.value;
  }
  
  return true;
});

// 获取上下文标题
const getContextTitle = (context: string) => {
  const titleMap: Record<string, string> = {
    'global': '全局数据',
    'student': '学生数据',
    'class': '班级数据',
    'quant-item': '量化项目数据',
    'record': '量化记录数据'
  };
  
  return titleMap[context] || '';
};

// 处理标签切换
const handleTabChange = (tab: string) => {
  activeTab.value = tab;
  if (tab === 'analysis') {
    // 默认选择全局分析
    if (!analysisContext.value) {
      analysisContext.value = 'global';
    }
  }
};

// 生成分析
const generateAnalysis = () => {
  if (!isAnalysisValid.value) return;
  
  showAnalysisResult.value = true;
  // 刷新分析结果
  nextTick(() => {
    dataAnalysisRef.value?.refreshAnalysis();
  });
};

// 处理洞察操作
const handleInsightAction = (action: any) => {
  message.info(`执行操作: ${action.text}`);
  
  if (action.type === 'custom' && action.payload === 'query') {
    activeTab.value = 'analysis';
    queryInput.value = action.data || '';
    nextTick(() => {
      handleNaturalLanguageQuery();
    });
  }
};

// 自然语言查询
const handleNaturalLanguageQuery = async () => {
  if (!queryInput.value || isNaturalQueryLoading.value) return;
  
  isNaturalQueryLoading.value = true;
  naturalQueryResult.value = null;
  
  try {
    const result = await getNaturalLanguageQueryResult(
      queryInput.value,
      analysisContext.value === 'global' ? undefined : analysisContext.value
    );
    
    naturalQueryResult.value = result;
  } catch (error) {
    console.error('Failed to process natural language query:', error);
    message.error('处理数据查询失败');
  } finally {
    isNaturalQueryLoading.value = false;
  }
};

// 历史会话计算属性（按ID倒序排序且排除当前会话，最多显示10条）
const historicalConversations = computed(() => {
  if (!conversations.value.length) return [];
  
  return conversations.value
    .filter(conv => !currentConversation.value || conv.id !== currentConversation.value.id)
    .sort((a, b) => b.id - a.id)
    .slice(0, 10); // 限制最多显示10条
});

// 格式化时间
const formatDate = (timestamp: string): string => {
  // 如果没有时间戳，则返回当前时间
  if (!timestamp) {
    console.warn('格式化时间收到空时间戳，使用当前时间代替');
    return dayjs().tz('Asia/Shanghai').format('YYYY/MM/DD HH:mm:ss');
  }
  
  try {
    // 检查是否是ISO格式时间（含有T字符）
    const isIsoFormat = typeof timestamp === 'string' && timestamp.includes('T');
    
    // 如果是ISO格式，假设是UTC时间并转换；否则直接以本地时间解析
    const date = isIsoFormat
      ? dayjs.utc(timestamp).tz('Asia/Shanghai')
      : dayjs(timestamp).tz('Asia/Shanghai');
    
    // 检查是否有效日期
    if (!date.isValid()) {
      console.warn(`无效时间戳: ${timestamp}, 使用当前时间代替`);
      return dayjs().tz('Asia/Shanghai').format('YYYY/MM/DD HH:mm:ss');
    }
    
    // 调试输出
    console.log(`原始时间戳: ${timestamp}`);
    console.log(`格式化后上海时间: ${date.format('YYYY/MM/DD HH:mm:ss')} (时区: ${date.format('Z')})`);
    
    return date.format('YYYY/MM/DD HH:mm:ss');
  } catch (error) {
    console.error('格式化日期出错:', error, timestamp);
    return dayjs().tz('Asia/Shanghai').format('YYYY/MM/DD HH:mm:ss');
  }
};

// 添加一个更精确的辅助函数来判断文本是否需要Markdown处理
const isSimpleText = (text: string): boolean => {
  // 如果文本包含这些特殊字符，则认为需要Markdown处理
  const markdownIndicators = ['#', '```', '*', '_', '- ', '1. ', '[', '|', '\n'];
  
  // 如果文本为空，不能判断为简单文本
  if (!text || text.trim() === '') {
    return false;
  }
  
  return !markdownIndicators.some(indicator => text.includes(indicator)) && text.length < 200;
};

// 修改formatMarkdown函数
const formatMarkdown = (content: string): string => {
  if (isSimpleText(content)) {
    // 对简单文本，使用安全转义防止XSS
    const escapedText = content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
    return `<span class="simple-text">${escapedText}</span>`;
  }
  // 复杂文本使用markdown-it处理
  return md.render(content);
};

// 添加本地模型相关的状态
const useLocalOllama = ref(true);
const selectedModel = ref('gemma3:27b');
const availableModels = ref<string[]>(['gemma3:27b']);
const useThinkMode = ref(true); // 添加思考模式变量
const modelOptions = computed(() => {
  return availableModels.value.map(model => ({
    label: model,
    key: model
  }));
});

// 在data部分添加
const uploadedFiles = ref<UploadedFile[]>([]);
const uploadRef = ref<InstanceType<typeof NUpload> | null>(null);

// 添加hasUploadedFiles ref
const hasUploadedFiles = ref(false);

// Add missing ref for polling timer
const pollingTimer = ref<number | null>(null);
// Fix to use non-ref variable for thinkingMessage in function
let thinkingMessageLocal: Message | null = null;

// 在正确位置添加 chartInstances 变量
const chartInstances = ref<any[]>([]);

onMounted(async () => {
  await fetchConversations();
  if (conversations.value.length > 0) {
    // 选择最新的会话（按ID排序后的第一个）
    const sortedConversations = [...conversations.value].sort((a, b) => b.id - a.id);
    if (sortedConversations.length > 0) {
      const latestConversation = sortedConversations[0];
      await selectConversation(latestConversation);
      currentConversation.value = latestConversation;
    }
  }
  
  // 确保设置本地模型
  useLocalOllama.value = true;
  aiAssistantStore.toggleModelSource(true);
  
  // 初始化思考模式状态
  useThinkMode.value = true; // 默认开启
  aiAssistantStore.toggleThinkMode(true);
  
  // 从store获取已保存的模型设置
  selectedModel.value = aiAssistantStore.localModelName;
  
  // 获取Ollama的可用模型
  try {
    const models = await getAvailableModels();
    if (models.length > 0) {
      availableModels.value = models;
      
      // 检查保存的模型是否在可用列表中
      if (!models.includes(selectedModel.value)) {
        // 如果保存的模型不可用，则选择列表中第一个模型
        selectedModel.value = models[0];
        aiAssistantStore.setLocalModelName(models[0]);
      }
    }
  } catch (error) {
    console.error('获取Ollama模型列表失败:', error);
    message.error('无法获取可用的本地模型列表，将使用保存的模型');
  }
  
  // 添加文档点击事件监听器以处理思考内容的展开/折叠
  document.addEventListener('click', handleThinkToggleClick);
});

// 修改为正确使用onUnmounted钩子
onUnmounted(() => {
  console.log('AI助手页面卸载，执行资源清理...');
  
  // 清理所有定时器
  if (pollingTimer.value) {
    clearTimeout(pollingTimer.value);
    pollingTimer.value = null;
  }
  
  // 清理所有文件上传相关资源
  if (uploadRef.value) {
    try {
      uploadRef.value.clear();
    } catch (error) {
      console.error('清理文件上传组件失败:', error);
    }
  }
  
  // 清理所有上传文件的URL，避免内存泄漏
  uploadedFiles.value.forEach(file => {
    if (file.url && file.url.startsWith('blob:')) {
      URL.revokeObjectURL(file.url);
    }
  });
  uploadedFiles.value = [];
  
  // 安全地检查和清理图表实例
  try {
    // 在组件内查找所有图表元素并清理
    const chartElements = document.querySelectorAll('.chart-container');
    if (chartElements && chartElements.length > 0) {
      console.log(`尝试清理 ${chartElements.length} 个图表元素`);
      // 清理工作已完成
    }
  } catch (e) {
    console.error('清理图表元素失败:', e);
  }
  
  // 重置所有状态变量，确保不会影响其他页面
  conversationMessages.value.clear();
  loadingMessages.value.clear();
  thinkingMessageMap.value.clear();
  
  // 安全地停止所有正在进行的HTTP请求
  try {
    // 使用原生方法取消未完成的请求
    console.log('清理未完成的HTTP请求');
    // 清理工作已完成
  } catch (e) {
    console.error('中止HTTP请求失败:', e);
  }
  
  // 清理发送锁
  localStorage.removeItem(SENDING_LOCK_KEY);
  
  console.log('AI助手页面资源清理完成');
});

// 当前会话的消息
const currentMessages = computed(() => {
  if (!currentConversation.value) return [];
  return conversationMessages.value.get(currentConversation.value.id) || [];
});

// 是否正在加载当前会话的消息
const isLoadingCurrentMessages = computed(() => {
  if (!currentConversation.value) return false;
  return loadingMessages.value.has(currentConversation.value.id);
});

// 更新watch以监听currentMessages变化
watch(currentMessages, () => {
  scrollToBottom();
}, { deep: true });

const fetchConversations = async () => {
  try {
    const result = await aiAssistantStore.getConversations();
    conversations.value = result || [];
  } catch (error) {
    console.error('Failed to fetch conversations:', error);
    message.error('获取对话历史失败');
    conversations.value = [];
  }
};

const createNewConversation = async () => {
  try {
    const newConversation = await aiAssistantStore.createConversation();
    conversations.value.unshift(newConversation);
    selectConversation(newConversation);
  } catch (error) {
    console.error('Failed to create new conversation:', error);
    message.error('创建新对话失败');
  }
};

const selectConversation = async (conversation: Conversation) => {
  currentConversation.value = conversation;
  
  // 如果已经有消息，检查是否需要更新
  if (conversationMessages.value.has(conversation.id)) {
    // 确保消息按ID排序，并转换为本地Message类型
    const sortedMessages = [...conversationMessages.value.get(conversation.id) || []].map(convertMessageFormat).sort((a, b) => a.id - b.id);
    
    // 去重处理：保留每个ID只出现一次的消息
    const uniqueMessages = Array.from(
      new Map(sortedMessages.map(item => [item.id, item])).values()
    );
    
    conversationMessages.value.set(conversation.id, uniqueMessages);
    
    nextTick(() => {
      scrollToBottom();
    });
    return;
  }
  
  // 标记为正在加载
  loadingMessages.value.add(conversation.id);
  
  try {
    const result = await aiAssistantStore.getMessages(conversation.id);
    // 确保消息按ID排序，并转换为本地Message类型
    const sortedMessages = [...result].map(convertMessageFormat).sort((a, b) => a.id - b.id);
    
    // 去重处理：保留每个ID只出现一次的消息
    const uniqueMessages = Array.from(
      new Map(sortedMessages.map(item => [item.id, item])).values()
    );
    
    // 存储到映射中
    conversationMessages.value.set(conversation.id, uniqueMessages);
    // 滚动到底部
    nextTick(() => {
      scrollToBottom();
    });
  } catch (error) {
    console.error('Failed to fetch messages:', error);
    message.error('获取消息记录失败');
    // 设置为空数组，避免重复加载
    conversationMessages.value.set(conversation.id, []);
  } finally {
    // 移除加载标记
    loadingMessages.value.delete(conversation.id);
  }
};

// 处理文件上传前的检查
const beforeUpload = (data: { file: File }): boolean => {
  const { file } = data;
  const maxSize = 10 * 1024 * 1024; // 10MB
  
  // 检查文件大小
  if (file.size > maxSize) {
    message.error(`文件大小不能超过10MB`);
    return false;
  }
  
  // 检查文件数量
  if (uploadedFiles.value.length >= 5) {
    message.error('最多只能上传5个文件');
    return false;
  }
  
  // 检查文件类型
  const allowedTypes = [
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'application/pdf', 
    'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain'
  ];
  
  if (!allowedTypes.includes(file.type)) {
    message.warning(`不支持的文件类型: ${file.type}`);
    return false;
  }

  console.log('文件上传前检查通过:', file.name);
  return true;
};

// 处理文件列表更新
const handleUpdateFileList = (fileList: any[]) => {
  console.log('文件列表更新:', fileList);
};

// 处理文件变更
const handleFileChange = (fileInfo: any, options?: { file?: any }) => {
  console.log('文件列表类型:', typeof fileInfo, fileInfo);
  
  // 检查是否有直接的文件列表数组
  let fileList = Array.isArray(fileInfo) ? fileInfo : [];
  
  // 如果fileInfo是对象且包含fileList字段，优先使用它的fileList
  if (fileInfo && typeof fileInfo === 'object' && 'fileList' in fileInfo && Array.isArray(fileInfo.fileList)) {
    console.log('使用fileInfo.fileList作为文件列表数据源');
    fileList = fileInfo.fileList;
  }
  
  // 如果有file对象，直接处理
  if (fileInfo && typeof fileInfo === 'object' && 'file' in fileInfo) {
    const fileObj = fileInfo.file;
    console.log('从参数中发现文件对象:', fileObj.name || '未命名文件');
    processNewFile(fileObj);
    return;
  }
  
  // 如果通过options提供了file对象
  if (options && options.file) {
    console.log('从options中发现文件对象:', options.file.name || '未命名文件');
    processNewFile(options.file);
    return;
  }
  
  // 处理文件列表中的新文件
  if (fileList.length > 0) {
    const pendingFiles = fileList.filter(f => f.status === 'pending');
    if (pendingFiles.length > 0) {
      console.log('从文件列表中找到待处理文件:', pendingFiles.length);
      pendingFiles.forEach(file => {
        if (!uploadedFiles.value.some(existing => 
          existing.id === file.id || existing.name === file.name
        )) {
          processNewFile(file);
        }
      });
    }
    
    // 处理可能被删除的文件
    const removedFiles = uploadedFiles.value.filter(existing => 
      !fileList.some(file => file.id === existing.id || file.name === existing.name)
    );
    
    if (removedFiles.length > 0) {
      console.log('检测到已移除文件:', removedFiles.length);
      removedFiles.forEach(file => {
        const index = uploadedFiles.value.findIndex(f => f.id === file.id);
        if (index !== -1) {
          if (file.url && file.type.startsWith('image/')) {
            URL.revokeObjectURL(file.url);
          }
          uploadedFiles.value.splice(index, 1);
        }
      });
    }
  }
  
  // 更新上传的文件状态
  hasUploadedFiles.value = uploadedFiles.value.length > 0;
};

// 处理单个文件的辅助函数
const processNewFile = (file: any) => {
  try {
    console.log('处理新文件:', file.name);
    
    // 尽可能获取原始文件对象
    let fileObject = null;
    
    // 检查各种可能的文件属性路径
    if (file instanceof File) {
      fileObject = file;
    } else if (file.file instanceof File) {
      fileObject = file.file;
    } else if (file.rawFile instanceof File) {
      fileObject = file.rawFile;
    } else if (typeof file.file === 'object' && file.file !== null) {
      // 可能是嵌套的file对象，尝试通过类型判断
      if (file.file.type && typeof file.file.size === 'number') {
        fileObject = file.file;
      }
    }
    
    if (!fileObject) {
      console.warn('无法获取有效的文件对象，尝试获取替代信息', file);
      // 尝试创建模拟文件对象
      if (file.name && file.type) {
        console.log('使用文件元数据创建上传项');
        uploadedFiles.value.push({
          id: file.id || `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          name: file.name,
          type: file.type || 'application/octet-stream',
          size: file.size || 0,
          url: '',
          // 使用任意类型绕过类型检查，实际上这些文件不会被上传
          file: file as any,
          rawFile: file as any,
          loading: false // 直接设置为false，避免阻止发送
        });
        hasUploadedFiles.value = true;
      }
      return;
    }
    
    // 创建文件URL（如果是图片）
    let fileUrl = '';
    if (fileObject.type.startsWith('image/')) {
      fileUrl = URL.createObjectURL(fileObject);
    }
    
    // 添加到上传文件列表
    uploadedFiles.value.push({
      id: file.id || `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: fileObject.name,
      type: fileObject.type,
      size: fileObject.size,
      url: fileUrl,
      file: fileObject,
      rawFile: fileObject,
      loading: false // 立即设置为非加载状态，因为我们实际上不执行上传
    });
    
    // 更新UI状态
    hasUploadedFiles.value = true;
    
    console.log('文件处理成功:', fileObject.name);
  } catch (error) {
    console.error('处理文件时出错:', error, file);
  }
};

// 添加文件上传预览组件调试方法
const logUploadedFiles = () => {
  console.log('当前上传文件列表:', JSON.stringify(uploadedFiles.value.map(f => ({
    id: f.id,
    name: f.name,
    type: f.type,
    size: f.size,
    loading: f.loading,
    hasUrl: !!f.url
  }))));
};

// 修改uploadedFiles的监视器
watch(uploadedFiles, (newFiles) => {
  console.log(`上传文件数量变化: ${newFiles.length}`);
  logUploadedFiles();
}, { deep: true });

// 移除文件
const removeFile = (index: number) => {
  if (index >= 0 && index < uploadedFiles.value.length) {
    const fileToRemove = uploadedFiles.value[index];
    console.log(`移除文件: ${fileToRemove.name}`);
    uploadedFiles.value.splice(index, 1);
    message.success(`已移除文件: ${fileToRemove.name}`);
  } else {
    console.warn(`无效的文件索引: ${index}`);
  }
};

// 添加防抖处理
let sendMessageDebounceTimer: any = null;
// 添加全局发送标志（在多个组件实例间共享）
const SENDING_LOCK_KEY = 'ai_assistant_sending_lock';

// 处理Enter键
const handleEnterKey = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    // 阻止事件默认行为和冒泡
    // event.preventDefault();
    // event.stopPropagation();
    
    // 检查全局锁定状态，如果已在发送则直接返回
    if (isProcessing.value || localStorage.getItem(SENDING_LOCK_KEY)) {
      console.warn('已有消息正在发送，忽略回车键触发');
      return;
    }
    
    clearTimeout(sendMessageDebounceTimer);
    sendMessageDebounceTimer = setTimeout(() => {
      sendMessageWithFiles();
    }, 300);
  }
};

// 处理发送按钮点击
const handleSendClick = () => {
  // 检查全局锁定状态，如果已在发送则直接返回
  if (isProcessing.value || localStorage.getItem(SENDING_LOCK_KEY)) {
    console.warn('已有消息正在发送，忽略按钮点击');
    return;
  }
  
  clearTimeout(sendMessageDebounceTimer);
  sendMessageDebounceTimer = setTimeout(() => {
    sendMessageWithFiles();
  }, 300);
};

// 清理定时器
onUnmounted(() => {
  // 移除文档点击事件监听器
  document.removeEventListener('click', handleThinkToggleClick);
  
  // 清理发送消息防抖定时器
  clearTimeout(sendMessageDebounceTimer);
  
  // 确保清理锁
  localStorage.removeItem(SENDING_LOCK_KEY);

  // 清除轮询定时器
  if (pollingTimer.value) {
    clearTimeout(pollingTimer.value);
    pollingTimer.value = null;
  }
});

// 发送消息函数 - 统一处理有无文件的情况
const sendMessageWithFiles = async () => {
  const messageText = inputMessage.value.trim();
  
  // 验证消息内容
  if (!messageText && (!uploadedFiles.value || uploadedFiles.value.length === 0)) {
    return;
  }
  
  // 检查重复提交锁
  if (localStorage.getItem(SENDING_LOCK_KEY)) {
    const lockTime = parseInt(localStorage.getItem(SENDING_LOCK_KEY) || '0');
    if (getCurrentTimeMs() - lockTime < 5000) {
      console.log('存在发送锁，消息正在处理中');
      message.warning('消息正在处理中，请稍等');
      return;
    } else {
      // 清除过期的锁
      localStorage.removeItem(SENDING_LOCK_KEY);
    }
  }
  
  // 设置发送锁
  localStorage.setItem(SENDING_LOCK_KEY, getCurrentTimeMs().toString());
  isProcessing.value = true;
  
  // 清空输入框和文件列表
  inputMessage.value = '';
  
  // 如果没有对话，先创建一个
  if (!currentConversation.value) {
    try {
      const newConversation = await aiAssistantStore.createConversation();
      currentConversation.value = newConversation;
      conversations.value.push(newConversation);
      // 正确传递参数类型
      if (typeof selectConversation === 'function') {
        selectConversation(newConversation);
      } else {
        // 直接设置活动会话
        currentConversation.value = newConversation;
      }
    } catch (error) {
      console.error('创建对话失败:', error);
      message.error('创建对话失败，请稍后重试');
      isProcessing.value = false;
      localStorage.removeItem(SENDING_LOCK_KEY);
      return;
    }
  }
  
  // 生成临时消息ID
  const tempUserMsgId = getCurrentTimeMs();
  const tempAiMsgId = tempUserMsgId - 1;
  
  try {
    // 创建用户消息对象
    let userMessage = convertMessageFormat({
      id: tempUserMsgId,
      role: 'user',
      content: messageText,
      timestamp: createTimestamp()
    });
    
    // 如果开启了思考模式，添加思考中的消息
    let thinkingMessage: Message | null = null;
    
    // 获取当前会话消息
    const currentMessages = conversationMessages.value.get(currentConversation.value!.id) || [];
    
    // 记录思考消息创建时间，用于确保最小显示时间
    const thinkingStartTime = getCurrentTimeMs();
    
    if (useThinkMode.value) {
      // 生成思考中消息 - 添加明确的类型标记
      thinkingMessage = {
        id: tempAiMsgId,
        role: 'assistant' as const,
        content: '正在思考中...',
        timestamp: createTimestamp(),
        is_thinking: true,  // 明确设置思考中标志
        _forceThinking: true, // 添加强制标记，确保前端始终识别为思考中状态
        conversation_id: currentConversation.value!.id
      };
      
      console.log('创建思考中消息:', JSON.stringify(thinkingMessage));
      
      // 修改顺序：先添加用户消息，再添加思考中消息
      conversationMessages.value.set(
        currentConversation.value!.id,
        [...currentMessages, userMessage, thinkingMessage]
      );
      
      // 添加到加载中消息集合
      loadingMessages.value.add(tempAiMsgId);
      
      // 存储映射关系 - 思考中消息ID -> 用户消息ID
      thinkingMessageMap.value.set(tempAiMsgId, tempUserMsgId);
      
      // 保存全局引用，以便在轮询结束时能找到
      thinkingMessageLocal = thinkingMessage;
      
      // 最短思考显示时间
      const minThinkingDisplayTime = 3000; // 3秒
      
      // 设置最短思考时间控制，以确保用户能看到思考动画
      setTimeout(() => {
        // 检查是否已经收到AI回复
        const currentMsgs = conversationMessages.value.get(currentConversation.value!.id) || [];
        const stillThinking = currentMsgs.some(m => m.id === tempAiMsgId && (m.is_thinking || (m as any)._forceThinking));
        
        if (stillThinking) {
          console.log(`思考中消息(ID:${tempAiMsgId})已显示${minThinkingDisplayTime/1000}秒，但尚未收到AI回复，继续等待`);
        }
        
        // 无论是否收到回复，都允许发送新消息
        isProcessing.value = false;
      }, minThinkingDisplayTime);
    } else {
      // 非思考模式，只添加用户消息
      conversationMessages.value.set(
        currentConversation.value!.id,
        [...currentMessages, userMessage]
      );
    }
    
    // 滚动到底部
    scrollToBottom();
    
    // 实际发送消息
    let response: any = null; // Use explicit any type
    let errorOccurred = false;
    const conversationId = currentConversation.value!.id;
    
    try {
      // 选择发送方式：文件或纯文本
      if (uploadedFiles.value && uploadedFiles.value.length > 0) {
        // 有文件，使用FormData方式发送
        const fileArray = uploadedFiles.value.map(file => file.rawFile);
        console.log('发送带文件的消息');
        response = await sendFormDataRequest(conversationId, messageText, fileArray);
        console.log('文件消息发送成功，响应:', response);
      } else {
        // 纯文本消息
        console.log('发送纯文本消息');
        response = await aiAssistantStore.sendMessage(conversationId, messageText);
        console.log('文本消息发送成功，响应:', response);
      }
      
      // 更新临时消息ID映射 - 用于后续替换
      if (response && response.id && thinkingMessage) {
        console.log(`创建临时消息映射: 思考中ID=${tempAiMsgId} -> 用户消息ID=${response.id}`);
        thinkingMessageMap.value.set(tempAiMsgId, response.id);
        
        // 获取当前消息列表以更新用户消息ID
        const messages = conversationMessages.value.get(conversationId) || [];
        const userMsgIndex = messages.findIndex((msg: any) => msg.id === tempUserMsgId);
        if (userMsgIndex >= 0) {
          messages[userMsgIndex] = {
            ...response,
            _tempId: tempUserMsgId // 保留临时ID用于调试
          };
          conversationMessages.value.set(conversationId, messages);
        }
      }
      
      // 计算思考动画已显示的时间
      const thinkingElapsedTime = getCurrentTimeMs() - thinkingStartTime;
      const minProcessingTime = 3000; // 最短思考时间（3秒）
      
      // 如果思考时间不足最短时间，延迟处理AI响应
      if (thinkingElapsedTime < minProcessingTime) {
        const delayTime = minProcessingTime - thinkingElapsedTime;
        console.log(`思考动画已显示${thinkingElapsedTime/1000}秒，不足${minProcessingTime/1000}秒，延迟${delayTime}ms处理AI响应`);
        
        setTimeout(() => {
          processAIResponse(response);
        }, delayTime);
      } else {
        console.log(`思考动画已显示${thinkingElapsedTime/1000}秒，已满足最短显示时间，立即处理AI响应`);
        processAIResponse(response);
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      message.error('发送消息失败，但消息已保存。正在尝试获取AI回复...');
      errorOccurred = true;
    }
    
    // 如果发送出错或响应中没有AI消息，尝试轮询获取AI回复
    if (errorOccurred || 
        !response || 
        (!response.ai_message && response.role !== 'assistant')) {
      console.log('没有立即获取到AI回复，开始轮询');
      // 启动轮询获取AI响应
      startPolling(conversationId, userMessage);
    }
    
    // 清空文件列表
    uploadedFiles.value = [];
    hasUploadedFiles.value = false;
  } catch (error) {
    console.error('发送消息过程中发生错误:', error);
    message.error('发送消息失败，请稍后重试');
  } finally {
    // 清理锁定状态 - 注意这里不要立即清除isProcessing.value,
    // 因为我们在setTimeout中有延迟清除
    localStorage.removeItem(SENDING_LOCK_KEY);
  }
};

// 处理超时响应
const handleTimeoutResponse = (aiMessageData: any) => {
  if (!currentConversation.value) return;
  
  // 获取当前会话的消息列表
  let messages = conversationMessages.value.get(currentConversation.value.id) || [];
  
  // 转换为正确类型
  const aiMessage = convertMessageFormat({
    ...aiMessageData,
    id: aiMessageData.id || Date.now(),
    conversation_id: aiMessageData.conversation_id || currentConversation.value.id,
    is_timeout_message: true
  });
  
  // 移除思考中消息，添加超时消息
  messages = messages.filter(msg => !msg.is_thinking);
  
  // 检查是否已经存在相同ID的消息
  const existingIndex = messages.findIndex(msg => msg.id === aiMessage.id);
  if (existingIndex !== -1) {
    // 更新现有消息
    messages[existingIndex] = aiMessage;
  } else {
    // 添加新消息
    messages.push(aiMessage);
  }
    
    // 更新消息列表
  conversationMessages.value.set(currentConversation.value.id, messages);
    
  // 显示提示
  message.info('AI响应超时，消息已发送，您可以稍后刷新查看回复');
    
  // 滚动到底部
    scrollToBottom();
};

// 更新消息列表 - 替换临时消息
const updateMessagesAfterSend = async (response: any) => {
  if (!currentConversation.value) return;
  
  console.log('处理发送响应:', response);
  
  // 检查是否存在超时响应
  if (response?.is_timeout && response?.ai_message) {
    console.log('检测到超时响应消息:', response.ai_message);
    // 调用超时处理函数
    handleTimeoutResponse(response.ai_message);
    return;
  }
  
  // 更新对话列表获取最新标题
  await fetchConversations();
  
  // 获取会话的最新消息
  console.log(`获取会话 ${currentConversation.value.id} 的最新消息`);
  const messages = await aiAssistantStore.getMessages(currentConversation.value.id);
  console.log(`获取到 ${messages?.length || 0} 条消息:`, messages);
  
  // 确保是数组并且有消息
  if (Array.isArray(messages) && messages.length > 0) {
    // 更新消息列表，丢弃临时ID的消息并转换类型
    const rawMessages = messages.filter(msg => 
      typeof msg.id === 'number' && msg.id > 0
    );
    
    // 转换为本地Message类型
    const realMessages = rawMessages.map(convertMessageFormat);
    
    console.log(`过滤后的有效消息: ${realMessages.length} 条`);
    
    // 排序消息 - 确保按照时间排序
    realMessages.sort((a, b) => {
      const timeA = new Date(a.timestamp).getTime();
      const timeB = new Date(b.timestamp).getTime();
      return timeA - timeB;
    });
    
    // 检查消息内容，记录日志
    realMessages.forEach((msg, index) => {
      console.log(`消息 ${index+1}: ID=${msg.id}, 角色=${msg.role}, 内容长度=${msg.content?.length || 0}`);
      if (msg.role === 'assistant' && (!msg.content || msg.content.trim() === '')) {
        console.warn(`检测到空的助手消息: ID=${msg.id}`);
      }
    });
    
    // 更新到状态
    conversationMessages.value.set(currentConversation.value.id, realMessages);
      } else {
    console.warn(`没有获取到消息或获取的消息为空`);
    // 尝试保留已有消息，只移除思考中状态
    const existingMessages = conversationMessages.value.get(currentConversation.value.id) || [];
    const filteredMessages = existingMessages.filter(msg => !msg.is_thinking);
    conversationMessages.value.set(currentConversation.value.id, filteredMessages);
  }
  
  // 滚动到底部
  scrollToBottom();
};

// 完全重写FormData请求函数
const sendFormDataRequest = async (conversationId: number, content: string, uploadFiles: File[] = []): Promise<any> => {
  console.log(`FormData请求 (尝试 1/2)`);
  
  const formData = new FormData();
  formData.append('content', content);
  formData.append('role', 'user');
  formData.append('useLocalModel', String(useLocalOllama.value));
  formData.append('modelName', selectedModel.value);
  formData.append('useThinkMode', String(useThinkMode.value));
  formData.append('waitForResponse', 'true'); // 等待AI响应完成
  
  // 添加上传文件
  if (uploadFiles && uploadFiles.length > 0) {
    uploadFiles.forEach(file => {
      formData.append('files', file);
    });
  }
  
  try {
    const requestId = `${getCurrentTimeMs()}-${Math.random().toString(36).substr(2, 9)}`;
    const response = await http.post(
      `/ai-assistant/conversations/${conversationId}/messages?t=${getCurrentTimeMs()}&request_id=${requestId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-Request-ID': requestId,
          'X-Timestamp': getCurrentTimeMs().toString()
        },
        timeout: 60000 // 60秒超时，等待AI响应
      }
    );
    
    console.log('FormData请求成功, 响应:', response);
    return response;
  } catch (error: any) {
    console.error('FormData请求失败:', error);
    
    // 检查是否是超时错误
    const isTimeout = error.code === 'ECONNABORTED' || 
                    error.message?.includes('timeout') || 
                    error.response?.status === 408;
    
    if (isTimeout) {
      console.log('FormData请求超时，尝试获取最新消息');
      
      // 尝试再次提交，但不等待AI响应
      try {
        console.log('尝试不等待AI响应的提交');
        const fallbackFormData = new FormData();
        fallbackFormData.append('content', content);
        fallbackFormData.append('role', 'user');
        fallbackFormData.append('useLocalModel', String(useLocalOllama.value));
        fallbackFormData.append('modelName', selectedModel.value);
        fallbackFormData.append('useThinkMode', String(useThinkMode.value));
        fallbackFormData.append('waitForResponse', 'false'); // 不等待AI响应
        
        // 添加上传文件
        if (uploadFiles && uploadFiles.length > 0) {
          uploadFiles.forEach(file => {
            fallbackFormData.append('files', file);
          });
        }
        
        // 发送不等待响应的请求
        const fallbackResponse = await http.post(
          `/ai-assistant/conversations/${conversationId}/messages?t=${getCurrentTimeMs()}&request_id=${getCurrentTimeMs()}-fallback`,
          fallbackFormData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            timeout: 10000 // 较短的超时
          }
        );
        
        console.log('不等待响应的请求成功:', fallbackResponse);
        
        // 创建超时消息
        const timeoutMessage = {
          id: getCurrentTimeMs(),
          role: 'assistant' as const,
          content: '**AI响应时间过长**，消息已发送，但未能在60秒内获得响应。AI会在后台继续处理，请稍后刷新对话查看回复。',
          timestamp: createTimestamp(),
          is_timeout_message: true,
          conversation_id: conversationId
        };
        
        return {
          ...fallbackResponse,
          is_timeout: true,
          ai_message: timeoutMessage
        };
      } catch (fallbackError) {
        console.error('后备请求失败:', fallbackError);
        throw new Error('消息已发送，但AI响应超时，请稍后刷新查看回复');
      }
    }
    
    // 非超时错误，直接抛出
    throw error;
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainerRef.value) {
      // Simply scroll to the bottom of the messages container
      // This will show the latest messages and position the input area in view
      messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight;
      
      // Focus on input field after scrolling
      setTimeout(() => {
        const inputElement = document.querySelector('.message-input-container textarea') as HTMLTextAreaElement;
        if (inputElement && !isProcessing.value) {
          // Only focus when not processing a message
          inputElement.focus();
        }
      }, 100);
    }
  });
};

// 修改defaultExpandedNames为ref而不是computed
const defaultExpandedNames = ref<number[]>([]);

// 处理折叠面板展开/收起事件
const handleExpandChange = async (expandedNames: number[]) => {
  if (expandedNames.length > 0) {
    // 获取当前展开的会话ID
    const expandedId = expandedNames[expandedNames.length - 1];
    const conversation = conversations.value.find(c => c.id === expandedId);
    
    if (conversation && expandedId !== currentConversation.value?.id) {
      console.log(`自动加载会话 ${expandedId} 的内容`);
      await selectConversation(conversation);
    }
  }
};

// 添加历史会话折叠状态变量
const isHistoryExpanded = ref(true); // 默认展开状态

// 处理模型来源切换
const handleModelSourceChange = (useLocal: boolean) => {
  useLocalOllama.value = useLocal;
  aiAssistantStore.toggleModelSource(useLocal);
  
  if (useLocal) {
    message.info(`已切换到本地Ollama模型: ${selectedModel.value}`);
  } else {
    message.info('已切换到远程API');
  }
};

// 处理模型选择
const handleModelSelect = (modelName: string) => {
  selectedModel.value = modelName;
  aiAssistantStore.setLocalModelName(modelName);
  message.success(`已选择模型: ${modelName}，下次将自动使用此模型`);
};

// 处理思考模式切换
const handleThinkModeToggle = (enabled: boolean) => {
  aiAssistantStore.toggleThinkMode(enabled);
  message.info(`已${enabled ? '开启' : '关闭'}思考模式`);
};

// 添加处理思考内容展开/折叠的事件处理函数
const handleThinkToggleClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  
  if (target && typeof target.closest === 'function') {
    const thinkWrapper = target.closest('.think-wrapper') as HTMLElement;
    
    if (thinkWrapper) {
      thinkWrapper.classList.toggle('expanded');
    }
  }
};

// 复制内容到剪贴板
const copyToClipboard = (text: string, copyType: 'full' | 'response' = 'full') => {
  let contentToCopy = text;
  
  // 如果只需要复制回答内容（不包含思考过程）
  if (copyType === 'response') {
    contentToCopy = removeThinkContent(text);
  }
  
  navigator.clipboard.writeText(contentToCopy).then(() => {
    message.success(copyType === 'full' ? '已复制全部内容到剪贴板' : '已复制回答内容到剪贴板');
  }).catch(err => {
    console.error('复制失败:', err);
    message.error('复制失败');
  });
};

// 复制内容到输入框
const copyToInput = (text: string) => {
  inputMessage.value = text;
  message.success('已复制到问题框');
  // 聚焦到输入框
  nextTick(() => {
    const inputElement = document.querySelector('textarea');
    if (inputElement) {
      inputElement.focus();
    }
  });
};

// 改进确认删除消息函数
const confirmDeleteMessage = async (messageId: number, conversationId?: number): Promise<void> => {
  // 检查conversationId是否有效
  if (!conversationId) {
    console.error('删除消息失败: 无效的会话ID');
    message.error('删除消息失败: 无效的会话ID');
    return;
  }

  // 创建确认对话框
  dialog.warning({
    title: '确认删除',
    content: '确定要删除这条消息吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        // 获取消息数据以用于错误显示
        const messagesMap = conversationMessages.value;
        const messages = messagesMap.get(conversationId) || [];
        const messageToDelete = messages.find((m: Message) => m.id === messageId);
        
        try {
          // 调用store方法删除消息
          await aiAssistantStore.deleteMessage(messageId, conversationId);
          
          // 更新本地UI
          const updatedMessages = messages.filter((m: Message) => m.id !== messageId);
          messagesMap.set(conversationId, updatedMessages);
          
          // 成功提示
          message.success('消息已删除');
        } catch (error: any) {
          // 错误处理与用户反馈
          console.error('删除消息失败:', error);
          
          // 更新本地UI，无论API调用成功与否
          const updatedMessages = messages.filter((m: Message) => m.id !== messageId);
          messagesMap.set(conversationId, updatedMessages);
          
          // 根据错误类型提供用户友好的反馈
          const errorStatus = error?.response?.status;
          
          if (errorStatus === 404) {
            message.warning('消息不存在或已被删除，界面已更新');
          } else if (errorStatus >= 400 && errorStatus < 500) {
            message.warning(`删除请求被拒绝(${errorStatus})，但消息已从界面移除`);
          } else if (errorStatus >= 500) {
            message.warning('服务器处理删除请求时出错，但消息已从界面移除');
          } else {
            message.warning('无法连接到服务器，但消息已从界面移除');
          }
          
          // 详细日志
          if (messageToDelete) {
            const contentPreview = messageToDelete.content.substring(0, 50) + 
                                  (messageToDelete.content.length > 50 ? '...' : '');
            console.warn(`已本地删除消息 ID: ${messageId}, 内容: "${contentPreview}"，错误:`, error);
          }
        }
      } catch (error) {
        console.error('删除消息操作失败:', error);
        message.error('删除操作失败，请刷新页面后重试');
      }
    }
  });
};

// 添加新的deleteMessage方法，由确认弹窗调用
const deleteMessage = async (messageId: number, conversationId: number): Promise<void> => {
  await confirmDeleteMessage(messageId, conversationId);
};

// 修改isUserMessage函数以提供更详细的调试信息
const isUserMessage = (role: string) => {
  const isUser = role === 'user';
  console.log(`检查消息角色: "${role}", 类型: ${typeof role}, 长度: ${role?.length}, 是否用户消息: ${isUser}`);
  return isUser;
};

// 添加思考内容提取和格式化函数
const extractThinkContent = (content: string): string => {
  const thinkContent = content.match(/<think>([\s\S]*?)<\/think>/);
  return thinkContent ? thinkContent[1].trim() : '';
};

const removeThinkContent = (content: string): string => {
  return content.replace(/<think>([\s\S]*?)<\/think>/, '').trim();
};

const formatThinkContent = (thinkContent: string): string => {
  return md.render(thinkContent);
};

const toggleThinkContent = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  
  if (target && typeof target.closest === 'function') {
    const thinkWrapper = target.closest('.think-wrapper') as HTMLElement;
    
    if (thinkWrapper) {
      thinkWrapper.classList.toggle('expanded');
    }
  }
};

// 处理文件类型显示的辅助函数
const getFileTypeIcon = (fileType: string) => {
  if (fileType.startsWith('image/')) return PictureOutlined;
  if (fileType.includes('pdf')) return FilePdfOutlined;
  if (fileType.includes('word') || fileType.includes('document')) return FileWordOutlined;
  if (fileType.includes('excel') || fileType.includes('sheet')) return FileExcelOutlined;
  if (fileType.includes('text')) return FileTextOutlined;
  return FileOutlined;
};

// 获取文件大小显示
const formatFileSize = (size: number): string => {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
};

// 添加新的处理函数用于解析消息中的图片引用
const processMessageWithImages = (content: string) => {
  if (!content) return { text: '', images: [] };

  // 检查消息是否包含图片引用
  const imageRefRegex = /\[图片:\s*([^\]]+)\]/g;
  let match;
  let processedContent = content;
  const images: { filename: string; path: string }[] = [];
  
  // 提取所有图片引用
  while ((match = imageRefRegex.exec(content)) !== null) {
    const filename = match[1].trim();
    
    // 构建图片路径 - 尝试多种可能的路径格式
    if (currentConversation.value && currentConversation.value.id && userStore.user) {
      // 1. 标准API路径
      const basePath = `/uploads/ai-assistant/user_${userStore.user.id}/conversation_${currentConversation.value.id}`;
      const encodedFilename = encodeURIComponent(filename);
      
      // 所有可能的路径格式 - 后端可能用不同格式存储
      const possiblePaths = [
        `${basePath}/${encodedFilename}`,
        `${basePath}/${filename}`,
        `/uploads/ai-assistant/user_${userStore.user.id}/conversation_${currentConversation.value.id}/${encodedFilename}`,
        `/ai-assistant/uploads/user_${userStore.user.id}/conversation_${currentConversation.value.id}/${encodedFilename}`
      ];

      console.log(`找到图片引用: ${filename}, 尝试路径: ${possiblePaths[0]}`);
      
      // 使用第一个路径，但在图片error事件中将尝试其他路径
      images.push({ 
        filename, 
        path: possiblePaths[0],
        // 添加其他可能的路径供error处理器使用
        possiblePaths
      } as any);
    }
  }
  
  // 如果找到图片引用，替换原始内容中的图片引用
  if (images.length > 0) {
    // 移除所有图片引用，将在UI中单独显示
    processedContent = processedContent.replace(imageRefRegex, '').trim();
    return { text: processedContent, images };
  }
  
  // 没有图片引用
  return { text: processedContent, images: [] };
};

// 添加图片预览状态
const previewVisible = ref(false);
const previewImageUrl = ref('');

// 添加打开图片预览的方法
const openImagePreview = (imageUrl: string) => {
  previewImageUrl.value = imageUrl;
  previewVisible.value = true;
};

// 添加关闭图片预览的方法
const closeImagePreview = () => {
  previewVisible.value = false;
};

// 修复handleImageError函数
const handleImageError = (event: Event, image: { 
  filename: string; 
  possiblePaths?: string[];
  path?: string;
}) => {
  console.warn(`图片加载失败: ${image.filename}, 尝试其他路径`);
  
  // 如果存在possiblePaths属性，则尝试其他可能的路径
  if (image.possiblePaths && Array.isArray(image.possiblePaths) && event.target instanceof HTMLImageElement) {
    // 查找当前路径的索引
    const currentIndex = image.possiblePaths.indexOf(event.target.src);
    
    // 如果找到，并且还有其他路径可以尝试
    if (currentIndex >= 0 && currentIndex < image.possiblePaths.length - 1) {
      // 尝试下一个路径
      const nextPath = image.possiblePaths[currentIndex + 1];
      console.log(`尝试下一个图片路径: ${nextPath}`);
      event.target.src = nextPath;
      return; // 不把onerror设为null，继续尝试其他路径
    }
  }
  
  // 没有更多路径可尝试，设置为默认占位图
  if (event.target instanceof HTMLImageElement) {
    console.log(`所有图片路径均失败，使用占位图`);
    event.target.src = '/assets/image-not-found.svg';
    event.target.classList.add('image-load-error');
    // 防止循环触发error事件
    event.target.onerror = null;
  }
};

// 准备FormData对象（包括处理文件）
const prepareFormData = (messageText: string, files: any[] = []) => {
  // 创建FormData对象
  const formData = new FormData();
  
  // 添加文本内容
  formData.append('content', messageText);
  formData.append('role', 'user');
  
  // 添加模型参数
  formData.append('useLocalModel', String(useLocalOllama.value));
  formData.append('modelName', selectedModel.value);
  formData.append('useThinkMode', String(useThinkMode.value));
  
  // 处理文件
  if (files && files.length > 0) {
    try {
      // 添加文件到FormData
      for (const file of files) {
        if (!file) continue;
        
        // 根据文件对象类型处理
        if (file instanceof File) {
          formData.append('files', file);
        } else if (file.file instanceof File) {
          formData.append('files', file.file, file.name);
        } else if (file.rawFile instanceof File) {
          formData.append('files', file.rawFile, file.name);
        }
      }
    } catch (error) {
      console.error('添加文件到FormData时出错:', error);
    }
  }
  
  return formData;
};

// 使用上面定义的函数发送带有文件的消息
const sendMessageWithFormData = async (messageText: string, files: any[] = []) => {
  try {
    // 准备FormData
    const formData = prepareFormData(messageText, files);
    
    // 发送请求 - 使用之前定义的重试函数，避免linter错误
    const url = `/ai-assistant/conversations/${currentConversation.value!.id}/messages?t=${getCurrentTimeMs()}`;
    const requestId = `${getCurrentTimeMs()}-${Math.random().toString(36).substring(2, 10)}`;
    
    // 使用完整的http请求处理，而不是依赖外部函数
    return await http.post(url, formData, {
      headers: {
        'X-Request-ID': requestId,
        'X-Timestamp': Date.now().toString()
      },
      timeout: 60000 // 60秒超时
    });
  } catch (error) {
    console.error('FormData方式发送消息失败:', error);
    throw error;
  }
};

// 优化的轮询函数 - 使用指数退避策略减少服务器负载
const startPolling = (conversationId: number, lastUserMessage: Message) => {
  let pollingCount = 0;
  const maxPolling = 10; // 增加轮询总次数，给后端处理时间更多
  let pollingInterval = 5000; // 初始5秒轮询间隔，增加到5秒，确保思考动画有足够显示时间
  const initialDelay = 5000; // 首次轮询前的延迟，给思考动画足够的显示时间
  const maxPollingInterval =  5000; // 最大10秒轮询间隔
  const backoffFactor = 1.5; // 指数退避因子
  let consecutiveFailures = 0; // 连续失败计数
  const maxConsecutiveFailures = 3; // 最大连续失败次数
  
  // 清除可能存在的之前的轮询定时器
  if (pollingTimer.value) {
    clearTimeout(pollingTimer.value);
    pollingTimer.value = null;
  }
  
  // 检查AI消息是否真正完成的内部函数
  const checkMessageCompleted = (aiMsg: any): boolean => {
    // 检查是否有明确的完成标志
    if (aiMsg.is_completed === true) {
      return true;
    }
    
    // 检查是否有处理时间（表示处理已完成）
    if (aiMsg.processing_time !== undefined && aiMsg.processing_time > 0) {
      return true;
    }
    
    // 检查内容是否看起来是完整的
    if (aiMsg.content && typeof aiMsg.content === 'string') {
      // 如果内容表明是临时状态，则不认为完成
      if (aiMsg.content.includes('正在处理') || 
          aiMsg.content.includes('思考中') ||
          aiMsg.content.includes('加载中') ||
          aiMsg.content.includes('请稍候') ||
          aiMsg.content.includes('请等待')) {
        return false;
      }
      
      // 检查内容结构是否看起来完整
      const contentEndMarkers = ['.', '。', '!', '！', '?', '？', '）', ')', ']', '}'];
      const lastChar = aiMsg.content.trim().slice(-1);
      
      // 以常见结束符号结尾，或内容较长，认为可能是完整消息
      if (contentEndMarkers.includes(lastChar) || aiMsg.content.length > 100) {
        return true;
      }
      
      // 如果内容包含代码块且是完整的代码块，也认为是完成的
      if (aiMsg.content.includes('```') && 
          (aiMsg.content.match(/```/g) || []).length >= 2) {
        return true;
      }
    }
    
    // 默认不认为完成
    return false;
  };
  
  const pollForAIResponse = async () => {
    // 设置最大轮询次数限制，防止无限循环
    if (pollingCount++ >= maxPolling) {
      console.warn('AI响应轮询超时，停止等待');
      message.warning('AI助手响应超时，请稍后重试');
      cleanupPolling(conversationId);
      return;
    }
    
    // 确保在每次轮询开始时思考动画正常显示
    const ensureThinkingVisible = () => {
      const currentMsgs = conversationMessages.value.get(conversationId) || [];
      const hasThinkingMsg = currentMsgs.some(msg => msg.is_thinking || (msg as any)._forceThinking);
      
      if (!hasThinkingMsg && thinkingMessageMap.value.size > 0) {
        console.warn('轮询开始前发现思考动画已消失但尚未收到AI回复，恢复思考状态');
        // 找到最后一条用户消息，为其添加对应的思考状态消息
        const userMsgs = currentMsgs.filter(msg => msg.role === 'user');
        if (userMsgs.length > 0) {
          const lastUserMsg = userMsgs[userMsgs.length - 1];
          
          // 创建新的思考消息
          const newThinkingMsg: Message = {
            id: getCurrentTimeMs(), // 生成新的临时ID
            role: 'assistant',
            content: '正在思考中...',
            timestamp: createTimestamp(),
            is_thinking: true,
            _forceThinking: true,
            conversation_id: conversationId
          };
          
          // 添加思考消息并更新状态
          const updatedMsgs = [...currentMsgs, newThinkingMsg];
          conversationMessages.value.set(conversationId, updatedMsgs);
          
          // 更新思考消息映射，确保思考消息与用户消息正确关联
          const pendingUserIds = Array.from(thinkingMessageMap.value.values());
          if (!pendingUserIds.includes(lastUserMsg.id)) {
            thinkingMessageMap.value.set(newThinkingMsg.id, lastUserMsg.id);
            loadingMessages.value.add(newThinkingMsg.id);
          }
          
          console.log('已恢复思考状态动画');
        }
      }
    };
    
    // 在每次轮询开始时确保思考动画显示
    ensureThinkingVisible();
    
    try {
      // 获取最新消息
      const allMessages = await aiAssistantStore.getMessages(conversationId);
      
      // 添加消息去重处理，但保留思考中消息
      const uniqueMessages = Array.from(
        new Map(allMessages.map((msg: Message) => [msg.id, msg])).values()
      ) as Message[];
      
      // 重置连续失败计数
      consecutiveFailures = 0;
      
      // 获取待处理的用户消息ID列表
      const pendingUserIds = Array.from(thinkingMessageMap.value.values());
      console.log('待处理的用户消息ID:', pendingUserIds);
      
      // 查找匹配的AI消息 - 根据关联ID匹配
      const newAIResponses = uniqueMessages.filter((msg: Message) => 
        msg.role === 'assistant' && 
        pendingUserIds.some(userId => userId + 1 === msg.id)
      );
      
      if (newAIResponses.length > 0) {
        console.log(`找到 ${newAIResponses.length} 条匹配的AI回复`);
        
        // 检查AI消息是否真正完成，只处理完成的消息
        const completedResponses = newAIResponses.filter(msg => {
          // 记录调试信息
          console.log(`检查消息ID=${msg.id}是否完成: 内容长度=${msg.content?.length || 0}, 处理时间=${msg.processing_time}`);
          
          // 使用增强的判断函数确定是否完成
          const completed = checkMessageCompleted(msg);
          console.log(`消息ID=${msg.id} 完成状态: ${completed}`);
          return completed;
        });
        
        if (completedResponses.length > 0) {
          console.log(`找到 ${completedResponses.length} 条已完成的AI回复，将替换思考状态`);
          
          // 处理每条完成的AI消息
          for (const aiMsg of completedResponses) {
            const aiMessage = convertMessageFormat(aiMsg);
            console.log(`准备替换思考状态: 消息ID=${aiMessage.id}, 内容长度=${aiMessage.content?.length || 0}`);
            
            // 只有在确认消息确实完成时才替换思考动画
            if (aiMessage.content && aiMessage.content.length > 0) {
              // 在替换前先标记所有相关思考消息为即将被替换
              // 这有助于防止在UI中出现思考动画和AI回复同时显示
              const currentMsgs = conversationMessages.value.get(conversationId) || [];
              currentMsgs.forEach(msg => {
                if (msg.is_thinking || (msg as any)._forceThinking) {
                  (msg as any).willBeReplaced = true;
                }
              });
              conversationMessages.value.set(conversationId, [...currentMsgs]);
              
              // 然后执行正常替换
              updateMessageList(conversationId, aiMessage, true);
              
              // 从映射表中移除已处理的消息
              for (const [thinkingId, userId] of thinkingMessageMap.value.entries()) {
                if (userId + 1 === aiMessage.id) {
                  thinkingMessageMap.value.delete(thinkingId);
                  loadingMessages.value.delete(thinkingId);
                  console.log(`已移除思考消息映射: thinkingId=${thinkingId} -> userId=${userId}`);
                  break;
                }
              }
            } else {
              console.log(`跳过空内容消息: ID=${aiMessage.id}`);
            }
          }
          
          // 如果所有思考消息都已处理，清理轮询状态
          if (thinkingMessageMap.value.size === 0) {
            console.log('所有思考中消息已替换，停止轮询');
            cleanupPolling(conversationId);
            return;
          }
          
          // 如果有未完成的消息，继续轮询
          if (completedResponses.length < newAIResponses.length) {
            console.log(`有 ${newAIResponses.length - completedResponses.length} 条AI回复尚未完成，继续轮询`);
            pollingTimer.value = setTimeout(pollForAIResponse, pollingInterval);
            return;
          } else if (thinkingMessageMap.value.size > 0) {
            console.log(`仍有 ${thinkingMessageMap.value.size} 条思考消息未处理，继续轮询`);
            pollingTimer.value = setTimeout(pollForAIResponse, pollingInterval);
            return;
          }
        } else {
          console.log(`找到的 ${newAIResponses.length} 条AI回复尚未完成，继续轮询`);
          // 使用指数退避策略增加等待时间
          pollingInterval = Math.min(pollingInterval * backoffFactor, maxPollingInterval);
          // 设置下一次轮询
          pollingTimer.value = setTimeout(pollForAIResponse, pollingInterval);
        }
      } else {
        console.log(`等待AI响应中... (${pollingCount}/${maxPolling}) 间隔: ${pollingInterval}ms`);
        
        // 确保轮询期间思考动画不会消失 - 关键修复点
        ensureThinkingVisible();
        
        // 使用指数退避策略增加等待时间
        pollingInterval = Math.min(pollingInterval * backoffFactor, maxPollingInterval);
        
        // 设置下一次轮询
        pollingTimer.value = setTimeout(pollForAIResponse, pollingInterval);
      }
    } catch (error) {
      console.error('轮询AI响应时出错:', error);
      
      // 增加连续失败计数
      consecutiveFailures++;
      
      // 错误时仍继续轮询，但增加等待时间
      if (consecutiveFailures >= maxConsecutiveFailures) {
        // 多次连续失败后提示用户，但不停止轮询
        message.error('获取AI助手响应时出错，正在重试...');
        // 重置失败计数
        consecutiveFailures = 0;
      }
      
      // 增加等待时间，但继续轮询
      pollingInterval = Math.min(pollingInterval * 2, maxPollingInterval);
      pollingTimer.value = setTimeout(pollForAIResponse, pollingInterval);
    }
  };
  
  // 开始第一次轮询，延迟执行，确保思考动画有足够显示时间
  pollingTimer.value = setTimeout(pollForAIResponse, initialDelay);
  
  // 清理轮询相关状态
  const cleanupPolling = (convId: number) => {
    console.log('开始清理轮询状态');
    
    // 强制移除所有思考消息，确保不会有思考消息与AI回复共存
    const currentMsgs = conversationMessages.value.get(convId) || [];
    const filteredMsgs = currentMsgs.filter(m => !m.is_thinking && !(m as any)._forceThinking);
    
    // 计算是否需要清理思考消息
    const hasThinkingMessages = currentMsgs.length !== filteredMsgs.length;
    
    if (hasThinkingMessages) {
      console.log('清理所有思考中消息');
      conversationMessages.value.set(convId, filteredMsgs);
    }
    
    // 清理临时消息映射
    loadingMessages.value.clear();
    thinkingMessageMap.value.clear();
    
    // 重置处理状态
    isProcessing.value = false;
    
    // 清理锁
    localStorage.removeItem(SENDING_LOCK_KEY);
    console.log('轮询完成，移除发送锁');
    
    // 清除轮询定时器
    if (pollingTimer.value) {
      clearTimeout(pollingTimer.value);
      pollingTimer.value = null;
    }
    
    // 滚动到底部
    scrollToBottom();
  };
};

// 处理返回的AI消息
const processAIResponse = (response: any) => {
  if (!response) {
    console.warn('收到的AI响应为空，无法处理');
    return;
  }
  
  console.log('AI响应数据结构:', response);
  
  // 确保当前会话存在
  if (!currentConversation.value) {
    console.error('当前没有活动会话，无法处理AI响应');
    return;
  }
  
  // 获取当前会话ID
  const conversationId = currentConversation.value.id;
  
  // 检查AI响应是否真正完成
  const isResponseCompleted = (aiMsg: any): boolean => {
    // 检查是否有明确的完成标志
    if (aiMsg.is_completed === true) {
      return true;
    }
    
    // 检查是否有处理时间（表示处理已完成）
    if (aiMsg.processing_time !== undefined && aiMsg.processing_time > 0) {
      return true;
    }
    
    // 检查内容是否看起来是完整的
    if (aiMsg.content && typeof aiMsg.content === 'string') {
      // 如果内容表明是临时状态，则不认为完成
      if (aiMsg.content.includes('正在处理') || 
          aiMsg.content.includes('思考中') ||
          aiMsg.content.includes('加载中') ||
          aiMsg.content.includes('请稍候') ||
          aiMsg.content.includes('请等待')) {
        return false;
      }
      
      // 检查内容结构是否看起来完整
      const contentEndMarkers = ['.', '。', '!', '！', '?', '？', '）', ')', ']', '}'];
      const lastChar = aiMsg.content.trim().slice(-1);
      
      // 以常见结束符号结尾，或内容较长，认为可能是完整消息
      if (contentEndMarkers.includes(lastChar) || aiMsg.content.length > 100) {
        return true;
      }
      
      // 如果内容包含代码块且是完整的代码块，也认为是完成的
      if (aiMsg.content.includes('```') && 
          (aiMsg.content.match(/```/g) || []).length >= 2) {
        return true;
      }
    }
    
    // 默认不认为完成
    return false;
  };
  
  // 有AI响应的情况
  if (response.ai_message) {
    console.log('检测到响应中包含AI消息:', response.ai_message);
    
    // 检查AI响应是否真正完成
    const responseCompleted = isResponseCompleted(response.ai_message);
    if (!responseCompleted) {
      console.log('AI响应尚未完成，保持思考状态，等待轮询获取完整响应');
      return;
    }
    
    console.log('AI响应已完成，可以替换思考动画');
    
    // 规范化处理时间值
    let processingTime = undefined;
    if (response.ai_message.processing_time !== undefined) {
      // 确保处理时间是数字类型
      if (typeof response.ai_message.processing_time === 'string') {
        processingTime = parseFloat(response.ai_message.processing_time);
        if (isNaN(processingTime)) processingTime = undefined;
      } else {
        processingTime = response.ai_message.processing_time;
      }
    }
    
    // 处理AI消息，确保所有必要字段
    const aiMessage = convertMessageFormat({
      id: response.ai_message.id || Date.now(),
      role: 'assistant',
      content: response.ai_message.content || '(无内容)',
      timestamp: response.ai_message.timestamp || createTimestamp(),
      conversation_id: conversationId,
      processing_time: processingTime,
      is_timeout_message: response.ai_message.is_timeout_message,
      is_completed: true // 标记为已完成
    });
    
    console.log('AI消息内容:', aiMessage.content);
    
    // 检查思考状态是否已经显示足够长时间
    // 获取当前会话的消息列表
    const msgs = conversationMessages.value.get(conversationId) || [];
    
    // 先查找有没有思考中的消息
    const thinkingIndex = msgs.findIndex(m => m.is_thinking || (m as any)._forceThinking);
    
    if (thinkingIndex >= 0) {
      console.log('找到思考中消息，准备替换');
      
      // 确保思考状态至少显示足够长时间
      const thinkingCreationTime = msgs[thinkingIndex] ? 
        new Date(msgs[thinkingIndex].timestamp).getTime() : 0;
      const currentTime = getCurrentTimeMs();
      const timeSinceThinking = currentTime - thinkingCreationTime;
      
      // 确保思考状态至少显示最少时间
      const minThinkingTime = 3000; // 最少思考显示时间(毫秒)
      
      if (thinkingCreationTime > 0 && timeSinceThinking < minThinkingTime) {
        // 思考时间不足，延迟替换，但不改变思考状态
        const delayTime = minThinkingTime - timeSinceThinking;
        console.log(`思考状态显示不足${minThinkingTime/1000}秒，延迟${delayTime}ms直接替换AI消息`);
        
        setTimeout(() => {
          // 更新消息列表 - 传入true表示替换思考中消息
          updateMessageList(conversationId, aiMessage, true);
        }, delayTime);
      } else {
        // 思考时间足够，直接替换
        console.log('思考状态已显示足够时间，直接替换为AI回复');
        // 更新消息列表 - 传入true表示替换思考中消息
        updateMessageList(conversationId, aiMessage, true);
      }
    } else {
      // 没有找到思考中消息，直接添加AI回复
      console.log('未找到思考中消息，直接添加AI回复');
      updateMessageList(conversationId, aiMessage, false);
    }
  } else if (response.role === 'assistant' && response.content) {
    // 使用与上面相同的逻辑，但避免代码重复
    const processResponseMessage = () => {
      // 检查AI响应是否真正完成
      const responseCompleted = isResponseCompleted(response);
      if (!responseCompleted) {
        console.log('直接响应的AI消息尚未完成，保持思考状态，等待轮询获取完整响应');
        return;
      }
      
      console.log('直接响应的AI消息已完成，可以替换思考动画');
      
      // 规范化处理时间值
      let processingTime = undefined;
      if (response.processing_time !== undefined) {
        // 确保处理时间是数字类型
        if (typeof response.processing_time === 'string') {
          processingTime = parseFloat(response.processing_time);
          if (isNaN(processingTime)) processingTime = undefined;
        } else {
          processingTime = response.processing_time;
        }
      }
      
      const aiMessage = convertMessageFormat({
        id: response.id || Date.now(),
        role: 'assistant',
        content: response.content || '(无内容)',
        timestamp: response.timestamp || createTimestamp(),
        conversation_id: conversationId,
        processing_time: processingTime,
        is_timeout_message: response.is_timeout_message,
        is_completed: true // 标记为已完成
      });
      
      console.log('AI消息内容:', aiMessage.content);
      
      // 检查思考状态是否已经显示足够长时间
      // 获取当前会话的消息列表
      const msgs = conversationMessages.value.get(conversationId) || [];
      
      // 先查找有没有思考中的消息
      const thinkingIndex = msgs.findIndex(m => m.is_thinking || (m as any)._forceThinking);
      
      if (thinkingIndex >= 0) {
        console.log('找到思考中消息，准备替换');
        
        // 确保思考状态至少显示足够长时间
        const thinkingCreationTime = msgs[thinkingIndex] ? 
          new Date(msgs[thinkingIndex].timestamp).getTime() : 0;
        const currentTime = getCurrentTimeMs();
        const timeSinceThinking = currentTime - thinkingCreationTime;
        
        // 确保思考状态至少显示最少时间
        const minThinkingTime = 3000; // 最少思考显示时间(毫秒)
        
        if (thinkingCreationTime > 0 && timeSinceThinking < minThinkingTime) {
          // 思考时间不足，延迟替换，但不改变思考状态
          const delayTime = minThinkingTime - timeSinceThinking;
          console.log(`思考状态显示不足${minThinkingTime/1000}秒，延迟${delayTime}ms直接替换AI消息`);
          
          setTimeout(() => {
            // 更新消息列表 - 传入true表示替换思考中消息
            updateMessageList(conversationId, aiMessage, true);
          }, delayTime);
        } else {
          // 思考时间足够，直接替换
          console.log('思考状态已显示足够时间，直接替换为AI回复');
          // 更新消息列表 - 传入true表示替换思考中消息
          updateMessageList(conversationId, aiMessage, true);
        }
      } else {
        // 没有找到思考中消息，直接添加AI回复
        console.log('未找到思考中消息，直接添加AI回复');
        updateMessageList(conversationId, aiMessage, false);
      }
    };
    
    // 执行处理
    processResponseMessage();
  } else {
    // 没有直接的AI响应，需要刷新消息列表
    console.log('响应中无AI消息，刷新消息列表');
    updateMessagesAfterSend(response);
  }
};

// 辅助函数：更新消息列表，替换思考消息
const updateMessageList = (conversationId: number, message: Message, isAiResponse = false) => {
  // 获取当前会话的消息列表
  const currentMessages = conversationMessages.value.get(conversationId) || [];
  
  // 获取消息ID
  const msgId = message.id;
  
  // 准备更新的消息列表
  let updatedMessages = [...currentMessages];
  
  // 如果是AI回复且存在思考中消息
  if (isAiResponse && message.role === 'assistant' && loadingMessages.value.size > 0) {
    console.log('正在处理AI回复消息:', message);
    
    // 查找对应的思考中消息ID
    let tempId = null;
    
    // 从映射表中查找对应的思考消息ID
    for (const [thinkingId, userId] of thinkingMessageMap.value.entries()) {
      // 如果AI消息ID是用户消息ID+1，说明这是对应的回复
      if (msgId === userId + 1) {
        tempId = thinkingId;
        break;
      }
    }
    
    // 如果找到对应的思考中消息
    if (tempId) {
      console.log(`找到对应的思考中消息ID: ${tempId}`);
      
      // 查找思考中消息的索引
      const thinkingIndex = updatedMessages.findIndex(m => m.id === tempId);
      
      if (thinkingIndex >= 0) {
        console.log(`替换思考中消息，位置: ${thinkingIndex}`);
        
        // 创建一个克隆的消息对象，保留思考消息的ID，但使用AI回复的内容
        // 这样前端会认为这是同一个消息，只是内容变了，而不是替换了消息
        const replacedMessage = {
          ...message,
          id: tempId, // 保留原思考消息ID，保证DOM元素身份一致性
          _originalAiMsgId: message.id, // 保存原始AI消息ID
          is_thinking: false, // 确保不再被识别为思考状态
          _forceThinking: false, // 移除强制思考标记
          _replacedAiContent: true, // 标记这是替换后的消息
          _transitionComplete: false, // 标记需要完成过渡动画
          timestamp: message.timestamp || createTimestamp(), // 使用新消息的时间戳
        };
        
        // 直接替换思考消息
        updatedMessages[thinkingIndex] = replacedMessage;
        
        // 从加载中集合移除
        loadingMessages.value.delete(tempId);
        
        // 从映射表中移除
        thinkingMessageMap.value.delete(tempId);
        
        // 更新消息列表 - 确保一次性更新，不出现中间状态
        conversationMessages.value.set(conversationId, updatedMessages);
        
        // 滚动到底部
        scrollToBottom();
        
        // 在短暂延迟后设置过渡完成标记，让组件有时间应用过渡效果
        setTimeout(() => {
          const latestMessages = conversationMessages.value.get(conversationId) || [];
          const msgIndex = latestMessages.findIndex(m => m.id === tempId);
          if (msgIndex >= 0) {
            const updatedMsg = {...latestMessages[msgIndex], _transitionComplete: true};
            latestMessages[msgIndex] = updatedMsg;
            conversationMessages.value.set(conversationId, [...latestMessages]);
          }
        }, 300); // 延长延迟时间至300ms，确保过渡动画有足够时间
        
        return updatedMessages;
      } else {
        console.warn(`未找到对应的思考中消息，位置: ${thinkingIndex}`);
        // 找不到thinking message的位置，添加为新消息
        updatedMessages.push(message);
      }
    } else {
      console.log('未找到匹配的思考中消息ID，添加为新消息');
      // 添加为新消息
      updatedMessages.push(message);
    }
  } else {
    // 非AI回复或无思考中消息，直接添加
    console.log('添加普通消息:', message);
    
    // 检查是否有同ID的思考消息需要删除或替换
    if (message.role === 'assistant') {
      // 查找并删除所有思考中消息
      updatedMessages = updatedMessages.filter(msg => !msg.is_thinking && !(msg as any)._forceThinking);
      console.log('已移除所有思考中消息');
    }
    
    updatedMessages.push(message);
  }
  
  // 更新消息列表
  conversationMessages.value.set(conversationId, updatedMessages);
  
  // 滚动到底部
  scrollToBottom();
  
  return updatedMessages;
};

// 添加开发环境标识
const isDev = import.meta.env.DEV || import.meta.env.MODE === 'development';

// 测试函数 - 添加思考中测试消息
const addTestThinkingMessage = () => {
  if (!currentConversation.value) {
    message.warning('请先创建或选择一个对话');
    return;
  }
  
  const tempId = Date.now();
  const thinkingMsg = {
    id: tempId,
    role: 'assistant' as const,
    content: '正在思考中...',
    timestamp: createTimestamp(),
    is_thinking: true,
    conversation_id: currentConversation.value.id
  };
  
  console.log('添加测试思考消息:', thinkingMsg);
  
  // 获取当前消息列表
  const msgs = conversationMessages.value.get(currentConversation.value.id) || [];
  
  // 添加思考消息
  conversationMessages.value.set(
    currentConversation.value.id, 
    [...msgs, thinkingMsg]
  );
  
  // 添加到加载中集合
  loadingMessages.value.add(tempId);
  
  // 3秒后移除思考消息
  setTimeout(() => {
    // 获取最新消息列表
    const currentMsgs = conversationMessages.value.get(currentConversation.value!.id) || [];
    // 移除思考消息
    const filteredMsgs = currentMsgs.filter(m => m.id !== tempId);
    
    // 添加回复消息
    const replyMsg = {
      id: tempId + 1,
      role: 'assistant' as const,
      content: '这是一条测试回复，替换了思考中消息。',
      timestamp: createTimestamp(),
      conversation_id: currentConversation.value!.id
    };
    
    // 更新消息列表
    conversationMessages.value.set(
      currentConversation.value!.id,
      [...filteredMsgs, replyMsg]
    );
    
    // 移除加载状态
    loadingMessages.value.delete(tempId);
    
    console.log('测试思考消息已替换为回复');
  }, 3000);
};
</script>

<style scoped>
.conversation-container {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.1) transparent;
}

.conversation-container::-webkit-scrollbar {
  width: 6px;
}

.conversation-container::-webkit-scrollbar-track {
  background: transparent;
}

.conversation-container::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.query-result {
  font-size: 14px;
}

/* Markdown内容样式 */
.markdown-content :deep(pre) {
  background-color: #f6f8fa;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  margin: 12px 0;
}

.markdown-content :deep(code) {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 85%;
  padding: 0.2em 0.4em;
  margin: 0;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
}

.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.markdown-content :deep(blockquote) {
  margin: 0;
  padding-left: 16px;
  border-left: 4px solid #dfe2e5;
  color: #6a737d;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.markdown-content :deep(th), 
.markdown-content :deep(td) {
  border: 1px solid #dfe2e5;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content :deep(th) {
  background-color: #f6f8fa;
}

/* 用户消息气泡样式 */
.custom-message-bubble.user-bubble {
  /* Removed to let MessageBubble component handle styling */
}

/* AI助手消息气泡样式 */
.custom-message-bubble.assistant-bubble {
  /* Removed to let MessageBubble component handle styling */
}

/* 确保内部内容不受Naive UI默认样式的影响 */
.custom-message-bubble.assistant-bubble :deep(p) {
  /* Removed to let MessageBubble component handle styling */
}

.custom-message-bubble.assistant-bubble :deep(p:last-child) {
  /* Removed to let MessageBubble component handle styling */
}

/* 单行内容不换行 */
.custom-message-bubble.assistant-bubble :deep(p:only-child) {
  /* Removed to let MessageBubble component handle styling */
}

/* 简单消息文本样式 */
.custom-message-bubble .simple-message {
  /* Removed to let MessageBubble component handle styling */
}

/* 使用pre标签显示简单消息，但保持与普通文本相同外观 */
.pre-message {
  white-space: pre-wrap;
  font-family: inherit;
  font-size: inherit;
  margin: 0;
  padding: 0;
  background: none;
  border: none;
  overflow: visible;
  line-height: inherit;
  text-align: inherit;
  color: inherit;
  display: inline;
}

/* 消息操作按钮相关样式 */
.relative {
  position: relative;
}

.message-actions {
  position: absolute;
  display: none;
  padding: 4px 8px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.relative:hover .message-actions {
  display: flex;
  gap: 8px;
}

.user-actions {
  bottom: -32px;
  right: 0;
}

.assistant-actions {
  bottom: -32px;
  left: 0;
}

/* 确保消息气泡有足够的底部边距 */
.conversation-container {
  padding-bottom: 60px !important;
}

/* 添加未知角色消息的样式 */
.custom-message-bubble.unknown-bubble {
  /* Removed to let MessageBubble component handle styling */
}

/* 思考内容样式 - 新版本 */
.think-wrapper {
  margin-bottom: 10px;
  border: 1px solid rgba(82, 196, 26, 0.3);
  border-radius: 6px;
  padding: 0px 12px;
  max-width: 90%;
  background-color: rgba(82, 196, 26, 0.05);
  overflow: hidden;
}

.think-wrapper.expanded .think-icon {
  transform: rotate(90deg);
}

.think-wrapper.expanded .think-body {
  display: block;
}

.think-header {
  padding: 8px 12px;
  font-size: 0.9em;
  color: #52c41a;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  user-select: none;
}

.think-header:hover {
  background-color: rgba(82, 196, 26, 0.1);
}

.think-icon {
  display: inline-block;
  margin-right: 8px;
  transition: transform 0.2s ease;
}

.think-title {
  flex: 1;
}

.think-body {
  display: none;
  padding: 0 12px 12px;
  font-size: 0.95em;
  border-top: 1px dashed rgba(82, 196, 26, 0.3);
}

.think-body .markdown-content {
  margin-top: 8px;
  padding-top: 8px;
}

/* 确保简单消息样式与其他内容一致 */
.simple-message {
  white-space: pre-wrap;
  word-break: normal;
  text-align: left;
}

/* 文件上传区域样式 */
.message-input-container {
  position: relative;
}

.input-area-container {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.file-upload-button {
  margin-right: 8px;
  display: flex;
  align-items: center;
  z-index: 10;
}

.uploaded-files-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.uploaded-file-item {
  position: relative;
}

.image-preview {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  background-color: #fff;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-preview {
  display: flex;
  align-items: center;
  min-width: 120px;
  padding: 8px 12px;
  background-color: #f0f0f0;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.file-icon {
  margin-right: 8px;
  color: #606060;
}

.file-name {
  font-size: 0.85em;
  color: #333;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 8px;
}

.file-size {
  font-size: 0.75em;
  color: #666;
  white-space: nowrap;
}

.remove-file-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.9) !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.send-button {
  align-self: flex-end;
}

/* 思考模式控制和按键提示放在同一行 */
.input-controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-top: 10px;
  margin-bottom: 4px;
  font-size: 0.75rem;
}

/* 思考模式控制 */
.think-mode-control {
  display: flex;
  align-items: center;
}

/* 按键提示 */
.keyboard-tips {
  display: flex;
  align-items: center;
  color: #666;
  margin-left: auto;
}

/* 图片缩略图容器样式 */
.message-images {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}

.image-thumbnail-container {
  position: relative;
  width: 120px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.image-thumbnail-container:hover {
  transform: scale(1.05);
  cursor: pointer;
}

.image-thumbnail {
  width: 100%;
  height: 100px;
  object-fit: cover;
  display: block;
}

.image-filename {
  font-size: 10px;
  color: #666;
  padding: 4px;
  background: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 图片预览样式 */
.image-preview-container {
  position: relative;
  max-height: 90vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-image {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
}

.close-preview-button {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.8);
}

/* Style for failed images */
.image-load-error {
  border: 1px dashed #d9d9d9;
  background-color: #f9f9f9;
  opacity: 0.8;
  filter: grayscale(100%);
}

/* 添加样式改进图片显示 */
.message-image-container {
  margin: 10px 0;
  max-width: 100%;
  overflow: hidden;
  border-radius: 4px;
}

.message-image {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.image-error {
  width: 150px;
  height: 150px;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.code-block {
  margin: 10px 0;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
}
</style>
