<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NForm, NFormItem, NInput, NButton, NSwitch, NSelect, NInputNumber, NSpace, NCard, NDivider, useMessage } from 'naive-ui';
import http from '@/services/http';

const message = useMessage();

// 系统设置表单
const systemForm = ref({
  PROJECT_NAME: '',
  DATA_BACKUP_DAYS: 7,
  LOG_RETENTION_DAYS: 30,
  ENABLE_NOTIFICATIONS: true,
  ENABLE_AUDIT_LOG: true,
  CACHE_TIMEOUT: 60,
  DATABASE_URL: '',
  SECRET_KEY: '',
  DEBUG: false,
  FRONTEND_URL: '',
  ALLOWED_ORIGINS: '',
  ALGORITHM: '',
  ACCESS_TOKEN_EXPIRE_MINUTES: 30
});

// 检查ALLOWED_ORIGINS格式是否有效
const validateAllowedOrigins = (origins: string): string => {
  if (!origins) return origins;
  
  const originList = origins.split(',');
  const validOrigins = originList.map(origin => {
    origin = origin.trim();
    // 检查是否包含无效的通配符格式
    if (origin.includes('*') && 
        !origin.endsWith('*') && 
        !origin.startsWith('*')) {
      
      // 处理端口中的通配符
      if (origin.includes(':') && 
          origin.split(':').pop()?.includes('*') && 
          origin.split(':').pop() !== '*') {
        
        console.warn('检测到无效的CORS通配符格式:', origin);
        // 替换为有效格式
        if (origin.startsWith('http://localhost:')) {
          return 'http://localhost:8200';
        }
        // 其他情况去除通配符
        return origin.replace(/\*/g, '');
      }
    }
    return origin;
  });
  
  return validOrigins.join(',');
};

// 原始配置用于比较是否有变更
const originalConfig = ref({});

// 加载状态
const isLoading = ref(false);
const isSaving = ref(false);
const isRestarting = ref(false);

// 加载系统配置
const loadSystemConfig = async () => {
  isLoading.value = true;
  console.log('开始加载系统配置...');
  
  try {
    // 确保路径正确，使用不带前缀的路径，因为http实例已经配置了baseURL
    const response = await http.get('/admin/config');
    console.log('系统配置API响应:', response);
    
    if (response && typeof response === 'object') {
      // 确保访问正确的数据结构
      const configData = response.data || response;
      console.log('配置数据:', configData);
      
      systemForm.value = {
        PROJECT_NAME: configData.PROJECT_NAME || '',
        DATA_BACKUP_DAYS: configData.DATA_BACKUP_DAYS || 7,
        LOG_RETENTION_DAYS: configData.LOG_RETENTION_DAYS || 30,
        ENABLE_NOTIFICATIONS: configData.ENABLE_NOTIFICATIONS || true,
        ENABLE_AUDIT_LOG: configData.ENABLE_AUDIT_LOG || true,
        CACHE_TIMEOUT: configData.CACHE_TIMEOUT || 60,
        DATABASE_URL: configData.DATABASE_URL || '',
        SECRET_KEY: configData.SECRET_KEY || '',
        DEBUG: configData.DEBUG || false,
        FRONTEND_URL: configData.FRONTEND_URL || '',
        ALLOWED_ORIGINS: configData.ALLOWED_ORIGINS || '',
        ALGORITHM: configData.ALGORITHM || '',
        ACCESS_TOKEN_EXPIRE_MINUTES: configData.ACCESS_TOKEN_EXPIRE_MINUTES || 30
      };
      
      originalConfig.value = { ...systemForm.value };
      console.log('已加载系统配置:', systemForm.value);
      message.success('配置加载成功');
    } else {
      console.error('API返回的数据格式不正确:', response);
      message.error('配置数据格式不正确');
    }
  } catch (error: any) {
    console.error('加载系统配置失败:', error);
    
    // 详细的错误信息
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('错误状态码:', error.response.status);
      console.error('错误数据:', error.response.data);
      
      if (error.response.status === 403) {
        message.error('您没有权限访问系统配置');
      } else {
        message.error(`加载配置失败: ${error.response.status} - ${error.response.data?.detail || '未知错误'}`);
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('未收到服务器响应:', error.request);
      message.error('服务器未响应配置请求');
    } else {
      // 请求设置时发生错误
      console.error('请求错误:', error.message);
      message.error(`请求错误: ${error.message}`);
    }
  } finally {
    isLoading.value = false;
  }
};

// 保存系统设置
const handleSaveSettings = async () => {
  isSaving.value = true;
  console.log('开始保存系统配置...');
  
  try {
    // 验证并清理ALLOWED_ORIGINS
    systemForm.value.ALLOWED_ORIGINS = validateAllowedOrigins(systemForm.value.ALLOWED_ORIGINS);
    
    const response = await http.put('/admin/config', systemForm.value);
    console.log('保存配置响应:', response);
    originalConfig.value = { ...systemForm.value };
    message.success('系统配置已更新');
  } catch (error: any) {
    console.error('保存配置失败:', error);
    
    if (error.response) {
      message.error(`保存失败: ${error.response.status} - ${error.response.data?.detail || '未知错误'}`);
    } else if (error.request) {
      message.error('服务器未响应保存请求');
    } else {
      message.error(`请求错误: ${error.message}`);
    }
  } finally {
    isSaving.value = false;
  }
};

// 重启后端服务
const handleRestartServer = async () => {
  isRestarting.value = true;
  console.log('开始重启服务器...');
  
  try {
    const response = await http.post('/admin/restart');
    console.log('重启服务器响应:', response);
    message.success('服务器正在重启，请稍候...');
    
    // 等待服务器重启完成
    setTimeout(() => {
      checkServerStatus();
    }, 5000);
    
  } catch (error: any) {
    console.error('重启服务器失败:', error);
    
    if (error.response) {
      message.error(`重启失败: ${error.response.status} - ${error.response.data?.detail || '未知错误'}`);
    } else if (error.request) {
      message.error('服务器未响应重启请求');
    } else {
      message.error(`请求错误: ${error.message}`);
    }
    
    isRestarting.value = false;
  }
};

// 检查服务器状态
const checkServerStatus = async () => {
  console.log('检查服务器状态...');
  try {
    const response = await http.get('/health');
    console.log('服务器状态检查响应:', response);
    message.success('服务器已重启并恢复运行');
    isRestarting.value = false;
  } catch (error) {
    console.log('服务器可能仍在重启中:', error);
    // 服务器可能仍在重启中，继续等待
    setTimeout(() => {
      checkServerStatus();
    }, 2000);
  }
};

// 检查配置是否有变更
const hasConfigChanged = () => {
  return JSON.stringify(systemForm.value) !== JSON.stringify(originalConfig.value);
};

// 组件挂载时加载配置
onMounted(() => {
  console.log('系统设置组件已挂载');
  loadSystemConfig();
});
</script>

<template>
  <div class="system-settings">
    <NCard title="系统基本配置" :loading="isLoading">
      <NForm :model="systemForm" label-placement="left" label-width="180">
        <NFormItem label="系统名称" path="PROJECT_NAME">
          <NInput v-model:value="systemForm.PROJECT_NAME" placeholder="输入系统名称" />
        </NFormItem>
        
        <NFormItem label="数据备份保留天数" path="DATA_BACKUP_DAYS">
          <NInputNumber v-model:value="systemForm.DATA_BACKUP_DAYS" :min="1" :max="90" />
        </NFormItem>
        
        <NFormItem label="日志保留天数" path="LOG_RETENTION_DAYS">
          <NInputNumber v-model:value="systemForm.LOG_RETENTION_DAYS" :min="1" :max="365" />
        </NFormItem>
        
        <NFormItem label="启用系统通知">
          <NSwitch v-model:value="systemForm.ENABLE_NOTIFICATIONS" />
        </NFormItem>
        
        <NFormItem label="启用审计日志">
          <NSwitch v-model:value="systemForm.ENABLE_AUDIT_LOG" />
        </NFormItem>
        
        <NFormItem label="缓存超时时间(分钟)" path="CACHE_TIMEOUT">
          <NInputNumber v-model:value="systemForm.CACHE_TIMEOUT" :min="5" :max="1440" />
        </NFormItem>
      </NForm>
    </NCard>
    
    <NDivider />
    
    <NCard title="高级配置" :loading="isLoading">
      <NForm :model="systemForm" label-placement="left" label-width="180">
        <NFormItem label="数据库连接字符串" path="DATABASE_URL">
          <NInput v-model:value="systemForm.DATABASE_URL" placeholder="数据库连接字符串" type="password" show-password-on="click" />
        </NFormItem>
        
        <NFormItem label="API密钥" path="SECRET_KEY">
          <NInput v-model:value="systemForm.SECRET_KEY" placeholder="API密钥" type="password" show-password-on="click" />
        </NFormItem>
        
        <NFormItem label="API调试模式">
          <NSwitch v-model:value="systemForm.DEBUG" />
        </NFormItem>
        
        <NFormItem label="前端URL" path="FRONTEND_URL">
          <NInput v-model:value="systemForm.FRONTEND_URL" placeholder="前端URL地址" />
        </NFormItem>
        
        <NFormItem label="允许跨域来源" path="ALLOWED_ORIGINS">
          <NInput v-model:value="systemForm.ALLOWED_ORIGINS" placeholder="允许跨域的源（以逗号分隔）" />
        </NFormItem>
        
        <NFormItem label="JWT算法" path="ALGORITHM">
          <NInput v-model:value="systemForm.ALGORITHM" placeholder="JWT加密算法" />
        </NFormItem>
        
        <NFormItem label="Token过期时间(分钟)" path="ACCESS_TOKEN_EXPIRE_MINUTES">
          <NInputNumber v-model:value="systemForm.ACCESS_TOKEN_EXPIRE_MINUTES" :min="5" :max="1440" />
        </NFormItem>
      </NForm>
    </NCard>

    <div class="action-buttons">
      <NSpace>
        <NButton 
          type="primary" 
          @click="handleSaveSettings" 
          :loading="isSaving"
          :disabled="!hasConfigChanged() || isRestarting"
        >
          保存配置
        </NButton>
        
        <NButton 
          type="warning" 
          @click="handleRestartServer" 
          :loading="isRestarting"
          :disabled="hasConfigChanged()"
        >
          重启服务器
        </NButton>
        
        <NButton @click="loadSystemConfig" :disabled="isLoading || isSaving || isRestarting">
          重新加载
        </NButton>
      </NSpace>
      
      <div class="tip" v-if="hasConfigChanged()">
        <p>您有未保存的更改，保存后需要重启服务器才能生效</p>
      </div>
      
      <div class="tip" v-else-if="isRestarting">
        <p>服务器正在重启中，请耐心等待...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.system-settings {
  max-width: 800px;
}

.action-buttons {
  margin-top: 20px;
  padding: 16px;
  background-color: #f3f3f3;
  border-radius: 4px;
}

.tip {
  margin-top: 12px;
  font-size: 13px;
  color: #d03050;
}
</style> 