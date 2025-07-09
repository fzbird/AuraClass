<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">系统设置</h1>
    </div>
    
    <n-tabs type="line" animated>
      <n-tab-pane name="profile" tab="个人信息">
        <user-profile-settings :user="currentUser" @update:user="handleUserUpdate" />
      </n-tab-pane>
      
      <n-tab-pane name="account" tab="账号安全">
        <account-security-settings />
      </n-tab-pane>
      
      <n-tab-pane v-if="hasAdminPermission" name="system" tab="系统设置">
        <system-settings />
      </n-tab-pane>
      
      <n-tab-pane v-if="hasAdminPermission" name="permissions" tab="权限管理">
        <permission-management />
      </n-tab-pane>
      
      <n-tab-pane name="appearance" tab="界面设置">
        <appearance-settings />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { NTabs, NTabPane, useMessage } from 'naive-ui';
import { useUserStore } from '@/stores/user';
import { usePermissionStore } from '@/stores/permission';
import http from '@/services/http';
import type { User } from '@/types';
import UserProfileSettings from '@/components/settings/UserProfileSettings.vue';
import AccountSecuritySettings from '@/components/settings/AccountSecuritySettings.vue';
import SystemSettings from '@/components/settings/SystemSettings.vue';
import PermissionManagement from '@/components/settings/PermissionManagement.vue';
import AppearanceSettings from '@/components/settings/AppearanceSettings.vue';

const message = useMessage();
const userStore = useUserStore();
const permissionStore = usePermissionStore();

const currentUser = computed(() => userStore.user);
const hasAdminPermission = computed(() => 
  permissionStore.hasPermission('manage:system') || 
  permissionStore.hasPermission('manage:permissions')
);

onMounted(async () => {
  if (!currentUser.value) {
    try {
      await userStore.fetchUserInfo();
    } catch (error) {
      console.error('Failed to fetch user data:', error);
      message.error('获取用户信息失败');
    }
  }
});

const handleUserUpdate = async (userData: Partial<User>) => {
  try {
    // Update user profile via API then refresh user data
    await http.put('/auth/me', userData);
    await userStore.fetchUserInfo();
    message.success('个人信息更新成功');
  } catch (error) {
    console.error('Failed to update user profile:', error);
    message.error('更新个人信息失败');
  }
};
</script>
