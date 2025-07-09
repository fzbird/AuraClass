<template>
  <div class="page-container" :class="{ 'dark-theme': isDarkMode }">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();
const isDarkMode = computed(() => themeStore.darkMode);
</script>

<style scoped>
.page-container {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 1rem 0.5rem;
  flex: 1;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: background-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
}

.page-container.dark-theme {
  background-color: #1e1e1e;
  color: #e5e5e5;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

@media (min-width: 768px) {
  .page-container {
    padding: 1.5rem 1rem;
  }
}

@media (min-width: 1280px) {
  .page-container {
    padding: 2rem 1.5rem;
  }
}
</style>
