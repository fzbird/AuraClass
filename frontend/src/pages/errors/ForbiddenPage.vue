<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-100">
    <div class="max-w-md w-full px-6 py-8 bg-white shadow-md rounded-lg">
      <div class="text-center">
        <h1 class="text-9xl font-bold text-warning mb-2">403</h1>
        <h2 class="text-2xl font-semibold text-gray-800 mb-4">禁止访问</h2>
        <p class="text-gray-600 mb-6">
          很抱歉，您没有权限访问此页面。
        </p>
        <router-link
          to="/"
          class="inline-block px-6 py-2 bg-warning text-white rounded-lg hover:bg-warning-dark transition-colors"
        >
          返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 禁止访问页面组件
</script>

<style scoped>
.text-warning {
  color: #FAAD14;
}

.bg-warning {
  background-color: #FAAD14;
}

.hover\:bg-warning-dark:hover {
  background-color: #D48806;
}
</style> 