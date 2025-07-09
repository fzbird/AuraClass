<template>
  <n-form inline :model="formModel" label-placement="left" label-width="auto">
    <n-grid :cols="24" :x-gap="24">
      <n-gi :span="6">
        <n-form-item label="班级">
          <n-select
            v-model:value="formModel.class_id"
            filterable
            clearable
            placeholder="选择班级"
            :options="classOptions"
          />
        </n-form-item>
      </n-gi>
      
      <n-gi :span="6">
        <n-form-item label="学生">
          <n-select
            v-model:value="formModel.student_id"
            filterable
            clearable
            placeholder="选择学生"
            :options="studentOptions"
            :loading="loadingStudents"
          />
        </n-form-item>
      </n-gi>
      
      <n-gi :span="6">
        <n-form-item label="量化项目">
          <n-select
            v-model:value="formModel.item_id"
            filterable
            clearable
            placeholder="选择量化项目"
            :options="itemOptions"
          />
        </n-form-item>
      </n-gi>
      
      <n-gi :span="6">
        <n-form-item label="分类">
          <n-select
            v-model:value="formModel.category"
            clearable
            placeholder="选择分类"
            :options="categoryOptions"
          />
        </n-form-item>
      </n-gi>
      
      <n-gi :span="6">
        <n-form-item label="分数范围">
          <n-space>
            <n-input-number
              v-model:value="formModel.min_score"
              clearable
              placeholder="最小值"
              style="width: 100px"
              :show-button="false"
            />
            <span>-</span>
            <n-input-number
              v-model:value="formModel.max_score"
              clearable
              placeholder="最大值"
              style="width: 100px"
              :show-button="false"
            />
          </n-space>
        </n-form-item>
      </n-gi>
      
      <n-gi :span="10">
        <n-form-item label="记录日期">
          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            clearable
            style="width: 100%"
          />
        </n-form-item>
      </n-gi>
      
      <n-gi :span="8">
        <n-space justify="end" style="width: 100%">
          <n-button @click="resetForm">重置</n-button>
          <n-button type="primary" @click="handleFilter">筛选</n-button>
        </n-space>
      </n-gi>
    </n-grid>
  </n-form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { 
  NForm, 
  NFormItem, 
  NGrid, 
  NGi, 
  NSelect, 
  NInputNumber, 
  NSpace, 
  NButton, 
  NDatePicker, 
  useMessage,
  type SelectOption
} from 'naive-ui';
import { getQuantItems } from '@/services/api/quant-items';
import { getStudents } from '@/services/api/students';
import { getClasses } from '@/services/api/classes';
import type { Class } from '@/types/class';
import type { Student } from '@/types/student';
import type { QuantItem } from '@/types/quant-item';

// 筛选表单模型
const formModel = reactive({
  class_id: null as number | null,
  student_id: null as number | null,
  item_id: null as number | null,
  category: null as string | null,
  min_score: null as number | null,
  max_score: null as number | null
});

// 日期选择范围
const dateRange = ref<[number, number] | null>(null);

// 数据加载状态
const loadingStudents = ref(false);
const loadingItems = ref(false);
const loadingClasses = ref(false);

// 选项列表
const classes = ref<Class[]>([]);
const students = ref<Student[]>([]);
const items = ref<QuantItem[]>([]);

// 指定触发更新的依赖
const deps = defineEmits(['filter', 'reset']);
const message = useMessage();

// 计算属性选项列表
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
    label: `${item.name} (${item.default_score})`,
    value: item.id
  }))
);

const categoryOptions = computed<SelectOption[]>(() => {
  const categories = new Set<string>();
  items.value.forEach(item => {
    if (item.category) {
      categories.add(item.category);
    }
  });
  
  return Array.from(categories).map(category => ({
    label: category,
    value: category
  }));
});

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

// 加载学生数据
const loadStudents = async (classId?: number) => {
  loadingStudents.value = true;
  try {
    const params = classId ? { class_id: classId, page_size: 1000 } : { page_size: 500 };
    const response = await getStudents(params);
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

// 当班级变化时加载学生数据
watch(() => formModel.class_id, (newValue) => {
  if (newValue) {
    loadStudents(newValue);
    // 清空学生选择
    formModel.student_id = null;
  }
});

// 筛选处理函数
const handleFilter = () => {
  const params: Record<string, any> = {};
  
  // 只添加非空值
  if (formModel.class_id !== null) {
    params.class_id = formModel.class_id;
  }
  
  if (formModel.student_id !== null) {
    params.student_id = formModel.student_id;
  }
  
  if (formModel.item_id !== null) {
    params.item_id = formModel.item_id;
  }
  
  if (formModel.category !== null) {
    params.category = formModel.category;
  }
  
  if (formModel.min_score !== null) {
    params.min_score = formModel.min_score;
  }
  
  if (formModel.max_score !== null) {
    params.max_score = formModel.max_score;
  }
  
  if (dateRange.value) {
    const [start, end] = dateRange.value;
    
    // 使用本地时区格式化日期，避免时区导致的日期偏移
    const formatLocalDate = (timestamp: number) => {
      const date = new Date(timestamp);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    };
    
    params.start_date = formatLocalDate(start);
    params.end_date = formatLocalDate(end);
  }
  
  deps('filter', params);
};

// 重置表单
const resetForm = () => {
  // 重置表单数据
  Object.keys(formModel).forEach(key => {
    formModel[key as keyof typeof formModel] = null;
  });
  
  // 重置日期
  dateRange.value = null;
  
  // 如果班级改变，重新加载学生
  loadStudents();
  
  // 发送重置事件
  deps('reset');
};

// 组件挂载时加载数据
onMounted(() => {
  loadClasses();
  loadStudents();
  loadItems();
});
</script>
