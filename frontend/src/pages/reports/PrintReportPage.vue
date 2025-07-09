<template>
  <div class="print-report-page">
    <page-header title="打印报表">
      <template #subtitle>
        生成和打印量化记录统计报表
      </template>
    </page-header>
    
    <!-- 报表配置 -->
    <n-card title="报表配置" class="mb-5">
      <n-form
        ref="formRef"
        :model="formModel"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-grid :cols="24" :x-gap="16">
          <n-gi :span="8">
            <n-form-item label="报表类型" path="reportType">
              <n-select
                v-model:value="formModel.reportType"
                :options="reportTypeOptions"
                placeholder="选择报表类型"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="8">
            <n-form-item label="班级" path="classId">
              <n-select
                v-model:value="formModel.classId"
                clearable
                filterable
                placeholder="选择班级"
                :options="classOptions"
                @update:value="handleClassChange"
                :disabled="formModel.reportType === 'all-classes'"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="8">
            <n-form-item label="学生" path="studentId">
              <n-select
                v-model:value="formModel.studentId"
                clearable
                filterable
                placeholder="选择学生"
                :options="studentOptions"
                :loading="loadingStudents"
                :disabled="!formModel.classId || formModel.reportType === 'class' || formModel.reportType === 'all-classes'"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="8">
            <n-form-item label="日期范围" path="dateRange">
              <n-date-picker
                v-model:value="formModel.dateRange"
                type="daterange"
                clearable
                style="width: 100%"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="8">
            <n-form-item label="排序方式" path="sortBy">
              <n-select
                v-model:value="formModel.sortBy"
                :options="sortOptions"
                placeholder="选择排序方式"
              />
            </n-form-item>
          </n-gi>
          
          <n-gi :span="8">
            <n-form-item label="报表样式" path="template">
              <n-select
                v-model:value="formModel.template"
                :options="templateOptions"
                placeholder="选择报表样式"
              />
            </n-form-item>
          </n-gi>
        </n-grid>
        
        <n-space justify="end">
          <n-button @click="resetForm">重置</n-button>
          <n-button type="primary" @click="generateReport" :loading="loading">
            生成报表
          </n-button>
        </n-space>
      </n-form>
    </n-card>
    
    <!-- 报表预览 -->
    <n-card v-if="reportData" title="报表预览" class="mb-5">
      <template #header-extra>
        <n-space>
          <n-button @click="printReport">
            <template #icon>
              <n-icon><PrinterOutlined /></n-icon>
            </template>
            打印
          </n-button>
          <n-button @click="exportPdf">
            <template #icon>
              <n-icon><FileTextOutlined /></n-icon>
            </template>
            导出PDF
          </n-button>
        </n-space>
      </template>
      
      <!-- 报表内容区域 -->
      <div ref="reportRef" class="report-content">
        <!-- 报表标题 -->
        <div class="report-header">
          <h1>{{ getReportTitle() }}</h1>
          <p class="report-time">生成时间: {{ formatDateTime(new Date()) }}</p>
        </div>
        
        <!-- 报表摘要 -->
        <div class="report-summary">
          <table class="summary-table">
            <tr>
              <th>总记录数</th>
              <th>总积分</th>
              <th>平均分</th>
              <th>覆盖学生数</th>
            </tr>
            <tr>
              <td>{{ reportData.summary.total_records }}</td>
              <td>{{ reportData.summary.total_score }}</td>
              <td>{{ formatNumber(reportData.summary.average_score) }}</td>
              <td>{{ reportData.summary.students_with_records }} / {{ reportData.summary.total_students }}</td>
            </tr>
          </table>
        </div>
        
        <!-- 根据报表类型显示不同的详情 -->
        <div v-if="formModel.reportType === 'student'" class="student-report">
          <h2>学生详情</h2>
          <div class="student-info">
            <p><strong>学号:</strong> {{ reportData.student?.student_id_no }}</p>
            <p><strong>姓名:</strong> {{ reportData.student?.name }}</p>
            <p><strong>班级:</strong> {{ reportData.student?.class_name }}</p>
            <p><strong>总积分:</strong> {{ reportData.student?.total_score }}</p>
            <p><strong>记录数:</strong> {{ reportData.student?.record_count }}</p>
          </div>
          
          <h3>记录详情</h3>
          <table class="detail-table">
            <tr>
              <th>日期</th>
              <th>量化项目</th>
              <th>分数</th>
              <th>原因</th>
              <th>记录人</th>
            </tr>
            <tr v-for="record in reportData.records" :key="record.id">
              <td>{{ formatDate(record.record_date) }}</td>
              <td>{{ record.item_name }}</td>
              <td :class="record.score > 0 ? 'positive' : record.score < 0 ? 'negative' : ''">
                {{ record.score }}
              </td>
              <td>{{ record.reason }}</td>
              <td>{{ record.recorder_name }}</td>
            </tr>
          </table>
        </div>
        
        <div v-else-if="formModel.reportType === 'class' || formModel.reportType === 'all-classes'" class="class-report">
          <h2>{{ formModel.reportType === 'class' ? '班级排名' : '全校班级排名' }}</h2>
          <table class="detail-table">
            <tr>
              <th>排名</th>
              <th>{{ formModel.reportType === 'class' ? '学号' : '班级' }}</th>
              <th>{{ formModel.reportType === 'class' ? '姓名' : '人数' }}</th>
              <th>总积分</th>
              <th>记录数</th>
              <th>平均分</th>
            </tr>
            <tr v-for="(item, index) in reportData.rankings" :key="item.id">
              <td>{{ index + 1 }}</td>
              <td>{{ formModel.reportType === 'class' ? item.student_id_no : item.name }}</td>
              <td>{{ formModel.reportType === 'class' ? item.name : item.student_count }}</td>
              <td :class="item.total_score > 0 ? 'positive' : item.total_score < 0 ? 'negative' : ''">
                {{ item.total_score }}
              </td>
              <td>{{ item.record_count }}</td>
              <td>{{ formatNumber(item.average_score) }}</td>
            </tr>
          </table>
        </div>
        
        <!-- 项目分布 -->
        <div class="distribution-section">
          <h2>量化项目分布</h2>
          <table class="detail-table">
            <tr>
              <th>项目名称</th>
              <th>分类</th>
              <th>记录数</th>
              <th>总分</th>
              <th>占比</th>
            </tr>
            <tr v-for="item in reportData.item_distribution" :key="item.item_id">
              <td>{{ item.item_name }}</td>
              <td>{{ item.category || '-' }}</td>
              <td>{{ item.count }}</td>
              <td :class="item.score_sum > 0 ? 'positive' : item.score_sum < 0 ? 'negative' : ''">
                {{ item.score_sum }}
              </td>
              <td>{{ formatPercent(item.count / reportData.summary.total_records) }}</td>
            </tr>
          </table>
        </div>
        
        <!-- 生成的报表页脚 -->
        <div class="report-footer">
          <p>AuraClass 班级量化管理系统 &copy; {{ new Date().getFullYear() }}</p>
          <p>页码: 1/1</p>
        </div>
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { 
  NCard, 
  NForm, 
  NFormItem, 
  NButton, 
  NSelect, 
  NDatePicker, 
  NGrid, 
  NGi, 
  NSpace,
  NIcon,
  useMessage
} from 'naive-ui';
import PrinterOutlined from '@vicons/antd/es/PrinterOutlined';
import FileTextOutlined from '@vicons/antd/es/FileTextOutlined';
import PageHeader from '@/components/layout/PageHeader.vue';
import { getClasses } from '@/services/api/classes';
import { getStudents } from '@/services/api/students';
import { generateReportData, exportReportPdf } from '@/services/api/reports';
import type { FormInst } from 'naive-ui';
import type { SelectOption } from 'naive-ui';

// 组件状态
const message = useMessage();
const formRef = ref<FormInst | null>(null);
const reportRef = ref<HTMLElement | null>(null);
const loading = ref(false);
const loadingStudents = ref(false);
const classes = ref<{ id: number; name: string }[]>([]);
const students = ref<{ id: number; student_id_no: string; full_name: string }[]>([]);
const reportData = ref<any>(null);

// 表单数据
const formModel = reactive({
  reportType: 'class' as 'student' | 'class' | 'all-classes',
  classId: null as number | null,
  studentId: null as number | null,
  dateRange: null as [number, number] | null,
  sortBy: 'score-desc' as string,
  template: 'standard' as string
});

// 选项
const reportTypeOptions = [
  { label: '学生个人报表', value: 'student' },
  { label: '班级排名报表', value: 'class' },
  { label: '全校班级报表', value: 'all-classes' }
];

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

const sortOptions = [
  { label: '按积分降序', value: 'score-desc' },
  { label: '按积分升序', value: 'score-asc' },
  { label: '按记录数降序', value: 'count-desc' },
  { label: '按记录数升序', value: 'count-asc' }
];

const templateOptions = [
  { label: '标准模板', value: 'standard' },
  { label: '简洁模板', value: 'simple' },
  { label: '详细模板', value: 'detailed' }
];

// 班级变更处理
const handleClassChange = (value: number | null) => {
  formModel.classId = value;
  formModel.studentId = null;
  
  if (value) {
    loadStudentsByClass(value);
  } else {
    students.value = [];
  }
};

// 加载班级数据
const loadClasses = async () => {
  try {
    const response = await getClasses();
    if (response.data && response.data.data) {
      classes.value = response.data.data;
    }
  } catch (error) {
    console.error('Failed to load classes:', error);
    message.error('加载班级数据失败');
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

// 生成报表
const generateReport = async () => {
  loading.value = true;
  
  try {
    const params: Record<string, any> = {
      report_type: formModel.reportType,
      sort_by: formModel.sortBy,
      template: formModel.template
    };
    
    if (formModel.classId) {
      params.class_id = formModel.classId;
    }
    
    if (formModel.studentId) {
      params.student_id = formModel.studentId;
    }
    
    if (formModel.dateRange) {
      const [startDate, endDate] = formModel.dateRange;
      params.start_date = new Date(startDate).toISOString().split('T')[0];
      params.end_date = new Date(endDate).toISOString().split('T')[0];
    }
    
    const response = await generateReportData(params);
    
    if (response.data && response.data.data) {
      reportData.value = response.data.data;
    } else {
      message.error('无法生成报表数据');
    }
  } catch (error) {
    console.error('Failed to generate report:', error);
    message.error('生成报表失败');
  } finally {
    loading.value = false;
  }
};

// 打印报表
const printReport = () => {
  if (!reportRef.value) {
    message.error('报表内容不存在');
    return;
  }
  
  const printWindow = window.open('', '_blank');
  if (!printWindow) {
    message.error('无法打开打印窗口，请检查浏览器设置');
    return;
  }
  
  // 创建基本样式
  const style = `
    <style>
      body { font-family: Arial, sans-serif; padding: 20px; }
      .report-header { text-align: center; margin-bottom: 20px; }
      .report-header h1 { margin-bottom: 10px; }
      .report-time { color: #666; font-size: 14px; }
      .report-summary { margin-bottom: 30px; }
      .summary-table, .detail-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
      .summary-table th, .summary-table td, .detail-table th, .detail-table td { 
        border: 1px solid #ddd; padding: 8px; text-align: center; 
      }
      .summary-table th, .detail-table th { background-color: #f2f2f2; }
      .student-info { margin-bottom: 20px; }
      .student-info p { margin: 5px 0; }
      .positive { color: #18a058; }
      .negative { color: #d03050; }
      .report-footer { 
        margin-top: 30px; 
        text-align: center; 
        font-size: 12px; 
        color: #666;
        border-top: 1px solid #eee;
        padding-top: 10px;
      }
      @media print {
        body { padding: 0; }
        button { display: none; }
      }
    </style>
  `;
  
  // 设置打印窗口内容
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>${getReportTitle()}</title>
        ${style}
      </head>
      <body>
        ${reportRef.value.innerHTML}
      </body>
    </html>
  `);
  
  printWindow.document.close();
  
  // 完成加载后打印
  printWindow.onload = () => {
    printWindow.print();
  };
};

// 导出PDF
const exportPdf = () => {
  if (!reportRef.value) {
    message.error('报表内容不存在');
    return;
  }
  
  const element = reportRef.value;
  const filename = `${getReportTitle()}_${formatDate(new Date())}.pdf`;
  
  message.loading('正在导出PDF...');
  
  // 动态导入html2pdf
  import('html2pdf.js').then((html2pdf) => {
    const options = {
      margin: 10,
      filename: filename,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    
    html2pdf.default().set(options).from(element).save().then(() => {
      message.success('PDF导出成功');
    }).catch((error: Error) => {
      console.error('Failed to export PDF:', error);
      message.error('PDF导出失败');
    });
  }).catch((error: Error) => {
    console.error('Failed to load html2pdf:', error);
    message.error('加载PDF导出工具失败');
  });
};

// 重置表单
const resetForm = () => {
  formModel.reportType = 'class';
  formModel.classId = null;
  formModel.studentId = null;
  formModel.dateRange = null;
  formModel.sortBy = 'score-desc';
  formModel.template = 'standard';
  reportData.value = null;
};

// 获取报表标题
const getReportTitle = () => {
  const typeName = reportTypeOptions.find(opt => opt.value === formModel.reportType)?.label || '';
  const className = formModel.classId 
    ? classes.value.find(cls => cls.id === formModel.classId)?.name 
    : '';
  const studentName = formModel.studentId
    ? students.value.find(s => s.id === formModel.studentId)?.full_name
    : '';
  
  let title = typeName;
  
  if (className && formModel.reportType !== 'all-classes') {
    title += ` - ${className}`;
  }
  
  if (studentName && formModel.reportType === 'student') {
    title += ` - ${studentName}`;
  }
  
  return title;
};

// 工具函数: 格式化日期
const formatDate = (date: Date | string) => {
  if (typeof date === 'string') {
    date = new Date(date);
  }
  return date.toISOString().split('T')[0];
};

// 工具函数: 格式化日期时间
const formatDateTime = (date: Date) => {
  return date.toLocaleString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  });
};

// 工具函数: 格式化数字
const formatNumber = (value: number) => {
  return value.toFixed(2);
};

// 工具函数: 格式化百分比
const formatPercent = (value: number) => {
  return `${(value * 100).toFixed(2)}%`;
};

// 组件挂载
onMounted(() => {
  loadClasses();
});
</script>

<style scoped>
.print-report-page {
  width: 100%;
}

.mb-5 {
  margin-bottom: 20px;
}

.report-content {
  padding: 20px;
  background-color: white;
  border: 1px solid #eee;
}

.report-header {
  text-align: center;
  margin-bottom: 30px;
}

.report-header h1 {
  margin-bottom: 10px;
}

.report-time {
  color: #888;
  font-size: 14px;
}

.report-summary {
  margin-bottom: 30px;
}

.summary-table,
.detail-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.summary-table th,
.summary-table td,
.detail-table th,
.detail-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

.summary-table th,
.detail-table th {
  background-color: #f2f2f2;
}

.student-report h2,
.class-report h2,
.distribution-section h2 {
  margin: 20px 0 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.student-info {
  margin-bottom: 20px;
}

.student-info p {
  margin: 5px 0;
}

.positive {
  color: #18a058;
}

.negative {
  color: #d03050;
}

.report-footer {
  margin-top: 40px;
  text-align: center;
  font-size: 12px;
  color: #888;
  border-top: 1px solid #eee;
  padding-top: 10px;
}
</style> 