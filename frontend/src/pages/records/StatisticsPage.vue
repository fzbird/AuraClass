<template>
  <div class="statistics-page">
    <page-header title="量化统计分析">
      <template #subtitle>
        查看学生量化记录的统计数据和排名情况
      </template>
    </page-header>
    
    <!-- 筛选面板 -->
    <n-card class="mb-5">
      <n-grid :cols="24" :x-gap="24">
        <n-gi :span="6">
          <n-form-item label="班级">
            <n-select
              v-model:value="filterParams.class_id"
              filterable
              clearable
              placeholder="选择班级"
              :options="classOptions"
              @update:value="handleClassChange"
            />
          </n-form-item>
        </n-gi>
        
        <n-gi :span="6">
          <n-form-item label="学生">
            <n-select
              v-model:value="filterParams.student_id"
              filterable
              clearable
              placeholder="选择学生"
              :options="studentOptions"
              :loading="loadingStudents"
              :disabled="!filterParams.class_id"
            />
          </n-form-item>
        </n-gi>
        
        <n-gi :span="6">
          <n-form-item label="量化项目">
            <n-select
              v-model:value="filterParams.item_id"
              filterable
              clearable
              placeholder="选择量化项目"
              :options="itemOptions"
              :loading="loadingItems"
            />
          </n-form-item>
        </n-gi>
        
        <n-gi :span="6">
          <n-form-item label="日期范围">
            <n-date-picker
              v-model:value="dateRange"
              type="daterange"
              clearable
              style="width: 100%"
            />
          </n-form-item>
        </n-gi>
        
        <n-gi :span="24">
          <div class="filter-actions">
            <n-space>
              <n-button @click="resetFilter">重置</n-button>
              <n-button type="primary" @click="applyFilter">应用筛选</n-button>
            </n-space>
          </div>
        </n-gi>
      </n-grid>
    </n-card>
    
    <!-- 统计面板 -->
    <statistics-panel
      :class-id="appliedFilter.class_id"
      :student-id="appliedFilter.student_id"
      :item-id="appliedFilter.item_id"
      :date-range="appliedFilter.dateRange"
      ref="statisticsPanelRef"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { 
  NCard, 
  NGrid, 
  NGi, 
  NFormItem, 
  NSelect,
  NDatePicker,
  NButton,
  NSpace,
  useMessage
} from 'naive-ui';
import type { SelectOption } from 'naive-ui';
import PageHeader from '@/components/layout/PageHeader.vue';
import StatisticsPanel from '@/components/business/StatisticsPanel.vue';
import { getClasses } from '@/services/api/classes';
import { getStudents } from '@/services/api/students';
import { getQuantItems } from '@/services/api/quant-items';

const message = useMessage();
const statisticsPanelRef = ref(null);

// 数据加载状态
const loadingClasses = ref(false);
const loadingStudents = ref(false);
const loadingItems = ref(false);

// 筛选参数
const filterParams = reactive({
  class_id: null as number | null,
  student_id: null as number | null,
  item_id: null as number | null
});

// 已应用的筛选参数
const appliedFilter = reactive({
  class_id: null as number | null,
  student_id: null as number | null,
  item_id: null as number | null,
  dateRange: null as [string, string] | null
});

// 日期范围
const dateRange = ref<[number, number] | null>(null);

// 选项数据
const classes = ref<{ id: number; name: string }[]>([]);
const students = ref<{ id: number; student_id_no: string; full_name: string }[]>([]);
const items = ref<{ id: number; name: string; category?: string }[]>([]);

// 选项计算属性
const classOptions = computed<SelectOption[]>(() => 
  classes.value.map(cls => ({
    label: cls.name,
    value: cls.id
  }))
);

const studentOptions = computed<SelectOption[]>(() => 
  students.value.map(student => ({
    label: `${student.student_id_no} - ${student.full_name}`,
    value: student.id
  }))
);

const itemOptions = computed<SelectOption[]>(() => 
  items.value.map(item => ({
    label: `${item.name}${item.category ? ` - ${item.category}` : ''}`,
    value: item.id
  }))
);

// 班级变更处理
const handleClassChange = (value: number | null) => {
  filterParams.class_id = value;
  filterParams.student_id = null;
  
  if (value) {
    loadStudentsByClass(value);
  } else {
    students.value = [];
  }
};

// 加载班级数据
const loadClasses = async () => {
  loadingClasses.value = true;
  try {
    const response = await getClasses();
    if (response.data && response.data.data) {
      classes.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load classes:', error);
    message.error('加载班级数据失败');
  } finally {
    loadingClasses.value = false;
  }
};

// 加载班级学生数据
const loadStudentsByClass = async (classId: number) => {
  loadingStudents.value = true;
  try {
    const response = await getStudents({ class_id: classId, page_size: 1000 });
    if (response.data && response.data.data) {
      students.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load students:', error);
    message.error('加载学生数据失败');
  } finally {
    loadingStudents.value = false;
  }
};

// 加载量化项目数据
const loadItems = async () => {
  loadingItems.value = true;
  try {
    const response = await getQuantItems();
    if (response.data && response.data.data) {
      items.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load quant items:', error);
    message.error('加载量化项目失败');
  } finally {
    loadingItems.value = false;
  }
};

// 应用筛选
const applyFilter = () => {
  // 应用筛选条件
  appliedFilter.class_id = filterParams.class_id;
  appliedFilter.student_id = filterParams.student_id;
  appliedFilter.item_id = filterParams.item_id;
  
  // 处理日期范围
  if (dateRange.value) {
    const [startDate, endDate] = dateRange.value;
    appliedFilter.dateRange = [
      new Date(startDate).toISOString().split('T')[0],
      new Date(endDate).toISOString().split('T')[0]
    ];
  } else {
    appliedFilter.dateRange = null;
  }
};

// 重置筛选
const resetFilter = () => {
  // 重置筛选参数
  filterParams.class_id = null;
  filterParams.student_id = null;
  filterParams.item_id = null;
  dateRange.value = null;
  
  // 清空学生列表
  students.value = [];
  
  // 重置已应用的筛选
  appliedFilter.class_id = null;
  appliedFilter.student_id = null;
  appliedFilter.item_id = null;
  appliedFilter.dateRange = null;
};

// 初始化数据
onMounted(() => {
  loadClasses();
  loadItems();
});
</script>

<style scoped>
.statistics-page {
  width: 100%;
}

.mb-5 {
  margin-bottom: 20px;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
}
</style> 