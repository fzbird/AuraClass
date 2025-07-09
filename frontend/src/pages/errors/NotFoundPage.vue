<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-100">
    <div class="max-w-md w-full px-6 py-8 bg-white shadow-md rounded-lg">
      <div class="text-center">
        <h1 class="text-9xl font-bold text-primary mb-2">404</h1>
        <h2 class="text-2xl font-semibold text-gray-800 mb-4">页面未找到</h2>
        <p class="text-gray-600 mb-6">
          很抱歉，您请求的页面不存在或已被移除。
        </p>
        <router-link
          to="/"
          class="inline-block px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
        >
          返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 页面未找到组件
</script>

<style scoped>
.text-primary {
  color: #3366FF;
}

.bg-primary {
  background-color: #3366FF;
}

.hover\:bg-primary-dark:hover {
  background-color: #2952CC;
}
</style> 