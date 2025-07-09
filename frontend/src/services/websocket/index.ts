import { ref, onMounted, onUnmounted } from 'vue';
import { useUserStore } from '@/stores/user';

export function useWebSocket(endpoint: string) {
  const userStore = useUserStore();
  const socket = ref<WebSocket | null>(null);
  const isConnected = ref(false);
  const messages = ref<any[]>([]);
  
  const connect = () => {
    const baseUrl = import.meta.env.VITE_WS_BASE_URL;
    const token = userStore.token;
    
    socket.value = new WebSocket(`${baseUrl}${endpoint}?token=${token}`);
    
    socket.value.onopen = () => {
      isConnected.value = true;
    };
    
    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data);
      messages.value.push(data);
    };
    
    socket.value.onclose = () => {
      isConnected.value = false;
    };
    
    socket.value.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };
  
  const disconnect = () => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.close();
    }
  };
  
  const send = (data: any) => {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify(data));
    }
  };
  
  onMounted(() => {
    if (userStore.isLoggedIn) {
      connect();
    }
  });
  
  onUnmounted(() => {
    disconnect();
  });
  
  return {
    socket,
    isConnected,
    messages,
    connect,
    disconnect,
    send
  };
}
