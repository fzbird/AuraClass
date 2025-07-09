<template>
  <div class="ranking-list">
    <div v-for="(item, index) in items" :key="item.id" class="ranking-item">
      <div class="flex items-center py-3 hover:bg-gray-50 px-2 rounded">
        <!-- 排名 -->
        <div 
          class="ranking-number flex-shrink-0 w-8 h-8 flex items-center justify-center mr-2 font-bold"
          :class="getRankClass(index + 1)"
        >
          {{ index + 1 }}
        </div>
        
        <!-- 名称 -->
        <div class="flex-grow truncate">
          {{ item.name }}
        </div>
        
        <!-- 数值 -->
        <div class="font-medium ml-4">
          {{ item.value }}{{ item.suffix || '' }}
        </div>
      </div>
    </div>
    
    <div v-if="items.length === 0" class="text-center py-4 text-gray-500">
      暂无数据
    </div>
  </div>
</template>

<script setup lang="ts">
interface RankingItem {
  id: number;
  name: string;
  value: number | string;
  rank?: number;
  suffix?: string;
}

const props = defineProps({
  items: {
    type: Array as () => RankingItem[],
    required: true
  }
});

// 根据排名获取样式类
const getRankClass = (rank: number): string => {
  if (rank === 1) {
    return 'bg-red-500 text-white';
  } else if (rank === 2) {
    return 'bg-orange-500 text-white';
  } else if (rank === 3) {
    return 'bg-yellow-500 text-white';
  }
  return 'bg-gray-200';
};
</script>

<style scoped>
.ranking-list {
  width: 100%;
  overflow: hidden;
}

.ranking-item:not(:last-child) {
  border-bottom: 1px solid #f0f0f0;
}

.ranking-number {
  border-radius: 50%;
  font-size: 14px;
}
</style>
