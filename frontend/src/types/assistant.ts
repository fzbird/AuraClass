/**
 * AI助手消息类型定义
 */
export interface AIMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  loading?: boolean;
  id?: number;
  conversation_id?: number;
  processing_time?: number;
  is_thinking?: boolean;
  is_timeout_message?: boolean;
}

/**
 * AI对话定义
 */
export interface AIConversation {
  id: number;
  title: string;
  updated_at: string;
  created_at?: string;
  user_id?: number;
  messages?: AIMessage[];
}

/**
 * AI助手查询请求
 */
export interface AIQuery {
  query_text: string;
  context_data?: Record<string, any>;
}

/**
 * AI助手响应
 */
export interface AIResponse {
  query_id?: number | string;
  response: string;
  processing_time?: number | string;
  error?: string | null;
  details?: Record<string, any> | string | null;
}

/**
 * AI助手建议
 */
export interface AISuggestion {
  suggestions: string[];
}

// 对话消息附件类型
export interface MessageAttachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
}

// 文件处理结果类型
export interface FileProcessResult {
  id: string;
  name: string;
  url: string;
  status: 'success' | 'error';
  message?: string;
}

// 消息上下文类型
export interface MessageContext {
  user?: {
    id: number;
    name: string;
    avatar?: string;
  };
  timestamp: string;
  conversation_id: number;
  attachments?: MessageAttachment[];
}

// 对话分析器配置类型
export interface AnalyzerConfig {
  contextType: 'student' | 'class' | 'general';
  contextId?: number;
  timeRange?: [string, string];
  metrics: string[];
}

// 添加新接口定义，用于处理带AI消息的响应
export interface AIMessageResponse {
  ai_message?: {
    id: number;
    role: 'assistant';
    content: string;
    timestamp?: string;
    processing_time?: number;
    conversation_id?: number;
    is_timeout_message?: boolean;
    is_thinking?: boolean;
  };
  is_timeout?: boolean;
  id?: number;
  role?: string;
  content?: string;
  conversation_id?: number;
  timestamp?: string;
  processing_time?: number;
  [key: string]: any; // 允许其他属性
}

// 通用消息类型，确保类型兼容性
export interface UnifiedMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  conversation_id?: number;
  processing_time?: number;
  is_thinking?: boolean;
  is_timeout_message?: boolean;
  files?: MessageAttachment[];
  use_local_model?: boolean;
  model_name?: string;
} 