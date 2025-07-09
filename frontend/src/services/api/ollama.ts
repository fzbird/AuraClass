import axios from 'axios';

// Ollama服务的基本配置
const ollamaClient = axios.create({
  baseURL: 'http://192.168.5.117:11434',
  headers: {
    'Content-Type': 'application/json'
  }
});

export interface OllamaResponse {
  response: string;
  model: string;
  created_at: string;
  done: boolean;
  context?: number[];
  total_duration?: number;
  load_duration?: number;
  prompt_eval_count?: number;
  prompt_eval_duration?: number;
  eval_count?: number;
  eval_duration?: number;
}

/**
 * 向Ollama发送请求并获取生成的文本
 * @param prompt 用户的提问内容
 * @param model 使用的模型名称，默认为"llama2"
 * @returns 生成的回复文本
 */
export async function queryOllama(prompt: string, model: string = 'llama2'): Promise<string> {
  try {
    console.log(`向Ollama发送请求，使用模型 ${model}`);
    const response = await ollamaClient.post('/api/generate', {
      model,
      prompt,
      stream: false
    });

    const data = response.data as OllamaResponse;
    console.log('Ollama响应:', data);
    
    return data.response || '无法获取有效回复';
  } catch (error) {
    console.error('Ollama请求失败:', error);
    return '与本地模型通信失败，请检查Ollama服务是否正常运行';
  }
}

/**
 * 获取可用的模型列表
 * @returns 模型列表
 */
export async function getAvailableModels(): Promise<string[]> {
  try {
    const response = await ollamaClient.get('/api/tags');
    
    if (response.data && Array.isArray(response.data.models)) {
      return response.data.models.map((model: any) => model.name);
    }
    
    return ['llama2']; // 默认返回llama2
  } catch (error) {
    console.error('获取Ollama模型列表失败:', error);
    return ['llama2']; // 出错时默认返回llama2
  }
} 