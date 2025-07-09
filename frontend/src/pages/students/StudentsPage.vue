<template>
  <div>
    <div class="flex justify-between mb-6">
      <h1 class="text-2xl font-bold page-title">学生管理</h1>
      
      <n-space>
        <n-button
          type="info"
          @click="refreshStudentScores"
          v-if="hasPermission('update:students')"
        >
          <template #icon>
            <n-icon><reload-outlined /></n-icon>
          </template>
          刷新分数和排名
        </n-button>

        <n-button
          type="success"
          @click="isImportVisible = true"
          v-if="hasPermission('create:students')"
        >
          <template #icon>
            <n-icon><upload-outlined /></n-icon>
          </template>
          批量导入
        </n-button>
        
        <n-button
          type="primary"
          @click="showCreateModal = true"
          v-if="hasPermission('create:students')"
        >
          <template #icon>
            <n-icon><user-add-outlined /></n-icon>
          </template>
          添加学生
        </n-button>
      </n-space>
    </div>
    
    <n-card class="mb-6">
      <student-filter-form 
        :class-options="classOptions"
        @filter="handleFilter"
      />
    </n-card>
    
    <!-- 批量导入功能 -->
    <batch-student-import 
      v-if="isImportVisible" 
      @success="handleImportSuccess" 
      @close="isImportVisible = false"
    />
    
    <n-card>
      <n-data-table
        :columns="columns"
        :data="students"
        :loading="loading"
        :pagination="pagination"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
        :row-key="row => row.id"
      />
    </n-card>
    
    <!-- 创建/编辑学生模态框 -->
    <student-form-modal
      v-model:show="showCreateModal"
      :class-options="classOptions"
      @success="handleSuccess"
    />
    
    <student-form-modal
      v-model:show="showEditModal"
      :class-options="classOptions"
      :student="selectedStudent"
      @success="handleSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { NButton, NCard, NDataTable, useMessage, NPopconfirm, NSpace, NIcon, useDialog } from 'naive-ui';
import UserAddOutlined from '@vicons/antd/es/UserAddOutlined';
import UploadOutlined from '@vicons/antd/es/UploadOutlined';
import ReloadOutlined from '@vicons/antd/es/ReloadOutlined';
import StudentFilterForm from '@/components/business/StudentFilterForm.vue';
import StudentFormModal from '@/components/business/StudentFormModal.vue';
import BatchStudentImport from '@/components/business/BatchStudentImport.vue';
import { 
  getStudents, 
  deleteStudent, 
  toggleStudentActive,
  updateStudentScores,
  forceDeleteStudent 
} from '@/services/api/students';
import { getClasses } from '@/services/api/classes';
import { usePermissionStore } from '@/stores/permission';
import { useThemeStore } from '@/stores/theme';
import { formatDate } from '@/utils';
import type { Student, Class } from '@/types/models';

const router = useRouter();
const message = useMessage();
const dialog = useDialog();
const permissionStore = usePermissionStore();
const themeStore = useThemeStore();

// 获取当前主题模式
const isDarkMode = computed(() => themeStore.darkMode);

const loading = ref(true);
const students = ref<Student[]>([]);
const classOptions = ref<{label: string, value: number}[]>([]);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const selectedStudent = ref(null);
const filterParams = ref({
  classId: undefined,
  name: undefined,
  student_id_no: undefined,
  gender: undefined,
  is_active: undefined
});
const isImportVisible = ref(false);

const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50],
  showSizePicker: true,
  prefix: ({ itemCount }) => `共 ${itemCount} 项`
});

const columns = [
  {
    title: '学号',
    key: 'student_id_no',
    sorter: 'default'
  },
  {
    title: '姓名',
    key: 'full_name',
    render: (row) => {
      return h(
        'a',
        {
          href: 'javascript:;',
          onclick: () => viewStudentDetail(row.id)
        },
        row.full_name
      );
    }
  },
  {
    title: '班级',
    key: 'class_name'
  },
  {
    title: '性别',
    key: 'gender',
    render: (row) => row.gender === 'male' ? '男' : '女'
  },
  {
    title: '总分',
    key: 'total_score',
    sorter: (a, b) => (a.total_score || 0) - (b.total_score || 0)
  },
  {
    title: '排名',
    key: 'rank',
    sorter: (a, b) => (a.rank || 9999) - (b.rank || 9999)
  },
  {
    title: '状态',
    key: 'is_active',
    render: (row) => {
      return h(
        'div',
        {
          class: row.is_active ? 'text-success' : 'text-error'
        },
        row.is_active ? '启用' : '禁用'
      );
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    render: (row) => formatDate(row.created_at)
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) => {
      return h(
        NSpace,
        { justify: 'center' },
        {
          default: () => [
            h(
              NButton,
              {
                size: 'small',
                onClick: () => viewStudentDetail(row.id)
              },
              { default: () => '查看' }
            ),
            h(
              NButton,
              {
                size: 'small',
                type: 'primary',
                onClick: () => editStudent(row),
                disabled: !hasPermission('update:students')
              },
              { default: () => '编辑' }
            ),
            h(
              NButton,
              {
                size: 'small',
                type: row.is_active ? 'warning' : 'success',
                onClick: () => toggleStudentStatus(row),
                disabled: !hasPermission('update:students')
              },
              { default: () => row.is_active ? '禁用' : '启用' }
            ),
            h(
              NPopconfirm,
              {
                onPositiveClick: () => removeStudent(row.id),
                disabled: !hasPermission('delete:students')
              },
              {
                default: () => '确定删除该学生吗？此操作不可撤销',
                trigger: () => h(
                  NButton,
                  {
                    size: 'small',
                    type: 'error',
                    disabled: !hasPermission('delete:students')
                  },
                  { default: () => '删除' }
                )
              }
            )
          ]
        }
      );
    }
  }
];

onMounted(async () => {
  await Promise.all([
    fetchStudents(),
    fetchClasses()
  ]);
});

const fetchStudents = async () => {
  loading.value = true;
  try {
    // 构建正确的参数对象
    const params: Record<string, any> = {
      page: pagination.page,
      size: pagination.pageSize
    };
    
    // 添加过滤参数
    if (filterParams.value) {
      if (filterParams.value.classId) {
        params.class_id = filterParams.value.classId;
      }
      
      if (filterParams.value.name) {
        params.name = filterParams.value.name;
      }
      
      if (filterParams.value.student_id_no) {
        params.student_id_no = filterParams.value.student_id_no;
      }
      
      if (filterParams.value.gender) {
        params.gender = filterParams.value.gender;
      }
      
      if (filterParams.value.is_active !== undefined) {
        params.is_active = filterParams.value.is_active;
      }
    }
    
    console.log('发送请求参数:', params);
    const response = await getStudents(params);
    console.log('学生原始响应:', response);
    
    // 更灵活地处理不同格式的响应
    let studentData = [];
    
    if (Array.isArray(response)) {
      studentData = response;
    } else if (response && typeof response === 'object') {
      if (response.data) {
        if (Array.isArray(response.data)) {
          studentData = response.data;
        } else if (response.data.data && Array.isArray(response.data.data)) {
          studentData = response.data.data;
        }
      } else if (response.items && Array.isArray(response.items)) {
        studentData = response.items;
      }
    }
    
    students.value = studentData;
    
    // 处理分页信息
    if (response.meta && response.meta.pagination) {
      pagination.itemCount = response.meta.pagination.total || 0;
    } else if (response.data && response.data.meta && response.data.meta.pagination) {
      pagination.itemCount = response.data.meta.pagination.total || 0;
    } else {
      pagination.itemCount = studentData.length;
    }
  } catch (error) {
    console.error('Failed to fetch students:', error);
    message.error('获取学生列表失败');
    students.value = [];
  } finally {
    loading.value = false;
  }
};

const fetchClasses = async () => {
  try {
    const response = await getClasses();
    console.log('班级原始响应:', response);
    
    // 更灵活地处理不同格式的响应，包括多层嵌套
    let classData = [];
    
    if (Array.isArray(response)) {
      // 响应直接是数组
      classData = response;
    } else if (response && typeof response === 'object') {
      if (response.data) {
        // 处理 {data: Array} 格式
        if (Array.isArray(response.data)) {
          classData = response.data;
        } 
        // 处理 {data: {data: Array}} 格式
        else if (response.data.data && Array.isArray(response.data.data)) {
          classData = response.data.data;
        }
      } else if (response.items && Array.isArray(response.items)) {
        classData = response.items;
      }
    }
    
    console.log('提取的班级数据:', classData);
    
    // 转换为下拉选项格式
    classOptions.value = classData.map(cls => ({
      label: cls.name,
      value: cls.id
    }));
    
    console.log('生成的班级选项:', classOptions.value);
  } catch (error) {
    console.error('获取班级列表失败:', error);
    message.error('获取班级列表失败');
  }
};

const handlePageChange = (page) => {
  pagination.page = page;
  fetchStudents();
};

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize;
  pagination.page = 1;
  fetchStudents();
};

const handleFilter = (params: Record<string, any>) => {
  const filteredParams = {};
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      filteredParams[key] = value;
    }
  });
  
  console.log('应用搜索过滤条件:', filteredParams);
  filterParams.value = filteredParams;
  pagination.page = 1;
  fetchStudents();
};

const handleSuccess = () => {
  fetchStudents();
};

const viewStudentDetail = (id) => {
  router.push(`/app/students/${id}`);
};

const editStudent = (student) => {
  selectedStudent.value = student;
  showEditModal.value = true;
};

const removeStudent = async (id) => {
  try {
    // 先尝试普通删除
    await deleteStudent(id);
    message.success('删除学生成功');
    fetchStudents();
  } catch (error) {
    // 如果失败，检查是否是因为存在量化记录
    if (error.response?.status === 400 && 
        (error.response?.data?.error?.detail?.includes('条量化记录') || 
         error.response?.data?.error?.message?.includes('条量化记录'))) {
      // 提取记录数量
      const recordCount = error.response.headers['x-record-count'] || 
                          error.response.data.error.detail?.match(/\d+/)?.[0] || 
                          error.response.data.error.message?.match(/\d+/)?.[0] || 0;
      
      // 显示确认对话框
      const d = dialog.warning({
        title: '删除确认',
        content: `该学生有${recordCount}条量化记录，删除后无法恢复。确认要删除该学生及其所有记录吗？`,
        positiveText: '确认删除',
        negativeText: '取消',
        onPositiveClick: async () => {
          try {
            // 用户确认，执行强制删除
            const result = await forceDeleteStudent(id);
            message.success(result.message || result.data?.message || '已成功删除学生及相关记录');
            fetchStudents();
          } catch (forceError) {
            console.error('强制删除学生失败:', forceError);
            message.error('强制删除学生失败: ' + (forceError.response?.data?.error?.message || '未知错误'));
          }
        }
      });
    } else {
      console.error('Failed to delete student:', error);
      message.error('删除学生失败: ' + (error.response?.data?.error?.message || '未知错误'));
    }
  }
};

const toggleStudentStatus = async (student) => {
  try {
    console.info('正在更新学生状态...');
    await toggleStudentActive(student.id, !student.is_active);
    fetchStudents();
    message.success(student.is_active ? '学生已禁用' : '学生已启用');
  } catch (error) {
    message.error('操作失败：' + (error.response?.data?.error?.message || '未知错误'));
  }
};

const handleImportSuccess = () => {
  message.success('学生导入成功');
  fetchStudents();
  isImportVisible.value = false;
};

const refreshStudentScores = async () => {
  console.log(`当前角色: ${permissionStore.role}, 刷新权限: ${hasPermission('update:students')}`);
  
  if (!hasPermission('update:students')) {
    message.warning('您没有刷新学生分数的权限');
    return;
  }
  
  loading.value = true;
  try {
    const classId = filterParams.value?.classId;
    console.log(`正在调用更新API, 班级ID: ${classId || '全部班级'}`);
    
    const response = await updateStudentScores(classId);
    console.log('API响应:', response);
    
    const successMsg = response?.data?.message || '学生分数和排名已更新';
    message.success(successMsg);
    fetchStudents();
  } catch (error) {
    console.error('刷新学生分数失败:', error);
    console.error('错误详情:', error?.response?.data, '状态码:', error?.response?.status);
    
    const errorMessage = error?.message || '未知错误';
    
    if (error?.response?.status === 403) {
      message.error('权限不足，无法更新学生分数和排名');
    } else if (error?.response) {
      const responseMessage = error.response?.data?.error?.message || error.response?.statusText || '服务器返回错误';
      message.error(`更新失败: ${responseMessage}`);
    } else {
      message.error(`更新学生分数和排名失败: ${errorMessage}`);
    }
  } finally {
    loading.value = false;
  }
};

const hasPermission = (permission) => {
  return permissionStore.hasPermission(permission);
};
</script>

<style scoped>
.page-title {
  color: inherit;
  transition: color 0.3s ease;
}

.text-success {
  color: #18a058;
}

:root.dark .text-success {
  color: #36ad6a;
}

.text-error {
  color: #d03050;
}

:root.dark .text-error {
  color: #e34d59;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

/* Ensure table links are visible in dark mode */
:root.dark a {
  color: #6366f1;
}

:root.dark a:hover {
  color: #818cf8;
  text-decoration: underline;
}
</style>
