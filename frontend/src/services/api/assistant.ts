// 临时修改，强制重新构建
import http from '../http'; // 从正确的路径导入
// import http from '@/utils/request'; // 错误的导入路径
import type { AIResponse, AIQuery, AISuggestion, AIMessage, AIConversation } from '@/types/assistant';

export interface AssistantResponse {
  content: string;
  query_id?: number;
  processing_time?: number;
}

/**
 * 发送普通消息给AI助手
 * @param content 消息内容
 * @returns AI助手的响应
 */
export const sendMessageToAssistant = async (content: string): Promise<AssistantResponse> => {
  try {
    const response = await http.post('/ai-assistant/query', { query_text: content });
    
    if (!response || !response.data) {
      console.warn('AI助手返回空响应');
      return {
        content: '服务器返回了空响应，请稍后重试。',
        processing_time: 0
      };
    }
    
    return {
      content: response.data?.response || '很抱歉，我无法理解您的问题。',
      query_id: response.data?.query_id,
      processing_time: response.data?.processing_time
    };
  } catch (error: any) {
    console.error('Error sending message to assistant:', error);
    
    // 错误分类处理
    const statusCode = error?.response?.status;
    
    // 提供更具体的错误消息
    if (statusCode === 401 || statusCode === 403) {
      return { content: '权限验证失败，请重新登录后再试。' };
    } else if (statusCode === 404) {
      return { content: 'AI服务接口不存在，请联系系统管理员。' };
    } else if (statusCode === 429) {
      return { content: '请求过于频繁，请稍后再试。' };
    } else if (statusCode >= 500) {
      return { content: 'AI服务暂时不可用，请稍后再试。' };
    }
    
    // 网络错误
    if (error.message?.includes('Network Error')) {
      return { content: '网络连接失败，请检查您的网络设置。' };
    }
    
    // 超时错误
    if (error.message?.includes('timeout')) {
      return { content: 'AI助手响应超时，请稍后再试。' };
    }
    
    return {
      content: '发送消息失败，请稍后重试。'
    };
  }
};

/**
 * 获取AI助手会话历史
 * @param conversationId 会话ID
 * @returns 会话历史消息列表
 */
export const getAssistantHistory = async (limit: number = 10) => {
  const response = await http.get('/ai-assistant/history', {
    params: { limit }
  });
  return response.data;
};

/**
 * 获取AI助手的建议
 * @param prefix 前缀文本，用于上下文相关建议
 * @returns 建议列表
 */
export const getAssistantSuggestions = async (prefix: string = '') => {
  const response = await http.get('/ai-assistant/suggestions', {
    params: { prefix }
  });
  return response.data?.suggestions || [];
};

interface MessagePayload {
  content: string;
}

interface MessageResponse {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface AnalysisParams {
  context: string;
  contextId?: string | number;
  timestamp?: number;
}

interface InsightResponse {
  data: any[];
  success: boolean;
  message?: string;
}

/**
 * 向会话中发送AI助手消息
 * @param conversationId 会话ID
 * @param message 消息内容
 * @returns 消息响应
 */
export const sendConversationMessage = async (conversationId: number, message: MessagePayload): Promise<MessageResponse> => {
  return http.post(`/ai-assistant/conversations/${conversationId}/messages`, message);
};

/**
 * 获取数据分析结果
 * @param params 分析参数
 * @returns 洞察结果响应
 */
export const getDataAnalysis = async (params: AnalysisParams): Promise<InsightResponse> => {
  return http.get('/ai-assistant/analysis', { params });
};

/**
 * 生成自然语言查询结果
 * @param query 查询文本
 * @param context 查询上下文
 * @returns 查询结果
 */
export const getNaturalLanguageQueryResult = async (query: string, context?: string): Promise<any> => {
  return http.post('/ai-assistant/query', { query, context });
};

/**
 * 获取智能建议
 * @param context 上下文
 * @param contextId 上下文ID
 * @returns 智能建议
 */
export const getSmartSuggestions = async (context: string, contextId?: number): Promise<any> => {
  return http.get('/ai-assistant/suggestions/smart', { 
    params: { context, contextId } 
  });
};

/**
 * 发送查询到AI助手
 * @param content 用户查询内容
 * @returns AI助手响应
 */
export async function queryAIAssistant(content: string) {
  try {
    const response = await http.post('/ai-assistant/query', { query_text: content });
    return response.data;
  } catch (error) {
    console.error('AI助手查询失败:', error);
    throw error;
  }
}

/**
 * 获取AI对话历史
 * @param params 查询参数
 * @returns 对话历史记录
 */
export async function getAIAssistantHistory(params = {}) {
  try {
    const response = await http.get('/ai-assistant/history', {
      params
    });
    return response.data;
  } catch (error) {
    console.error('获取AI对话历史失败:', error);
    return { data: [] };
  }
}

/**
 * 获取常用问题建议
 * @returns 建议列表
 */
export async function getAISuggestions(params = {}) {
  try {
    const response = await http.get('/ai-assistant/suggestions', {
      params
    });
    return response.data.data as AISuggestion[];
  } catch (error) {
    console.error('获取AI建议失败:', error);
    return [];
  }
}

/**
 * 创建新的AI对话
 * @param title 对话标题
 * @returns 新对话信息
 */
export async function createAIConversation(title: string): Promise<AIConversation> {
  try {
    const response = await http.post('/ai-assistant/conversations', { title });
    return response.data.data;
  } catch (error) {
    console.error('创建AI对话失败:', error);
    throw error;
  }
}

/**
 * 添加消息到对话中
 * @param conversationId 对话ID
 * @param message 消息内容
 * @returns 添加的消息
 */
export async function addMessageToConversation(conversationId: number, message: { content: string, role: 'user' | 'assistant' }) {
  return http.post(`/ai-assistant/conversations/${conversationId}/messages`, message);
}

/**
 * 获取AI分析
 * @param params 分析参数
 */
export async function getAIAnalysis(params = {}) {
  return http.get('/ai-assistant/analysis', { params });
}

/**
 * 高级查询AI助手
 * @param query 查询内容
 * @param context 上下文信息
 */
export async function advancedQueryAI(query: string, context?: any) {
  return http.post('/ai-assistant/query', { query, context });
}

/**
 * 获取智能建议
 * @param context 上下文参数
 */
export async function getAdvancedSmartSuggestions(context = {}) {
  return http.get('/ai-assistant/suggestions/smart', {
    params: context
  });
}

/**
 * 删除会话中的特定消息
 * @param conversationId 会话ID
 * @param messageId 消息ID
 * @returns 删除操作的结果
 */
export async function deleteMessage(conversationId: number, messageId: number): Promise<{ status: string; message: string }> {
  try {
    // 添加超时和重试逻辑
    const timeoutMs = 5000; // 5秒超时
    const retries = 2; // 最多重试2次
    
    let lastError: any = null;
    
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        
        const response = await http.delete<{ status: string; message: string }>(
          `/ai-assistant/conversations/${conversationId}/messages/${messageId}`,
          { signal: controller.signal }
        );
        
        clearTimeout(timeoutId);
        return response.data;
      } catch (error: any) {
        lastError = error;
        
        // 如果是超时或网络错误，则重试
        if (error.name === 'AbortError' || error.message?.includes('Network Error')) {
          console.warn(`删除消息尝试 ${attempt + 1}/${retries + 1} 失败，正在重试...`);
          // 如果不是最后一次尝试，则继续重试
          if (attempt < retries) continue;
        }
        
        // 如果是其他错误或已达到最大重试次数，则抛出异常
        throw error;
      }
    }
    
    throw lastError; // 如果所有重试都失败，抛出最后一个错误
  } catch (error: any) {
    console.error('删除消息失败:', error);
    
    // 提供更具体的错误响应
    if (error.response?.status === 404) {
      return { 
        status: 'not_found', 
        message: '消息不存在或已被删除' 
      };
    } else if (error.response?.status === 403) {
      return { 
        status: 'forbidden', 
        message: '您没有权限删除此消息' 
      };
    } else if (error.name === 'AbortError') {
      return { 
        status: 'timeout', 
        message: '删除请求超时，但界面已更新'
      };
    }
    
    // 重新抛出错误，让调用者决定如何处理
    throw error;
  }
} 