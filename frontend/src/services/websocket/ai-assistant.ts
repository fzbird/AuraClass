import { ref, watch } from 'vue';
import { useUserStore } from '@/stores/user';
import { useBaseWebSocket } from './base';
import type { AIResponse, AIQuery } from '@/types/assistant';

/**
 * AI助手WebSocket服务
 * 提供AI查询、响应处理和建议获取等功能
 */
export function useAIAssistantWebSocket() {
  const userStore = useUserStore();
  
  // 创建基础WebSocket连接
  const {
    socket,
    isConnected,
    isConnecting,
    connectionError,
    connect,
    disconnect,
    reconnect,
    send
  } = useBaseWebSocket('/ws/ai-assistant', {
    debug: import.meta.env.DEV,     // 开发环境开启调试
    heartbeatInterval: 60000,       // 60秒心跳间隔
    reconnectAttempts: 3            // 最多尝试3次重连
  });
  
  // 最新的AI响应
  const latestResponse = ref<AIResponse | null>(null);
  // 最新的AI建议
  const latestSuggestions = ref<string[]>([]);
  // 是否正在处理查询
  const isProcessing = ref(false);
  
  // 发送AI查询
  const sendQuery = (queryText: string, contextData?: Record<string, any>) => {
    if (!isConnected.value) {
      connectionError.value = "WebSocket未连接，无法发送查询";
      return false;
    }
    
    if (isProcessing.value) {
      console.warn('已有正在处理的查询，请等待完成');
      return false;
    }
    
    const query: AIQuery = {
      query_text: queryText,
      context_data: contextData
    };
    
    isProcessing.value = true;
    
    const success = send({
      type: 'query',
      data: query
    });
    
    if (!success) {
      isProcessing.value = false;
    }
    
    return success;
  };
  
  // 请求AI建议
  const requestSuggestions = (prefix: string = '') => {
    if (!isConnected.value) {
      return false;
    }
    
    return send({
      type: 'suggest',
      data: {
        prefix
      }
    });
  };
  
  // 处理接收到的AI响应
  const handleResponse = (data: any) => {
    try {
      // 添加调试日志，查看收到的数据结构
      console.log('WebSocket received data:', JSON.stringify(data, null, 2));
      
      if (data.type === 'response' && data.data) {
        // 确保处理潜在的日期时间字符串
        let response = data.data.response;
        let error = data.data.error;
        
        // 如果没有response但有content字段，使用content作为response (兼容旧版API)
        if (!response && data.data.content) {
          response = data.data.content;
        }
        
        // 检查是否包含日期时间序列化错误信息
        if (!response && error && (
            error.includes("datetime is not JSON serializable") || 
            error === 'datetime_serialization_error')) {
          // 提供友好的错误信息
          response = "由于服务器内部错误，无法显示完整回复。请联系技术支持进行修复。";
          error = "服务器响应格式错误 (datetime序列化失败)";
          
          // 记录详细错误
          console.warn("AI响应中包含datetime序列化错误");
        }
        
        latestResponse.value = {
          query_id: data.data.query_id || "",
          response: response || "服务器未返回有效响应",
          processing_time: data.data.processing_time || 0,
          error: error || null,
          details: data.data.details || {}
        };
        
        isProcessing.value = false;
      } else if (data.type === 'suggestions' && data.data && Array.isArray(data.data.suggestions)) {
        latestSuggestions.value = data.data.suggestions;
      } else if (data.type === 'error') {
        // 处理显式错误消息
        const errorMessage = data.message || "AI助手服务出现未知错误";
        
        // 检查是否是datetime序列化错误
        if (data.data?.error === 'datetime_serialization_error' || 
            (typeof errorMessage === 'string' && errorMessage.includes('datetime'))) {
          // 显示友好错误消息
          latestResponse.value = {
            query_id: "",
            response: "请求处理过程中发生错误，请稍后再试。",
            processing_time: 0,
            error: "服务器内部错误",
            details: {
              original_error: errorMessage
            }
          };
        } else {
          // 处理其他类型错误
          latestResponse.value = {
            query_id: "",
            response: `很抱歉，服务器处理请求时出错: ${errorMessage}`,
            processing_time: 0,
            error: errorMessage,
            details: data.data || {}
          };
        }
        
        isProcessing.value = false;
      } else {
        // 未知响应类型，记录并提供默认响应
        console.warn('未识别的WebSocket响应类型:', data);
        
        latestResponse.value = {
          query_id: "",
          response: "收到未识别的响应格式，请稍后再试",
          processing_time: 0,
          error: "响应格式错误",
          details: { raw_data: data }
        };
        
        isProcessing.value = false;
      }
    } catch (error) {
      console.error('处理AI助手响应时出现错误:', error);
      
      // 提供默认响应以防止UI崩溃
      latestResponse.value = {
        query_id: "",
        response: "处理响应时发生错误，请重试",
        processing_time: 0,
        error: error instanceof Error ? error.message : "未知错误",
        details: {}
      };
      
      isProcessing.value = false;
    }
  };
  
  // 清除响应状态
  const clearResponse = () => {
    latestResponse.value = null;
    isProcessing.value = false;
  };
  
  // 监听WebSocket消息
  if (socket.value) {
    socket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleResponse(data);
      } catch (error) {
        console.error('处理AI助手消息出错:', error);
        isProcessing.value = false;
      }
    };
  }
  
  // 监听WebSocket变化
  watch(socket, (newSocket) => {
    if (newSocket) {
      newSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleResponse(data);
        } catch (error) {
          console.error('处理AI助手消息出错:', error);
          isProcessing.value = false;
        }
      };
    }
  });
  
  // 监听连接状态变化
  watch(isConnected, (connected) => {
    if (!connected) {
      // 连接断开时，重置处理状态
      isProcessing.value = false;
    }
  });
  
  return {
    socket,
    isConnected,
    isConnecting,
    connectionError,
    isProcessing,
    latestResponse,
    latestSuggestions,
    connect,
    disconnect,
    reconnect,
    sendQuery,
    requestSuggestions,
    clearResponse
  };
} 