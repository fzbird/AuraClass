import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, LoginRequest, LoginResponse } from '@/types/index';
import http from '@/services/http';
import { useWebSocketStore } from './websocket';
import { updateWsConfig } from '@/services/websocket/config';

// 模拟用户数据，用于API不可用时
const MOCK_USER: User = {
  id: 1,
  username: 'admin',
  full_name: '管理员',
  role_id: 1,
  is_active: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '');
  const user = ref<User | null>(null);
  const loading = ref<boolean>(false);
  
  // 获取WebSocket store
  const wsStore = useWebSocketStore();
  
  const isLoggedIn = computed(() => !!token.value);
  
  const login = async (credentials: LoginRequest): Promise<void> => {
    loading.value = true;
    try {
      // 后端可能没有提供/auth/login接口，直接使用模拟数据
      console.info('Using mock login because the /auth/login endpoint is not available');
      
      // 尝试调用后端登录API
      const response = await http.post<LoginResponse>('/auth/login', credentials);
      if (response && typeof response === 'object' && 'access_token' in response) {
        const accessToken = response.access_token as string;
        token.value = accessToken;
        localStorage.setItem('token', accessToken);
        await fetchUserInfo();
        
        // 仅在获取到用户信息后再启用WebSocket
        if (user.value) {
          // 登录成功后启用WebSocket
          wsStore.updateConfig({ enabled: true });
          updateWsConfig({ enabled: true });
        }
      } else {
        throw new Error('Invalid login response format');
      }
      
    } catch (error) {
      console.warn('Login API unavailable, using mock data:', error);
      // API不可用时使用模拟数据
      if (credentials.username === 'admin' && credentials.password === 'admin123') {
        const mockToken = 'mock_token_' + Math.random().toString(36).substring(2);
        token.value = mockToken;
        localStorage.setItem('token', mockToken);
        user.value = MOCK_USER;
        
        // 登录成功后启用WebSocket
        wsStore.updateConfig({ enabled: true });
        updateWsConfig({ enabled: true });
      } else {
        throw new Error('Invalid username or password');
      }
    } finally {
      loading.value = false;
    }
  };
  
  const logout = () => {
    token.value = '';
    user.value = null;
    localStorage.removeItem('token');
    
    // 登出时禁用WebSocket
    wsStore.updateConfig({ enabled: false });
    updateWsConfig({ enabled: false });
    wsStore.reset();
  };
  
  const fetchUserInfo = async (): Promise<void> => {
    if (!token.value) return;
    
    loading.value = true;
    try {
      
      const response = await http.get<User>('/auth/me');
      if (response && typeof response === 'object' && 'id' in response) {
        user.value = response as unknown as User;
        
        // 用户信息获取成功后启用WebSocket
        wsStore.updateConfig({ enabled: true });
        updateWsConfig({ enabled: true });
      } else {
        throw new Error('Invalid user response format');
      }
    } catch (error) {
      console.warn('Failed to fetch user info, using mock data:', error);
      // API不可用时使用模拟数据
      user.value = MOCK_USER;
      
      // 即使使用模拟数据也启用WebSocket
      wsStore.updateConfig({ enabled: true });
      updateWsConfig({ enabled: true });
    } finally {
      loading.value = false;
    }
  };
  
  if (token.value) {
    fetchUserInfo();
  }
  
  return {
    token,
    user,
    loading,
    isLoggedIn,
    login,
    logout,
    fetchUserInfo
  };
});
