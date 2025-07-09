<template>
  <footer class="footer" :class="{ 'dark-theme': isDarkMode }">
    <div class="footer-container">
      <div class="footer-left">
        <p class="copyright">© {{ currentYear }} AuraClass. 保留所有权利</p>
      </div>
      <div class="footer-right">
        <p class="version">版本 {{ version }}</p>
        <div class="links">
          <a href="#" class="footer-link">使用条款</a>
          <a href="#" class="footer-link">隐私政策</a>
          <a href="#" class="footer-link">联系我们</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useThemeStore } from '@/stores/theme';

// 获取当前年份
const currentYear = computed(() => new Date().getFullYear());

// 应用版本号
const version = ref('1.0.0');

// 主题状态
const themeStore = useThemeStore();
const isDarkMode = computed(() => themeStore.darkMode);
</script>

<style scoped>
.footer {
  width: 100%;
  padding: 1rem 0;
  background-color: #fff;
  border-top: 1px solid #e5e7eb;
  margin-top: auto;
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

.footer.dark-theme {
  background-color: #1a1a1a;
  border-top: 1px solid #333;
  color: #e5e5e5;
}

.footer-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px;
}

.footer-left, .footer-right {
  display: flex;
  align-items: center;
}

.footer-right {
  gap: 24px;
}

.copyright, .version {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
  transition: color 0.3s ease;
}

.dark-theme .copyright, 
.dark-theme .version {
  color: #9ca3af;
}

.links {
  display: flex;
  gap: 16px;
}

.footer-link {
  color: #6b7280;
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.dark-theme .footer-link {
  color: #9ca3af;
}

.footer-link:hover {
  color: #4f46e5;
}

.dark-theme .footer-link:hover {
  color: #6366f1;
}

@media (max-width: 640px) {
  .footer-container {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
  
  .footer-right {
    flex-direction: column;
    gap: 8px;
  }
  
  .links {
    justify-content: center;
  }
}
</style> 