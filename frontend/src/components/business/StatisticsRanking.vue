<template>
  <div>
    <n-tabs type="line" :default-value="rankingType" @update:value="handleRankingTypeChange">
      <n-tab-pane name="total" tab="总分排名">
        <student-ranking-table 
          :data="sortedRankings" 
          :loading="loading" 
          score-field="total_score"
          description="总分排名展示学生在所有量化项目中的累计得分情况（加分与减分的净得分）"
        />
      </n-tab-pane>
      
      <n-tab-pane name="positive" tab="加分排名">
        <student-ranking-table 
          :data="sortedPositiveRankings" 
          :loading="loading" 
          score-field="positive_score"
          description="加分排名展示学生在加分项目中的累计得分情况（不含减分项目）"
        />
      </n-tab-pane>
      
      <n-tab-pane name="negative" tab="减分排名">
        <student-ranking-table 
          :data="sortedNegativeRankings" 
          :loading="loading" 
          score-field="negative_score"
          description="减分排名仅显示负分记录，数值从小到大排序，减分越多排名越靠前"
        />
      </n-tab-pane>
      
      <n-tab-pane name="count" tab="记录数排名">
        <student-ranking-table 
          :data="sortedCountRankings" 
          :loading="loading" 
          score-field="record_count"
          score-label="记录数"
          description="记录数排名展示学生的记录总条数，按记录数从高到低排序"
        />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { NTabs, NTabPane } from 'naive-ui';
import StudentRankingTable from './StudentRankingTable.vue';

interface StudentRanking {
  id?: number;
  name?: string;
  class_name?: string;
  total_score?: number;
  positive_score?: number;
  negative_score?: number;
  record_count?: number;
  total_records?: number;
  positive?: number;
  negative?: number;
  rank?: number;
  [key: string]: any;
}

const props = defineProps({
  rankings: {
    type: Array as () => StudentRanking[],
    default: () => []
  }
});

const loading = ref(false);
const rankingType = ref('total');

const handleRankingTypeChange = (value: string) => {
  rankingType.value = value;
};

// 总分排名
const sortedRankings = computed(() => {
  return [...props.rankings].sort((a, b) => (b.total_score || 0) - (a.total_score || 0))
    .map((student, index) => ({
      ...student,
      rank: index + 1
    }));
});

// 加分排名
const sortedPositiveRankings = computed(() => {
  const rankingsWithPositive = [...props.rankings].map(student => ({
    ...student,
    positive_score: student.positive_score !== undefined ? student.positive_score : 0
  }));
  
  return rankingsWithPositive
    .sort((a, b) => (b.positive_score || 0) - (a.positive_score || 0))
    .map((student, index) => ({
      ...student,
      rank: index + 1
    }));
});

// 减分排名（仅包含负分，按从小到大排序，即-10排在-5前面）
const sortedNegativeRankings = computed(() => {
  const rankingsWithNegative = [...props.rankings].map(student => ({
    ...student,
    negative_score: student.negative_score !== undefined ? student.negative_score :  0
  }));
  
  // 过滤出negative_score小于0的记录，并按从小到大排序（负数从小到大，即-20比-10小）
  const filteredRankings = rankingsWithNegative
    .filter(student => (student.negative_score || 0) < 0);
  
  // 强制按照negative_score从小到大排序（绝对值从大到小）
  const sortedRankings = filteredRankings
    .sort((a, b) => {
      const scoreA = a.negative_score || 0;
      const scoreB = b.negative_score || 0;
      // 数值越小（绝对值越大）排在前面
      return scoreA - scoreB;
    });
  
  // 重新映射排名，确保从1开始
  return sortedRankings.map((student, index) => ({
    ...student,
    rank: index + 1
  }));
});

// 记录数排名
const sortedCountRankings = computed(() => {
  return [...props.rankings].sort((a, b) => {
    const aCount = a.record_count || a.total_records || 0;
    const bCount = b.record_count || b.total_records || 0;
    return bCount - aCount;
  })
    .map((student, index) => ({
      ...student,
      rank: index + 1
    }));
});
</script>
