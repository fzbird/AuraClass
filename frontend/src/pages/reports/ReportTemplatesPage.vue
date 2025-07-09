<template>
  <div class="report-templates-page">
    <page-header title="报表模板管理">
      <template #subtitle>
        创建和管理自定义报表模板
      </template>
      <template #extra>
        <n-button type="primary" @click="showCreateModal = true">
          <template #icon>
            <n-icon><PlusOutlined /></n-icon>
          </template>
          创建模板
        </n-button>
      </template>
    </page-header>
    
    <!-- 模板列表 -->
    <n-card class="card-container">
      <n-data-table
        ref="tableRef"
        :columns="columns"
        :data="templates"
        :loading="loading"
        :pagination="pagination"
        :row-key="(row: ReportTemplate) => row.id"
        @update:page="handlePageChange"
      />
    </n-card>
    
    <!-- 创建/编辑模板对话框 -->
    <n-modal
      v-model:show="showCreateModal"
      :mask-closable="false"
      preset="card"
      :title="editingTemplate ? '编辑报表模板' : '创建报表模板'"
      :style="{ width: '900px' }"
    >
      <n-form
        ref="formRef"
        :model="formModel"
        :rules="rules"
        label-placement="left"
        label-width="100px"
        require-mark-placement="right-hanging"
      >
        <n-grid :cols="24" :x-gap="24">
          <n-gi :span="24">
            <n-form-item label="模板名称" path="name">
              <n-input v-model:value="formModel.name" placeholder="输入模板名称" />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="12">
            <n-form-item label="报表类型" path="type">
              <n-select
                v-model:value="formModel.type"
                :options="templateTypeOptions"
                placeholder="选择报表类型"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="12">
            <n-form-item label="描述" path="description">
              <n-input v-model:value="formModel.description" placeholder="输入模板描述（可选）" />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="24">
            <n-form-item label="模板内容" path="content">
              <div class="template-editor-container">
                <div class="template-editor-header">
                  <n-space>
                    <n-button-group>
                      <n-tooltip trigger="hover" placement="bottom">
                        <template #trigger>
                          <n-button @click="insertVariable('CLASS_NAME')">班级</n-button>
                        </template>
                        插入班级名称
                      </n-tooltip>
                      <n-tooltip trigger="hover" placement="bottom">
                        <template #trigger>
                          <n-button @click="insertVariable('STUDENT_NAME')">学生</n-button>
                        </template>
                        插入学生姓名
                      </n-tooltip>
                      <n-tooltip trigger="hover" placement="bottom">
                        <template #trigger>
                          <n-button @click="insertVariable('DATE_RANGE')">日期范围</n-button>
                        </template>
                        插入报表日期范围
                      </n-tooltip>
                    </n-button-group>
                    
                    <n-button-group>
                      <n-tooltip trigger="hover" placement="bottom">
                        <template #trigger>
                          <n-button @click="insertVariable('TOTAL_RECORDS')">记录数</n-button>
                        </template>
                        插入总记录数
                      </n-tooltip>
                      <n-tooltip trigger="hover" placement="bottom">
                        <template #trigger>
                          <n-button @click="insertVariable('TOTAL_SCORE')">总分</n-button>
                        </template>
                        插入总积分
                      </n-tooltip>
                      <n-tooltip trigger="hover" placement="bottom">
                        <template #trigger>
                          <n-button @click="insertVariable('AVERAGE_SCORE')">平均分</n-button>
                        </template>
                        插入平均分
                      </n-tooltip>
                    </n-button-group>
                    
                    <n-button-group>
                      <n-tooltip trigger="hover" placement="bottom">
                        <template #trigger>
                          <n-button @click="insertBlock('STUDENT_LIST')">学生列表</n-button>
                        </template>
                        插入学生排名表格
                      </n-tooltip>
                      <n-tooltip trigger="hover" placement="bottom">
                        <template #trigger>
                          <n-button @click="insertBlock('RECORD_LIST')">记录列表</n-button>
                        </template>
                        插入量化记录列表
                      </n-tooltip>
                      <n-tooltip trigger="hover" placement="bottom">
                        <template #trigger>
                          <n-button @click="insertBlock('ITEM_DISTRIBUTION')">项目分布</n-button>
                        </template>
                        插入量化项目分布
                      </n-tooltip>
                    </n-button-group>
                  </n-space>
                </div>
                
                <n-input
                  v-model:value="formModel.content"
                  type="textarea"
                  placeholder="在此处编辑模板内容，使用HTML格式，可插入变量和数据块"
                  :autosize="{ minRows: 15, maxRows: 30 }"
                />
                
                <div class="template-editor-footer">
                  <n-text depth="3">
                    可用变量: {'{{ CLASS_NAME }}', '{{ STUDENT_NAME }}', '{{ DATE_RANGE }}', '{{ TOTAL_RECORDS }}', '{{ TOTAL_SCORE }}', '{{ AVERAGE_SCORE }}', ...}
                  </n-text>
                </div>
              </div>
            </n-form-item>
          </n-gi>
        </n-grid>
        
        <n-space justify="end">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleSaveTemplate" :loading="saving">保存</n-button>
        </n-space>
      </n-form>
    </n-modal>
    
    <!-- 预览模板对话框 -->
    <n-modal
      v-model:show="showPreviewModal"
      preset="card"
      title="模板预览"
      :style="{ width: '800px' }"
    >
      <div class="preview-container">
        <div v-html="sanitizedPreviewContent" class="preview-content"></div>
      </div>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="showPreviewModal = false">关闭</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, h, onMounted } from 'vue';
import {
  NCard,
  NButton,
  NIcon,
  NSpace,
  NDataTable,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NGrid,
  NGi,
  NButtonGroup,
  NTooltip,
  NText,
  NTag,
  NPopconfirm,
  useMessage
} from 'naive-ui';
import type { DataTableColumns, FormInst, FormRules } from 'naive-ui';
import PlusOutlined from '@vicons/antd/es/PlusOutlined';
import EditOutlined from '@vicons/antd/es/EditOutlined';
import DeleteOutlined from '@vicons/antd/es/DeleteOutlined';
import EyeOutlined from '@vicons/antd/es/EyeOutlined';
import PageHeader from '@/components/layout/PageHeader.vue';
import { 
  getReportTemplates,
  createReportTemplate,
  updateReportTemplate,
  deleteReportTemplate,
  type ReportTemplate,
  type CreateReportTemplatePayload
} from '@/services/api/reports';
import { sanitizeHTML } from '@/utils/sanitize';

// 组件状态
const message = useMessage();
const loading = ref(false);
const saving = ref(false);
const templates = ref<ReportTemplate[]>([]);
const showCreateModal = ref(false);
const showPreviewModal = ref(false);
const editingTemplate = ref<ReportTemplate | null>(null);
const previewContent = ref('');
const formRef = ref<FormInst | null>(null);
const tableRef = ref(null);

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page: number) => {
    pagination.page = page;
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.pageSize = pageSize;
    pagination.page = 1;
  }
});

// 表单数据
const formModel = reactive<{
  name: string;
  type: 'student' | 'class' | 'all-classes';
  description: string;
  content: string;
}>({
  name: '',
  type: 'class',
  description: '',
  content: ''
});

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择报表类型', trigger: ['blur', 'change'] }
  ],
  content: [
    { required: true, message: '请输入模板内容', trigger: 'blur' }
  ]
};

// 模板类型选项
const templateTypeOptions = [
  { label: '学生个人报表', value: 'student' },
  { label: '班级排名报表', value: 'class' },
  { label: '全校班级报表', value: 'all-classes' }
];

// 表格列定义
const columns = computed<DataTableColumns>(() => [
  {
    title: '模板名称',
    key: 'name'
  },
  {
    title: '报表类型',
    key: 'type',
    render: (row: ReportTemplate) => {
      const types = {
        student: '学生个人报表',
        class: '班级排名报表',
        'all-classes': '全校班级报表'
      };
      const type = row.type as keyof typeof types;
      return types[type] || row.type;
    }
  },
  {
    title: '描述',
    key: 'description',
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    render: (row: ReportTemplate) => {
      const date = new Date(row.created_at);
      return date.toLocaleDateString('zh-CN');
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render: (row: ReportTemplate) => {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, {
            quaternary: true,
            size: 'small',
            onClick: () => handlePreviewTemplate(row)
          }, {
            default: () => '预览',
            icon: () => h(NIcon, null, { default: () => h(EyeOutlined) })
          }),
          h(NButton, {
            quaternary: true,
            size: 'small',
            onClick: () => handleEditTemplate(row)
          }, {
            default: () => '编辑',
            icon: () => h(NIcon, null, { default: () => h(EditOutlined) })
          }),
          h(NPopconfirm, {
            onPositiveClick: () => handleDeleteTemplate(row)
          }, {
            default: () => '确定删除此模板吗？',
            trigger: () => h(NButton, {
              quaternary: true,
              size: 'small'
            }, {
              default: () => '删除',
              icon: () => h(NIcon, null, { default: () => h(DeleteOutlined) })
            })
          })
        ]
      });
    }
  }
]);

// 安全的预览内容
const sanitizedPreviewContent = computed(() => {
  // 使用HTML净化函数确保安全
  return sanitizeHTML(previewContent.value);
});

// 加载模板数据
const loadTemplates = async () => {
  loading.value = true;
  try {
    const response = await getReportTemplates();
    if (response.data && response.data.data) {
      templates.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load templates:', error);
    message.error('加载报表模板失败');
  } finally {
    loading.value = false;
  }
};

// 处理页面变更
const handlePageChange = (page: number) => {
  pagination.page = page;
};

// 预览模板
const handlePreviewTemplate = (template: ReportTemplate) => {
  // 填充测试数据进行预览
  let content = template.content;
  
  // 替换变量
  content = content
    .replace(/\{\{\s*CLASS_NAME\s*\}\}/g, '示例班级')
    .replace(/\{\{\s*STUDENT_NAME\s*\}\}/g, '张三')
    .replace(/\{\{\s*DATE_RANGE\s*\}\}/g, '2023-01-01 至 2023-12-31')
    .replace(/\{\{\s*TOTAL_RECORDS\s*\}\}/g, '42')
    .replace(/\{\{\s*TOTAL_SCORE\s*\}\}/g, '360')
    .replace(/\{\{\s*AVERAGE_SCORE\s*\}\}/g, '8.57');
  
  // 替换数据块
  if (content.includes('{{ STUDENT_LIST }}')) {
    content = content.replace(/\{\{\s*STUDENT_LIST\s*\}\}/g, `
      <table class="report-table">
        <tr>
          <th>排名</th>
          <th>学号</th>
          <th>姓名</th>
          <th>总积分</th>
          <th>记录数</th>
        </tr>
        <tr>
          <td>1</td>
          <td>202101</td>
          <td>张三</td>
          <td>95</td>
          <td>10</td>
        </tr>
        <tr>
          <td>2</td>
          <td>202102</td>
          <td>李四</td>
          <td>85</td>
          <td>8</td>
        </tr>
        <tr>
          <td>3</td>
          <td>202103</td>
          <td>王五</td>
          <td>80</td>
          <td>9</td>
        </tr>
      </table>
    `);
  }
  
  if (content.includes('{{ RECORD_LIST }}')) {
    content = content.replace(/\{\{\s*RECORD_LIST\s*\}\}/g, `
      <table class="report-table">
        <tr>
          <th>日期</th>
          <th>量化项目</th>
          <th>分数</th>
          <th>原因</th>
        </tr>
        <tr>
          <td>2023-10-01</td>
          <td>课堂表现</td>
          <td>+5</td>
          <td>积极回答问题</td>
        </tr>
        <tr>
          <td>2023-10-05</td>
          <td>作业完成</td>
          <td>+3</td>
          <td>按时完成作业</td>
        </tr>
        <tr>
          <td>2023-10-10</td>
          <td>纪律表现</td>
          <td>-2</td>
          <td>课堂讲话</td>
        </tr>
      </table>
    `);
  }
  
  if (content.includes('{{ ITEM_DISTRIBUTION }}')) {
    content = content.replace(/\{\{\s*ITEM_DISTRIBUTION\s*\}\}/g, `
      <table class="report-table">
        <tr>
          <th>量化项目</th>
          <th>记录数</th>
          <th>总分</th>
          <th>占比</th>
        </tr>
        <tr>
          <td>课堂表现</td>
          <td>15</td>
          <td>+75</td>
          <td>35.7%</td>
        </tr>
        <tr>
          <td>作业完成</td>
          <td>12</td>
          <td>+36</td>
          <td>28.6%</td>
        </tr>
        <tr>
          <td>纪律表现</td>
          <td>8</td>
          <td>-16</td>
          <td>19%</td>
        </tr>
        <tr>
          <td>考试成绩</td>
          <td>7</td>
          <td>+35</td>
          <td>16.7%</td>
        </tr>
      </table>
    `);
  }
  
  // 添加样式
  content = `
    <style>
      .report-content {
        font-family: Arial, sans-serif;
        padding: 20px;
      }
      .report-header {
        text-align: center;
        margin-bottom: 20px;
      }
      .report-header h1 {
        margin-bottom: 10px;
      }
      .report-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
      }
      .report-table th, .report-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
      }
      .report-table th {
        background-color: #f2f2f2;
      }
    </style>
    <div class="report-content">
      ${content}
    </div>
  `;
  
  previewContent.value = content;
  showPreviewModal.value = true;
};

// 编辑模板
const handleEditTemplate = (template: ReportTemplate) => {
  editingTemplate.value = template;
  formModel.name = template.name;
  formModel.type = template.type;
  formModel.description = template.description || '';
  formModel.content = template.content;
  showCreateModal.value = true;
};

// 删除模板
const handleDeleteTemplate = async (template: ReportTemplate) => {
  try {
    await deleteReportTemplate(template.id);
    message.success('模板删除成功');
    loadTemplates();
  } catch (error) {
    console.error('Failed to delete template:', error);
    message.error('删除模板失败');
  }
};

// 保存模板
const handleSaveTemplate = () => {
  formRef.value?.validate(async (errors: any) => {
    if (errors) {
      return;
    }
    
    saving.value = true;
    
    try {
      const payload: CreateReportTemplatePayload = {
        name: formModel.name,
        type: formModel.type,
        description: formModel.description,
        content: formModel.content
      };
      
      if (editingTemplate.value) {
        // 更新模板
        await updateReportTemplate(editingTemplate.value.id, payload);
        message.success('模板更新成功');
      } else {
        // 创建模板
        await createReportTemplate(payload);
        message.success('模板创建成功');
      }
      
      // 重置表单
      resetForm();
      showCreateModal.value = false;
      loadTemplates();
    } catch (error) {
      console.error('Failed to save template:', error);
      message.error('保存模板失败');
    } finally {
      saving.value = false;
    }
  });
};

// 插入变量
const insertVariable = (variable: string) => {
  const textarea = document.querySelector('.template-editor-container textarea') as HTMLTextAreaElement;
  if (textarea) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = formModel.content;
    const variableText = `{{ ${variable} }}`;
    
    formModel.content = text.substring(0, start) + variableText + text.substring(end);
    
    // 重新设置光标位置
    setTimeout(() => {
      textarea.selectionStart = start + variableText.length;
      textarea.selectionEnd = start + variableText.length;
      textarea.focus();
    }, 0);
  }
};

// 插入数据块
const insertBlock = (blockName: string) => {
  let blockContent = '';
  
  switch (blockName) {
    case 'STUDENT_LIST':
      blockContent = `<div class="student-list">
  <h3>学生排名</h3>
  {{ STUDENT_LIST }}
</div>`;
      break;
    case 'RECORD_LIST':
      blockContent = `<div class="record-list">
  <h3>量化记录</h3>
  {{ RECORD_LIST }}
</div>`;
      break;
    case 'ITEM_DISTRIBUTION':
      blockContent = `<div class="item-distribution">
  <h3>量化项目分布</h3>
  {{ ITEM_DISTRIBUTION }}
</div>`;
      break;
  }
  
  const textarea = document.querySelector('.template-editor-container textarea') as HTMLTextAreaElement;
  if (textarea && blockContent) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = formModel.content;
    
    formModel.content = text.substring(0, start) + blockContent + text.substring(end);
    
    // 重新设置光标位置
    setTimeout(() => {
      textarea.selectionStart = start + blockContent.length;
      textarea.selectionEnd = start + blockContent.length;
      textarea.focus();
    }, 0);
  }
};

// 重置表单
const resetForm = () => {
  formModel.name = '';
  formModel.type = 'class';
  formModel.description = '';
  formModel.content = '';
  editingTemplate.value = null;
};

// 组件加载时获取数据
onMounted(() => {
  loadTemplates();
});
</script>

<style scoped>
.report-templates-page {
  width: 100%;
}

.card-container {
  margin-top: 16px;
}

.template-editor-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.template-editor-header {
  margin-bottom: 8px;
}

.template-editor-footer {
  margin-top: 8px;
  font-size: 12px;
}

.preview-container {
  max-height: 600px;
  overflow-y: auto;
  padding: 0 16px;
  border: 1px solid #eee;
  background-color: white;
}

.preview-content {
  padding: 16px 0;
}
</style> 