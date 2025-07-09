import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useUserStore } from './user';

export const usePermissionStore = defineStore('permission', () => {
  const userStore = useUserStore();
  
  // 添加初始化状态标记
  const isInitialized = ref(false);
  
  // 用户角色
  const role = computed(() => {
    if (!userStore.user) return null;
    switch (userStore.user.role_id) {
      case 1: return 'admin';
      case 2: return 'teacher';
      case 3: return 'student';
      default: return null;
    }
  });
  
  // 权限映射表
  const permissionMap = ref(new Map<string, string[]>([
    ['admin', ['*']], // 管理员拥有所有权限
    ['teacher', [
      'view:students', 'create:students', 'update:students', 'delete:students',
      'view:quant-items', 'create:quant-items', 'update:quant-items', 'delete:quant-items',
      'view:records', 'create:records', 'update:records', 'delete:records',
      'view:statistics', 'view:notifications', 'create:notifications',
      'use:ai-assistant', 'view:settings'
    ]],
    ['student', [
      'view:own-records', 'view:own-statistics', 'view:notifications', 'use:ai-assistant'
    ]]
  ]));
  
  // 检查是否有特定权限
  const hasPermission = (permission: string): boolean => {
    if (!role.value) return false;
    
    const permissions = permissionMap.value.get(role.value) || [];
    return permissions.includes('*') || permissions.includes(permission);
  };
  
  // 添加加载权限方法
  const loadPermissions = async (): Promise<void> => {
    try {
      // 如果需要从API加载权限，可以在这里添加代码
      // 例如：const response = await fetch('/api/v1/permissions');
      
      // 标记权限已初始化
      isInitialized.value = true;
      console.log('权限加载完成，当前角色:', role.value);
    } catch (error) {
      console.error('加载权限失败:', error);
      throw error;
    }
  };
  
  return {
    isInitialized,
    role,
    hasPermission,
    loadPermissions
  };
});
