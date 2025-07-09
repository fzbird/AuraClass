<template>
  <n-form
    ref="formRef"
    :model="formModel"
    :rules="rules"
    label-placement="left"
    label-width="auto"
    require-mark-placement="right-hanging"
  >
    <n-grid :cols="24" :x-gap="24">
      <!-- 班级选择 -->
      <n-gi :span="12">
        <n-form-item path="class_id" label="班级">
          <n-select
            v-model:value="formModel.class_id"
            filterable
            placeholder="请选择班级"
            :options="classOptions"
            :loading="loadingClasses"
            @update:value="handleClassChange"
          />
        </n-form-item>
      </n-gi>
      
      <!-- 量化项目选择 -->
      <n-gi :span="12">
        <n-form-item path="item_id" label="量化项目">
          <n-select
            v-model:value="formModel.item_id"
            filterable
            placeholder="请选择量化项目"
            :options="itemOptions"
            :loading="loadingItems"
            @update:value="handleItemChange"
          />
        </n-form-item>
      </n-gi>
      
      <!-- 分数输入 -->
      <n-gi :span="8">
        <n-form-item path="score" label="分数">
          <n-input-number
            v-model:value="formModel.score"
            placeholder="请输入分数"
            :min="-10"
            :max="10"
            :show-button="false"
            style="width: 100%"
          />
        </n-form-item>
      </n-gi>
      
      <!-- 记录日期选择 -->
      <n-gi :span="8">
        <n-form-item path="record_date" label="记录日期">
          <n-date-picker
            v-model:value="formModel.record_date"
            type="date"
            clearable
            style="width: 100%"
          />
        </n-form-item>
      </n-gi>
      
      <!-- 原因输入 -->
      <n-gi :span="24">
        <n-form-item path="reason" label="原因">
          <n-input
            v-model:value="formModel.reason"
            type="textarea"
            placeholder="请输入量化原因"
            :rows="3"
          />
        </n-form-item>
      </n-gi>
      
      <!-- 学生选择 -->
      <n-gi :span="24">
        <n-form-item path="selected_students" label="选择学生">
          <div class="student-selection">
            <div class="selection-header">
              <n-space align="center">
                <n-checkbox 
                  :indeterminate="isIndeterminate" 
                  :checked="isAllSelected"
                  @update:checked="handleSelectAll"
                />
                <span>全选</span>
                <n-button text type="primary" @click="toggleSortByName">
                  按姓名排序
                  <template #icon>
                    <n-icon>
                      <SortAscendingOutlined v-if="sortByName" />
                      <SortDescendingOutlined v-else />
                    </n-icon>
                  </template>
                </n-button>
              </n-space>
              
              <n-input 
                v-model:value="searchText" 
                placeholder="搜索学生"
                clearable
                style="width: 220px"
              >
                <template #prefix>
                  <n-icon><SearchOutlined /></n-icon>
                </template>
              </n-input>
            </div>
            
            <div class="students-list">
              <n-scrollbar style="max-height: 300px">
                <div class="students-grid">
                  <n-checkbox-group v-model:value="formModel.selected_students">
                    <div 
                      v-for="student in filteredStudents" 
                      :key="student.id" 
                      class="student-item"
                    >
                      <n-checkbox :value="student.id" :label="student.full_name" />
                      <span class="student-id">{{ student.student_id_no }}</span>
                    </div>
                  </n-checkbox-group>
                </div>
              </n-scrollbar>
            </div>
            
            <div class="selection-summary">
              已选择 {{ formModel.selected_students.length }} 名学生
            </div>
          </div>
        </n-form-item>
      </n-gi>
    </n-grid>
    
    <!-- 表单按钮 -->
    <div class="flex justify-end mt-4">
      <n-space>
        <n-button @click="handleCancel">取消</n-button>
        <n-button type="primary" @click="handleSubmit" :loading="submitting">
          批量创建
        </n-button>
      </n-space>
    </div>
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
  NInput,
  NButton,
  NSpace,
  NCheckbox,
  NCheckboxGroup,
  NScrollbar,
  NDatePicker,
  NIcon,
  useMessage
} from 'naive-ui';
import type { FormInst, FormRules, SelectOption } from 'naive-ui';
import { getClasses, getClassStudents } from '@/services/api/classes';
import { getStudents } from '@/services/api/students';
import { getQuantItems } from '@/services/api/quant-items';
import { createQuantRecords } from '@/services/api/records';
import type { QuantItem } from '@/types/quant-item';
import type { CreateQuantRecordPayload } from '@/types/record';
import SearchOutlined from '@vicons/antd/es/SearchOutlined';
import SortAscendingOutlined from '@vicons/antd/es/SortAscendingOutlined';
import SortDescendingOutlined from '@vicons/antd/es/SortDescendingOutlined';

// 定义组件事件
const emit = defineEmits(['success', 'cancel']);

// 表单和消息实例
const formRef = ref<FormInst | null>(null);
const message = useMessage();

// 数据加载和提交状态
const loadingClasses = ref(false);
const loadingStudents = ref(false);
const loadingItems = ref(false);
const submitting = ref(false);

// 搜索和排序状态
const searchText = ref('');
const sortByName = ref(true);

// 选项数据
const classes = ref<{ id: number; name: string }[]>([]);
const students = ref<{ id: number; student_id_no: string; full_name: string }[]>([]);
const items = ref<QuantItem[]>([]);

// 表单模型数据
interface BatchRecordFormModel {
  class_id: number | null;
  item_id: number | null;
  score: number;
  reason: string;
  record_date: number | null;
  selected_students: number[];
}

const formModel = reactive<BatchRecordFormModel>({
  class_id: null,
  item_id: null,
  score: 0,
  reason: '',
  record_date: Date.now(),
  selected_students: []
});

// 表单验证规则
const rules: FormRules = {
  class_id: [
    { required: true, message: '请选择班级', trigger: ['blur', 'change'] }
  ],
  item_id: [
    { required: true, message: '请选择量化项目', trigger: ['blur', 'change'] }
  ],
  score: [
    { required: true, message: '请输入分数', trigger: ['blur', 'change'] },
    { type: 'number', message: '分数必须为数字', trigger: ['blur', 'change'] }
  ],
  record_date: [
    { required: true, message: '请选择记录日期', trigger: ['blur', 'change'] }
  ],
  selected_students: [
    { 
      required: true, 
      type: 'array', 
      min: 1, 
      message: '请至少选择一名学生', 
      trigger: ['blur', 'change'] 
    }
  ]
};

// 计算属性：班级选项
const classOptions = computed<SelectOption[]>(() => {
  return classes.value.map(cls => ({
    label: cls.name,
    value: cls.id
  }));
});

// 计算属性：量化项目选项
const itemOptions = computed<SelectOption[]>(() => {
  return items.value.map(item => ({
    label: `${item.name} (${item.default_score ?? 0}) ${item.category ? `- ${item.category}` : ''}`,
    value: item.id,
    category: item.category,
    default_score: item.default_score ?? 0
  }));
});

// 计算属性：过滤后的学生列表
const filteredStudents = computed(() => {
  let result = students.value;
  
  // 搜索过滤
  if (searchText.value.trim()) {
    const searchLower = searchText.value.toLowerCase();
    result = result.filter(
      student => 
        student.full_name.toLowerCase().includes(searchLower) || 
        student.student_id_no.toLowerCase().includes(searchLower)
    );
  }
  
  // 排序
  if (sortByName.value) {
    result = [...result].sort((a, b) => a.full_name.localeCompare(b.full_name));
  } else {
    result = [...result].sort((a, b) => a.student_id_no.localeCompare(b.student_id_no));
  }
  
  return result;
});

// 计算属性：选择状态
const isAllSelected = computed(() => {
  return filteredStudents.value.length > 0 && 
         filteredStudents.value.every(student => 
           formModel.selected_students.includes(student.id)
         );
});

const isIndeterminate = computed(() => {
  return formModel.selected_students.length > 0 && 
         !isAllSelected.value;
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
const loadStudents = async (classId: number) => {
  loadingStudents.value = true;
  try {
    const response = await getClassStudents(classId);
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

// 班级变更处理
const handleClassChange = (value: number | null) => {
  formModel.class_id = value;
  formModel.selected_students = [];
  
  if (value) {
    loadStudents(value);
  } else {
    students.value = [];
  }
};

// 量化项目变更处理
const handleItemChange = (value: number | null) => {
  formModel.item_id = value;
  
  if (value) {
    const selectedItem = items.value.find(item => item.id === value);
    if (selectedItem && selectedItem.default_score !== undefined) {
      formModel.score = selectedItem.default_score;
    }
  }
};

// 全选/取消全选处理
const handleSelectAll = (checked: boolean) => {
  if (checked) {
    formModel.selected_students = filteredStudents.value.map(student => student.id);
  } else {
    formModel.selected_students = [];
  }
};

// 切换排序方式
const toggleSortByName = () => {
  sortByName.value = !sortByName.value;
};

// 提交表单
const handleSubmit = () => {
  formRef.value?.validate(async (errors) => {
    if (errors) {
      return;
    }
    
    if (formModel.selected_students.length === 0) {
      message.warning('请至少选择一名学生');
      return;
    }
    
    submitting.value = true;
    
    try {
      // 格式化日期为ISO字符串并截取日期部分
      const recordDate = formModel.record_date 
        ? new Date(formModel.record_date).toISOString().split('T')[0]
        : new Date().toISOString().split('T')[0];
      
      // 准备批量提交数据
      const records: CreateQuantRecordPayload[] = formModel.selected_students.map(studentId => ({
        student_id: studentId,
        item_id: formModel.item_id!,
        score: formModel.score,
        reason: formModel.reason || '',
        record_date: recordDate
      }));
      
      // 批量创建记录
      const response = await createQuantRecords(records);
      
      message.success(`成功添加 ${formModel.selected_students.length} 条量化记录`);
      emit('success');
    } catch (error) {
      console.error('Failed to create batch records:', error);
      message.error('批量创建记录失败');
    } finally {
      submitting.value = false;
    }
  });
};

// 取消操作
const handleCancel = () => {
  emit('cancel');
};

// 组件挂载时加载数据
onMounted(() => {
  loadClasses();
  loadItems();
});
</script>

<style scoped>
.mt-4 {
  margin-top: 16px;
}

.flex {
  display: flex;
}

.justify-end {
  justify-content: flex-end;
}

.student-selection {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 16px;
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px 16px;
  padding: 8px 0;
}

.student-item {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
}

.student-item:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.student-id {
  margin-left: 8px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.selection-summary {
  margin-top: 12px;
  text-align: right;
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
}
</style> 