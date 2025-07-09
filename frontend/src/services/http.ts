import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { useUserStore } from '@/stores/user';
import router from '@/router';

// 扩展InternalAxiosRequestConfig类型，添加我们自定义的属性
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    _requestKey?: string;
    _formDataFields?: string[];
  }
}

// 定义后端API的响应结构
export interface ApiResponse<T = any> {
  data: T;
  meta?: {
    pagination?: {
      page?: number;
      size?: number;
      total?: number;
    };
    [key: string]: any;
  };
  [key: string]: any;
}

// 请求去重缓存
interface RequestCache {
  timestamp: number;
  promise: Promise<any>;
}
const pendingRequests = new Map<string, RequestCache>();

// 生成请求的唯一标识 - 改进FormData处理
const getRequestKey = (config: InternalAxiosRequestConfig): string => {
  const { method, url, params } = config;
  let dataString = '{}';
  
  // 特殊处理FormData对象
  if (config.data instanceof FormData) {
    try {
      // 提取FormData中的关键字段，忽略文件内容
      const formDataObj: Record<string, string> = {};
      
      // 处理已知的关键字段
      const keyFields = ['content', 'role', 'useLocalModel', 'modelName', 'useThinkMode', 'conversation_id'];
      keyFields.forEach(field => {
        if (config.data instanceof FormData && config.data.has(field)) {
          formDataObj[field] = config.data.get(field) as string;
        }
      });
      
      // 记录处理的字段名，用于调试
      config._formDataFields = Object.keys(formDataObj);
      
      // 只序列化非文件字段，忽略文件内容以实现去重
      dataString = JSON.stringify(formDataObj);
    } catch (e) {
      console.error('序列化FormData时出错:', e);
      // 使用时间戳作为备用，确保请求不会被错误地合并
      dataString = `FormData-${Date.now()}`;
    }
  } else if (config.data && typeof config.data === 'object') {
    // 常规对象处理
    try {
      dataString = JSON.stringify(config.data);
    } catch (e) {
      console.error('序列化请求数据时出错:', e);
      dataString = `${Date.now()}`;
    }
  }
  
  // 生成请求键
  const requestKey = `${method}-${url}-${JSON.stringify(params || {})}-${dataString}`;
  
  // 添加调试日志
  if (url && (url.includes('/ai-assistant/conversations') || url.includes('/messages'))) {
    console.log(`生成请求键: ${requestKey.substring(0, 100)}...`);
  }
  
  return requestKey;
};

// 清理过期的请求缓存（超过指定时间）
const cleanupPendingRequests = () => {
  const now = Date.now();
  let cleanCount = 0;
  pendingRequests.forEach((cache, key) => {
    // 清理超过10秒的缓存
    if (now - cache.timestamp > 10000) {
      pendingRequests.delete(key);
      cleanCount++;
    }
  });
  
  if (cleanCount > 0) {
    console.log(`已清理 ${cleanCount} 条过期请求缓存, 剩余 ${pendingRequests.size} 条`);
  }
};

// 定期清理过期请求
setInterval(cleanupPendingRequests, 30000);

const createHttp = (): AxiosInstance => {
  // 确保baseURL只添加一次/api/v1前缀
  const baseURL = '/api/v1';
  console.log('API 基础URL:', baseURL);
  
  const http = axios.create({
    baseURL,
    timeout: 60000, // 超时时间增加到60秒，以适应AI模型调用的延迟
    headers: {
      'Content-Type': 'application/json'
    }
  });

  // 请求拦截器
  http.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const userStore = useUserStore();
      if (userStore.token && config.headers) {
        config.headers.Authorization = `Bearer ${userStore.token}`;
        // 调试信息
        console.debug(`添加认证头: ${config.headers.Authorization} 到 ${config.url}`);
      } else {
        console.warn(`请求 ${config.url} 没有认证Token`);
      }
      
      // 特殊处理登录请求，使用表单格式
      if (config.url && config.url.endsWith('/auth/login') && config.method === 'post') {
        config.headers['Content-Type'] = 'application/x-www-form-urlencoded';
        // 将请求数据转换为表单格式
        const formData = new URLSearchParams();
        if (config.data) {
          // 使用类型断言确保Object.entries可以正确处理
          const entries = Object.entries(config.data as Record<string, unknown>);
          entries.forEach(([key, value]) => {
            formData.append(key, String(value));
          });
        }
        config.data = formData;
      }
      
      // 防止重复的API路径
      if (config.url && config.url.startsWith('/api/v1/')) {
        console.warn(`检测到重复的API路径前缀: ${config.url}`);
        config.url = config.url.replace('/api/v1/', '/');
        console.log(`已修正为: ${config.url}`);
      }
      
      // 只对特定接口启用去重逻辑
      if (config.url && (
        config.url.includes('/ai-assistant/conversations') || 
        config.url.includes('/messages')
      )) {
        // 检查是否为POST请求（创建消息）
        if (config.method?.toLowerCase() === 'post') {
          const requestKey = getRequestKey(config);
          
          // 检查是否存在相同的请求
          if (pendingRequests.has(requestKey)) {
            const cache = pendingRequests.get(requestKey)!;
            const now = Date.now();
            
            // 如果请求在5秒内重复发送，直接返回缓存的Promise
            if (now - cache.timestamp < 5000) {
              console.warn(`检测到重复请求: ${config.method} ${config.url}`);
              if (config.data instanceof FormData) {
                console.warn(`FormData字段: ${config._formDataFields?.join(', ')}`);
              }
              console.warn('使用缓存的请求结果，避免重复发送');
              
              // 设置取消标志，告诉axios不要发送这个请求
              config.signal = AbortSignal.abort('请求被取消 - 重复请求');
              
              // 返回原始配置使请求继续，但会被axios的信号终止
              return config;
            }
          }
          
          // 记录这个请求的配置，但还没有缓存结果
          // 结果会在响应拦截器中缓存
          config._requestKey = requestKey;
        }
      }
      
      console.log(`发送请求: ${config.method?.toUpperCase()} ${config.url}`, config.params || {});
      return config;
    },
    (error: AxiosError) => Promise.reject(error)
  );

  // 响应拦截器
  http.interceptors.response.use(
    (response: AxiosResponse) => {
      console.log(`请求成功: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
      
      // 缓存AI助手相关请求的结果
      const config = response.config;
      if (config._requestKey && (
        config.url?.includes('/ai-assistant/conversations') || 
        config.url?.includes('/messages')
      )) {
        // 记录请求结果到缓存
        const requestKey = config._requestKey as string;
        pendingRequests.set(requestKey, {
          timestamp: Date.now(),
          promise: Promise.resolve(response.data)
        });
        
        // 记录缓存状态
        console.log(`已缓存请求结果, 当前缓存数: ${pendingRequests.size}`);
      }
      
      // 检查响应类型和数据格式，提供更详细的调试信息
      if (config.url?.includes('/ai-assistant')) {
        console.log(`AI接口调用返回数据结构: ${typeof response.data}`);
        console.log(`是否为数组: ${Array.isArray(response.data)}`);
        
        if (typeof response.data === 'object' && response.data !== null) {
          console.log(`响应对象键: ${Object.keys(response.data).join(', ')}`);
          
          if ('data' in response.data) {
            console.log(`data内部类型: ${typeof response.data.data}`);
            console.log(`是否数组: ${Array.isArray(response.data.data)}`);
          }
        }
      }
      
      // 标准化响应处理: 如果响应有data字段且不是我们需要的直接数据，则返回data字段
      if (response.data && typeof response.data === 'object' && 'data' in response.data) {
        // 检查data属性是否确实是我们需要的数据，而不是整个响应都应该返回的情况
        if (
          // 排除标准响应结构中data本来就是数据一部分的情况
          !('meta' in response.data) && 
          !('pagination' in response.data) &&
          !('timestamp' in response.data) &&
          !('status' in response.data)
        ) {
          // 这可能是一个嵌套响应，直接返回内部data
          console.log('检测到嵌套data结构，返回内部data');
          return response.data.data;
        }
      }
      
      // 特殊处理AI助手接口
      if (config.url?.includes('/ai-assistant')) {
        const aiResponse = response.data;
        
        // 检查数据格式并确保AI响应正确返回
        if (aiResponse && typeof aiResponse === 'object') {
          // 确保ai_message在返回给前端代码时保留
          if ('ai_message' in aiResponse) {
            console.log('保留ai_message结构供前端处理');
            
            // 确保处理时间字段类型正确处理
            if (aiResponse.ai_message && 'processing_time' in aiResponse.ai_message) {
              // 确保processing_time是数字类型
              if (typeof aiResponse.ai_message.processing_time === 'string') {
                aiResponse.ai_message.processing_time = parseFloat(aiResponse.ai_message.processing_time);
              }
              console.log(`AI消息处理时间: ${aiResponse.ai_message.processing_time}s`);
            }
            
            // 确保消息内容非空
            if (aiResponse.ai_message && (!aiResponse.ai_message.content || aiResponse.ai_message.content.trim() === '')) {
              console.warn('AI消息内容为空，将设置默认内容');
              aiResponse.ai_message.content = '(系统返回了空内容)';
            }
            
            return aiResponse;
          }
          
          // 如果响应本身就是消息对象格式（包含role, content等字段）
          if ('role' in aiResponse && 'content' in aiResponse) {
            // 确保处理时间字段类型正确处理
            if ('processing_time' in aiResponse) {
              // 确保processing_time是数字类型
              if (typeof aiResponse.processing_time === 'string') {
                aiResponse.processing_time = parseFloat(aiResponse.processing_time);
              }
              console.log(`AI消息处理时间: ${aiResponse.processing_time}s`);
            }
            
            // 确保消息内容非空
            if (!aiResponse.content || aiResponse.content.trim() === '') {
              console.warn('AI消息内容为空，将设置默认内容');
              aiResponse.content = '(系统返回了空内容)';
            }
          }
        }
      }
      
      // 直接返回响应数据对象
      return response.data;
    },
    (error: AxiosError) => {
      const userStore = useUserStore();
      
      // 如果是被我们的请求去重逻辑取消的请求，直接返回缓存的结果
      if (error.name === 'AbortError' && 
          error.message && 
          error.message.includes('请求被取消 - 重复请求')) {
        // 从原始请求中获取请求键
        const config = error.config as InternalAxiosRequestConfig;
        const requestKey = getRequestKey(config);
        
        if (pendingRequests.has(requestKey)) {
          console.log('返回缓存的请求结果，而不是重新发送请求');
          return pendingRequests.get(requestKey)!.promise;
        }
      }
      
      console.error(`请求失败: ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.data || error.message);
      
      // 处理未授权错误
      if (error.response && error.response.status === 401) {
        userStore.logout();
        
        // 获取当前路径，但排除现有的redirect参数
        const currentPath = router.currentRoute.value.path;
        const isLoginPage = currentPath.includes('/auth/login');
        
        // 如果已经在登录页，不添加redirect参数，避免循环
        if (isLoginPage) {
          router.push({ name: 'Login' });
        } else {
          router.push({ name: 'Login', query: { redirect: currentPath } });
        }
      }
      // 处理禁止访问错误，保持某些请求的连续性
      else if (error.response && error.response.status === 403) {
        // 不做路由跳转，让调用方自行处理
        console.warn('权限不足，无法访问资源:', error.config?.url);

        // 对特定的API请求返回一个空数据结构而不是抛出异常
        if (error.config?.url?.includes('/quant-item-categories') ||
            error.config?.url?.includes('/categories/quant-items')) {
          console.log('对量化项目分类请求返回空数据');
          return { data: [] };
        }
      }
      
      return Promise.reject(error);
    }
  );

  return http;
};

const http = createHttp();
export default http;
