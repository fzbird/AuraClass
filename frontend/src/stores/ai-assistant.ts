import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import http from '@/services/http';
import { queryOllama } from '@/services/api/ollama';
import axios from 'axios';
import { useUserStore } from '@/stores/user';

export interface Conversation {
  id: number;
  title: string;
  updated_at: string;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  conversationId?: number; // 添加对话ID字段
  conversation_id?: number; // 兼容后端返回的字段
  processing_time?: number; // 处理时间，统一为数字类型
  use_local_model?: boolean;
  model_name?: string;
  is_thinking?: boolean; // 标记思考中状态
  is_timeout_message?: boolean; // 标记是否为超时消息
}

export const useAIAssistantStore = defineStore('ai-assistant', () => {
  const conversations = ref<Conversation[]>([]);
  const useLocalModel = ref(true); // 默认使用本地Ollama模型
  const localModelName = ref(localStorage.getItem('ai_assistant_model') || 'gemma3:27'); // 从localStorage获取或使用默认模型
  const useThinkMode = ref(true); // 默认开启思考模式
  
  // 添加消息存储
  const messages = ref<Map<number, Message[]>>(new Map());
  
  // 计算属性：当前AI模型来源
  const aiModelSource = computed(() => {
    return useLocalModel.value ? `本地模型 (${localModelName.value})` : '远程API';
  });
  
  // 计算属性：当前思考模式状态
  const aiThinkModeStatus = computed(() => {
    return useThinkMode.value ? '已开启' : '已关闭';
  });
  
  // 添加请求锁跟踪
  const pendingRequests = new Map<string, {
    id: string;
    timestamp: number;
    promise: Promise<any>;
  }>();
  
  // 添加请求去重函数
  const getDuplicateRequest = (conversationId: number, content: string): Promise<any> | null => {
    const cacheKey = `${conversationId}-${content}`;
    const now = Date.now();
    
    // 清理超过30秒的旧请求
    for (const [key, request] of pendingRequests.entries()) {
      if (now - request.timestamp > 30000) {
        pendingRequests.delete(key);
      }
    }
    
    // 检查相同请求
    const pendingRequest = pendingRequests.get(cacheKey);
    if (pendingRequest && now - pendingRequest.timestamp < 5000) {
      console.log(`[AIStore] 检测到重复请求: ${cacheKey}, 复用现有Promise`);
      return pendingRequest.promise;
    }
    
    return null;
  };
  
  // 获取所有对话
  const getConversations = async (): Promise<Conversation[]> => {
    console.log('[AIStore] 获取对话列表');
    
    try {
      // 获取对话列表
      const response = await http.get<Conversation[]>('/ai-assistant/conversations');
      console.log('获取对话响应:', response);
      
      // 处理不同格式的响应
      let conversationData: Conversation[] = [];
      
      if (Array.isArray(response)) {
        // 如果响应直接是数组
        conversationData = response;
      } else if (response && typeof response === 'object') {
        if (Array.isArray(response.data)) {
          // 如果响应有data字段且为数组
          conversationData = response.data;
        } else if (response && typeof response === 'object' && 'conversations' in response) {
          // 如果响应有conversations字段且为数组
          const responseWithConversations = response as { conversations: Conversation[] };
          if (Array.isArray(responseWithConversations.conversations)) {
            conversationData = responseWithConversations.conversations;
          }
        }
      }
      
      // 确保返回的是数组
      conversations.value = conversationData || [];
      return conversationData;
    } catch (error) {
      console.error('获取对话失败:', error);
      conversations.value = [];
      return [];
    }
  };
  
  // 创建新对话
  const createConversation = async (): Promise<Conversation> => {
    console.log('[AIStore] 创建新对话');
    
    try {
      // 发送创建对话请求
      const response = await http.post<Conversation>('/ai-assistant/conversations');
      console.log('[AIStore] 创建新对话成功:', response);
      
      // 处理不同格式的响应
      if (response && typeof response === 'object') {
        if (response.data) {
          return response.data;
        } else {
          // 如果直接返回了对话对象，先转为unknown再转为Conversation
          return response as unknown as Conversation;
        }
      }
      
      // 如果无法解析响应，返回一个基本的对话对象
      return {
        id: Date.now(),
        title: '未命名对话',
        updated_at: new Date().toISOString()
      };
    } catch (error) {
      console.error('创建新对话失败:', error);
      throw error;
    }
  };
  
  // 获取指定对话的消息历史
  const getMessages = async (conversationId: number): Promise<Message[]> => {
    console.log(`[AIStore] 获取会话 ${conversationId} 的消息列表`);
    
    try {
      const response = await http.get<Message[]>(
        `/ai-assistant/conversations/${conversationId}/messages`
      );
      
      // 添加数据格式检查
      if (!response) {
        console.warn('[AIStore] 响应对象为空');
        return [];
      }
      
      // 处理不同响应格式
      let messagesData: Message[] = [];
      if (Array.isArray(response)) {
        // 如果直接返回数组
        messagesData = response;
      } else if (response && typeof response === 'object') {
        // 如果返回对象中包含data属性
        if (Array.isArray(response.data)) {
          messagesData = response.data;
        } else if (response.data === undefined && Array.isArray(response)) {
          // 适配可能的后端直接返回数组的情况
          messagesData = response;
        }
      }
      
      console.log(`[AIStore] 成功获取 ${messagesData.length} 条消息`);
      
      // 记录消息状态并安全处理
      const processedMessages = messagesData.map((msg, index) => {
        // 确保消息ID有效
        if (!msg.id || typeof msg.id !== 'number') {
          console.warn(`[AIStore] 消息ID无效, 使用临时ID: ${Date.now() + index}`);
          msg.id = Date.now() + index;
        }
        
        // 确保content不为null或undefined
        if (msg.content === null || msg.content === undefined) {
          console.warn(`[AIStore] 消息内容为空: ID=${msg.id}, 角色=${msg.role}`);
          msg.content = msg.role === 'assistant' ? '(AI没有返回内容)' : '(空消息)';
        }
        
        // 确保role是有效值
        if (msg.role !== 'user' && msg.role !== 'assistant') {
          console.warn(`[AIStore] 角色类型无效: ${msg.role}, 已修正为assistant`);
          msg.role = 'assistant';
        }
        
        // 检查timestamp，确保格式有效
        if (!msg.timestamp) {
          msg.timestamp = new Date().toISOString();
        }
        
        console.log(`[AIStore] 处理消息 ${index + 1}: ID=${msg.id}, 角色=${msg.role}, 内容长度=${msg.content.length}`);
        return msg;
      });
      
      return processedMessages;
    } catch (error) {
      console.error('[AIStore] 获取消息失败:', error);
      // 返回空数组而不是抛出错误，确保UI不会崩溃
      return [];
    }
  };
  
  // 添加或修改sendMessage方法，使用直接等待而非轮询
  const sendMessage = async (conversationId: number, content: string, retryCount: number = 1): Promise<any> => {
    // 检查是否有重复请求
    const duplicateRequest = getDuplicateRequest(conversationId, content);
    if (duplicateRequest) {
      return duplicateRequest;
    }
    
    // 生成请求ID
    const requestId = `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
    
    // 创建包装的Promise
    const requestPromise = new Promise<any>(async (resolve, reject) => {
      try {
        console.log(`[AIStore] 发送消息并等待AI响应`);
        
        // 发送用户消息 - 设置较长的超时时间
        const response = await http.post(`/ai-assistant/conversations/${conversationId}/messages?request_id=${requestId}`, {
          content,
          role: 'user',
          useLocalModel: useLocalModel.value,
          modelName: localModelName.value,
          useThinkMode: useThinkMode.value,
          waitForResponse: true // 告知后端等待AI响应完成再返回
        }, {
          // 添加额外的请求头
          headers: {
            'X-Request-ID': requestId,
            'X-Timestamp': Date.now().toString()
          },
          // 设置较长的超时时间 - 60秒
          timeout: 60000
        });
        
        console.log(`[AIStore] 消息发送成功 (请求ID: ${requestId})`);
        resolve(response);
      } catch (error: any) {
        console.error(`[AIStore] 请求失败:`, error);
        
        // 获取错误详情
        const errorStatus = error.response?.status;
        const errorDetail = error.response?.data?.detail || '未知错误';
        const isTimeout = error.code === 'ECONNABORTED' || errorStatus === 408 || error.message.includes('timeout');
        
        // 处理超时错误，提供友好信息
        if (isTimeout) {
          console.log('[AIStore] 请求超时，AI响应时间过长');
          
          // 尝试一次FormData格式提交，不等待AI响应
          try {
            console.log('[AIStore] 尝试发送消息但不等待AI响应');
            const formData = new FormData();
            formData.append('content', content);
            formData.append('role', 'user');
            formData.append('useLocalModel', String(useLocalModel.value));
            formData.append('modelName', localModelName.value);
            formData.append('useThinkMode', String(useThinkMode.value));
            formData.append('waitForResponse', 'false');
            
            const fallbackResponse = await http.post(
              `/ai-assistant/conversations/${conversationId}/messages?request_id=${requestId}&t=${Date.now()}`,
              formData,
              {
                headers: {
                  'Content-Type': 'multipart/form-data',
                  'X-Request-ID': `${requestId}-fallback`,
                  'X-Timestamp': Date.now().toString()
                },
                timeout: 10000 // 较短的超时
              }
            );
            
            console.log('[AIStore] 消息发送成功 (不等待AI响应)');
            
            // 构建一个带有超时标识的响应对象
            const responseWithTimeout = {
              ...fallbackResponse,
              is_timeout: true,
              ai_message: {
                id: Date.now(), // 生成一个临时ID
                role: 'assistant' as const,
                content: '**AI响应时间过长**，消息已发送，但未能在60秒内获得响应。AI会在后台继续处理，请稍后刷新对话查看回复。',
                timestamp: new Date().toISOString(),
                processing_time: 60, // 预设超时时间
                is_timeout_message: true, // 添加标识字段
                conversation_id: conversationId
              }
            };
            
            resolve(responseWithTimeout);
            return;
          } catch (fallbackError) {
            console.error('[AIStore] 后备请求失败:', fallbackError);
          }
        }
        
        // 移除挂起的请求
        const cacheKey = `${conversationId}-${content}`;
        pendingRequests.delete(cacheKey);
        
        // 构建更有信息量的错误消息
        const errorMessage = isTimeout 
          ? 'AI响应超时，请稍后查看是否有回复' 
          : (errorDetail 
            ? `请求处理失败 (${errorStatus}): ${errorDetail}` 
            : '服务器处理请求时出错，请稍后再试');
        
        reject(new Error(errorMessage));
      }
    });
    
    // 记录挂起的请求
    const cacheKey = `${conversationId}-${content}`;
    pendingRequests.set(cacheKey, {
      id: requestId,
      timestamp: Date.now(),
      promise: requestPromise
    });
    
    return requestPromise;
  };
  
  // 切换使用本地或远程模型
  const toggleModelSource = (useLocal: boolean) => {
    useLocalModel.value = useLocal;
    console.log(`已切换到${useLocal ? '本地' : '远程'}模型`);
  };
  
  // 设置本地模型名称
  const setLocalModelName = (modelName: string) => {
    localModelName.value = modelName;
    // 保存到localStorage以便下次使用
    localStorage.setItem('ai_assistant_model', modelName);
    console.log(`已设置本地模型: ${modelName} (已保存到本地存储)`);
  };
  
  // 切换思考模式
  const toggleThinkMode = (enabled: boolean) => {
    useThinkMode.value = enabled;
    console.log(`已${enabled ? '开启' : '关闭'}思考模式`);
  };
  
  // 删除对话
  const deleteConversation = async (conversationId: number): Promise<void> => {
    await http.delete(`/ai-assistant/conversations/${conversationId}`);
    conversations.value = conversations.value.filter(c => c.id !== conversationId);
  };
  
  // 删除消息
  const deleteMessage = async (messageId: number, conversationId: number): Promise<void> => {
    await http.delete(`/ai-assistant/conversations/${conversationId}/messages/${messageId}`);
  };
  
  return {
    conversations,
    useLocalModel,
    localModelName,
    useThinkMode,
    aiModelSource,
    aiThinkModeStatus,
    getConversations,
    createConversation,
    getMessages,
    sendMessage,
    deleteConversation,
    deleteMessage,
    toggleModelSource,
    setLocalModelName,
    toggleThinkMode
  };
});
