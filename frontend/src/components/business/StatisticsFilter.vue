<template>
  <n-card class="mb-6">
    <n-grid :cols="24" :x-gap="16" :y-gap="16">
      <n-grid-item :span="12" :lg="8">
        <n-form-item label="班级">
          <n-select
            v-model:value="filterModel.class_id"
            placeholder="选择班级"
            clearable
            :options="classOptions"
          />
        </n-form-item>
      </n-grid-item>
      
      <n-grid-item :span="12" :lg="8">
        <n-form-item label="日期范围">
          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            clearable
            style="width: 100%"
          />
        </n-form-item>
      </n-grid-item>
      
      <n-grid-item :span="24" :lg="8" class="flex items-end">
        <div class="flex w-full">
          <n-space justify="end" class="w-full">
            <n-button @click="resetFilter">重置</n-button>
            <n-button type="primary" @click="submitFilter">应用筛选</n-button>
          </n-space>
        </div>
      </n-grid-item>
    </n-grid>
  </n-card>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { NCard, NGrid, NGridItem, NFormItem, NSelect, NDatePicker, NButton, NSpace } from 'naive-ui';
import dayjs from 'dayjs';

const props = defineProps({
  classOptions: {
    type: Array,
    default: () => []
  },
  dateRange: {
    type: Object,
    default: () => ({
      start_date: dayjs().subtract(30, 'day').valueOf(),
      end_date: dayjs().valueOf()
    })
  }
});

const emit = defineEmits(['filter']);

const filterModel = reactive({
  class_id: null
});

// 转换日期范围格式，用于日期选择器
const dateRange = ref([
  props.dateRange.start_date,
  props.dateRange.end_date
]);

// 监听传入的日期范围变化
watch(() => props.dateRange, (newValue) => {
  dateRange.value = [newValue.start_date, newValue.end_date];
}, { deep: true });

const resetFilter = () => {
  filterModel.class_id = null;
  dateRange.value = [
    dayjs().subtract(30, 'day').valueOf(),
    dayjs().valueOf()
  ];
  
  submitFilter();
};

const submitFilter = () => {
  // 创建过滤参数对象
  const filterParams: {
    class_id: number | null;
    start_date?: string;
    end_date?: string;
  } = {
    class_id: filterModel.class_id || null,
  };
  
  // 确保有有效的日期范围
  if (dateRange.value && dateRange.value.length === 2 && dateRange.value[0] && dateRange.value[1]) {
    // 转换为正确的日期格式
    filterParams.start_date = dayjs(dateRange.value[0]).format('YYYY-MM-DD');
    filterParams.end_date = dayjs(dateRange.value[1]).format('YYYY-MM-DD');
  } else {
    // 如果没有有效日期范围，使用默认的（最近30天）
    const defaultStart = dayjs().subtract(30, 'day');
    const defaultEnd = dayjs();
    
    filterParams.start_date = defaultStart.format('YYYY-MM-DD');
    filterParams.end_date = defaultEnd.format('YYYY-MM-DD');
    
    // 更新日期选择器的值
    dateRange.value = [defaultStart.valueOf(), defaultEnd.valueOf()];
  }
  
  // 发出过滤事件
  console.log('应用过滤条件:', filterParams);
  emit('filter', filterParams);
};
</script>
