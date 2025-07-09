<template>
  <div class="locale-switcher">
    <n-dropdown
      :options="localeOptions"
      :value="currentLocale"
      @select="handleLocaleSelect"
      trigger="hover"
      placement="bottom-end"
      :render-label="renderLabel"
    >
      <n-button 
        :quaternary="true"
        :size="size" 
        class="locale-switcher-button"
      >
        <template #icon>
          <n-icon>
            <translation-outlined />
          </n-icon>
        </template>
        {{ displayMode === 'full' ? currentLocaleName : '' }}
      </n-button>
    </n-dropdown>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n, supportedLocales } from '@/utils/i18n';
import type { LocaleType } from '@/utils/i18n';
import { NDropdown, NButton, NIcon } from 'naive-ui';
import type { DropdownOption } from 'naive-ui';
import TranslationOutlined from '@vicons/antd/es/TranslationOutlined';
import EarthOutlined from '@vicons/antd/es/GlobalOutlined';
import CheckOutlined from '@vicons/antd/es/CheckOutlined';
import { h } from 'vue';

// 组件属性
const props = defineProps({
  size: {
    type: String as () => 'tiny' | 'small' | 'medium' | 'large',
    default: 'small'
  },
  displayMode: {
    type: String as () => 'icon' | 'full' | 'compact',
    default: 'compact' // 'icon': 仅图标, 'full': 图标+文字, 'compact': 紧凑视图
  }
});

// 使用国际化
const { t, currentLocale, changeLocale, isCurrentLocale, getLocaleName } = useI18n();

// 下拉选项
const localeOptions = computed<DropdownOption[]>(() => 
  supportedLocales.map(locale => ({
    label: getLocaleName(locale),
    key: locale,
    icon: () => h(EarthOutlined)
  }))
);

// 当前语言名称
const currentLocaleName = computed(() => 
  getLocaleName(currentLocale.value)
);

// 处理语言选择
const handleLocaleSelect = (key: string) => {
  changeLocale(key as LocaleType);
};

// 渲染下拉标签
const renderLabel = (option: DropdownOption) => {
  return h('div', {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      width: '100%'
    }
  }, [
    h('span', {}, option.label as string),
    isCurrentLocale(option.key as LocaleType) ? h(CheckOutlined, {
      style: {
        marginLeft: '8px',
        color: 'var(--n-primary-color)'
      }
    }) : null
  ]);
};
</script>

<style scoped>
.locale-switcher {
  display: inline-flex;
  align-items: center;
}

.locale-switcher-button {
  padding: var(--padding, 0 8px);
}
</style> 