<template>
  <div class="system-settings">
    <n-page-header subtitle="管理系统配置和设置">
      <template #title>
        <div class="flex items-center">
          <n-icon size="24" class="mr-2">
            <settings-outlined />
          </n-icon>
          系统设置
        </div>
      </template>
    </n-page-header>

    <div class="mt-4 grid grid-cols-1 gap-6">
      <n-tab-pane name="general">
        <n-tabs type="line" animated>
          <n-tab-pane name="general" tab="常规设置">
            <general-settings />
          </n-tab-pane>
          
          <n-tab-pane name="websocket" tab="WebSocket设置">
            <websocket-settings />
          </n-tab-pane>
          
          <n-tab-pane name="appearance" tab="外观设置">
            <appearance-settings />
          </n-tab-pane>
          
          <n-tab-pane name="data" tab="数据设置">
            <data-settings />
          </n-tab-pane>
          
          <n-tab-pane v-if="isElectron" name="desktop" tab="桌面应用">
            <electron-settings />
          </n-tab-pane>
        </n-tabs>
      </n-tab-pane>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NPageHeader, NIcon, NTabs, NTabPane } from 'naive-ui';
import SettingsOutlined from '@vicons/material/SettingsOutlined';
import GeneralSettings from '@/components/settings/GeneralSettings.vue';
import WebsocketSettings from '@/components/settings/WebsocketSettings.vue';
import AppearanceSettings from '@/components/settings/AppearanceSettings.vue';
import DataSettings from '@/components/settings/DataSettings.vue';
import ElectronSettings from '@/components/settings/ElectronSettings.vue';
import { isElectron } from '@/utils/electron';
</script>

<style scoped>
.system-settings {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.mr-2 {
  margin-right: 8px;
}

.mt-4 {
  margin-top: 16px;
}

.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.gap-6 {
  gap: 24px;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}
</style> 