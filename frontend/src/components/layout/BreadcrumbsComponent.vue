<template>
  <div class="breadcrumbs-container mb-4">
    <n-breadcrumb>
      <n-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
        <router-link v-if="item.path && index < breadcrumbs.length - 1" :to="item.path">
          {{ item.title }}
        </router-link>
        <span v-else>{{ item.title }}</span>
      </n-breadcrumb-item>
    </n-breadcrumb>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { NBreadcrumb, NBreadcrumbItem } from 'naive-ui';

const route = useRoute();

interface Breadcrumb {
  title: string;
  path?: string;
}

const breadcrumbs = computed<Breadcrumb[]>(() => {
  const breadcrumbItems: Breadcrumb[] = [
    { title: '首页', path: '/' }
  ];
  
  const routeMeta = route.meta;
  const routeTitle = routeMeta.title as string;
  const pathSegments = route.path.split('/').filter(segment => !!segment);
  
  // 当前路由是首页，只显示首页面包屑
  if (route.path === '/') {
    return breadcrumbItems;
  }
  
  // 根据路由路径和 meta 构建面包屑
  if (routeTitle) {
    // 删除'app'路径前缀，确保路径段没有这个关键字
    const filteredSegments = pathSegments.filter(segment => segment !== 'app');
    
    if (route.params.id && filteredSegments.length > 0) {
      // 如果是详情页，添加列表页面包屑
      const listPathSegment = filteredSegments[0];
      // 构建正确的路径，保留'/app'前缀以确保路由跳转正确
      const listPath = `/app/${listPathSegment}`;
      let listTitle = '';
      
      switch (listPathSegment) {
        case 'students':
          listTitle = '学生管理';
          break;
        case 'quant-items':
          listTitle = '量化项目';
          break;
        case 'records':
          listTitle = '量化记录';
          break;
        case 'dashboard':
          listTitle = '数据仪表盘';
          break;
        case 'settings':
          listTitle = '系统设置';
          break;
        default:
          listTitle = listPathSegment;
      }
      
      breadcrumbItems.push({ title: listTitle, path: listPath });
    }
    
    breadcrumbItems.push({ title: routeTitle });
  }
  
  return breadcrumbItems;
});
</script>

<style scoped>
.breadcrumbs-container {
  font-size: 0.875rem;
}
</style>
