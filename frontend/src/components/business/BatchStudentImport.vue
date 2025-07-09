<template>
  <div>
    <n-card title="批量导入学生" class="mb-4">
      <n-space vertical>
        <n-alert type="info" class="mb-4">
          <template #icon>
            <n-icon>
              <InformationCircleOutline />
            </n-icon>
          </template>
          <p>请上传包含学生信息的CSV文件，或下载模板后填写再上传。</p>
          <p>文件第一行需要包含以下列（必填字段标有*）：</p>
          <p>
            <span class="text-primary">
              "*学号", "*姓名", "*班级ID", "*性别", "出生日期", "电话", "邮箱", "联系信息"
            </span>
          </p>
          <p class="text-xs text-gray-500 mt-1">
            <span class="mr-4">* 号标记为必填字段</span>
            <span class="mr-4">性别取值: male(男)/female(女)</span>
            <span>日期格式: YYYY-MM-DD (例如: 2000-01-01)</span>
          </p>
        </n-alert>
        
        <div class="flex items-center gap-4 mb-4">
          <n-button @click="downloadTemplate" type="info">
            <template #icon>
              <n-icon>
                <DownloadOutline />
              </n-icon>
            </template>
            下载导入模板
          </n-button>
          
          <n-upload
            ref="uploadRef"
            accept=".csv"
            :custom-request="customRequest"
            :show-file-list="false"
            :max="1"
          >
            <n-button type="primary">
              <template #icon>
                <n-icon>
                  <CloudUploadOutline />
                </n-icon>
              </template>
              选择CSV文件
            </n-button>
          </n-upload>
        </div>
        
        <template v-if="fileData">
          <div class="mb-4">
            <div class="flex justify-between items-center mb-2">
              <span class="font-medium">文件预览：{{ fileName }}</span>
              <n-button text @click="resetUpload">
                <template #icon>
                  <n-icon>
                    <CloseCircleOutline />
                  </n-icon>
                </template>
                清除
              </n-button>
            </div>
            
            <n-data-table
              :columns="previewColumns"
              :data="previewData"
              :pagination="{ pageSize: 5 }"
              :max-height="300"
              :scroll-x="1200"
            />
          </div>
          
          <n-space justify="end">
            <n-button
              type="primary"
              @click="handleImport"
              :loading="importing"
              :disabled="!fileData || previewData.length === 0"
            >
              开始导入 ({{ previewData.length }}条)
            </n-button>
          </n-space>
        </template>
      </n-space>
    </n-card>
    
    <!-- 导入结果 -->
    <n-card v-if="importResult" title="导入结果" class="mb-4">
      <n-space vertical>
        <n-alert :type="importResult.success ? 'success' : 'warning'">
          <template #icon>
            <n-icon>
              <component :is="importResult.success ? 'checkmark-circle-outline' : 'alert-circle-outline'" />
            </n-icon>
          </template>
          <p v-if="importResult.success">成功导入 {{ importResult.successCount }} 条记录</p>
          <p v-else>
            导入完成，成功: {{ importResult.successCount }}，
            失败: {{ importResult.failedCount }}
          </p>
        </n-alert>
        
        <n-collapse v-if="importResult.failedRecords && importResult.failedRecords.length > 0">
          <n-collapse-item title="查看失败记录" name="1">
            <n-data-table
              :columns="errorColumns"
              :data="importResult.failedRecords"
              :pagination="{ pageSize: 5 }"
              :max-height="300"
            />
          </n-collapse-item>
        </n-collapse>
      </n-space>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, defineEmits } from 'vue';
import { 
  NCard, 
  NSpace, 
  NButton, 
  NAlert, 
  NIcon, 
  NUpload, 
  NDataTable,
  NCollapse,
  NCollapseItem,
  useMessage
} from 'naive-ui';
import InformationCircleOutline from '@vicons/ionicons5/es/InformationCircleOutline';
import DownloadOutline from '@vicons/ionicons5/es/DownloadOutline';
import CloudUploadOutline from '@vicons/ionicons5/es/CloudUploadOutline';
import CloseCircleOutline from '@vicons/ionicons5/es/CloseCircleOutline';
import CheckmarkCircleOutline from '@vicons/ionicons5/es/CheckmarkCircleOutline';
import AlertCircleOutline from '@vicons/ionicons5/es/AlertCircleOutline';
import { importStudents } from '@/services/api/students';
// @ts-ignore
import { getClasses } from '@/services/api/classes';
import type { UploadCustomRequestOptions, UploadInst, DataTableColumns } from 'naive-ui';
import type { CreateStudentPayload } from '@/types/student';

interface ClassOption {
  id: number;
  name: string;
}

const emit = defineEmits(['success']);
const message = useMessage();
const uploadRef = ref<UploadInst | null>(null);

// File data
const fileName = ref('');
const fileData = ref<string | null>(null);
const previewData = ref<any[]>([]);
const importing = ref(false);
const importResult = ref<{
  success: boolean;
  successCount: number;
  failedCount: number;
  failedRecords?: any[];
} | null>(null);

// Class options for mapping
const classOptions = ref<ClassOption[]>([]);

// Load classes for mapping
const loadClasses = async () => {
  try {
    const response = await getClasses();
    if (response && response.data) {
      classOptions.value = response.data;
    }
  } catch (error) {
    console.error('Failed to load classes:', error);
    message.error('加载班级数据失败');
  }
};

// Call loadClasses when component is mounted
loadClasses();

// Preview columns
const previewColumns: DataTableColumns = [
  { title: '行号', key: 'rowIndex' },
  { title: '学号 *', key: 'student_id_no' },
  { title: '姓名 *', key: 'full_name' },
  { title: '班级 *', key: 'class_name' },
  { title: '性别 *', key: 'gender_display' },
  { title: '出生日期', key: 'birth_date' },
  { title: '电话', key: 'phone' },
  { title: '邮箱', key: 'email' },
  { title: '联系信息', key: 'contact_info' }
];

// Error columns
const errorColumns: DataTableColumns = [
  { title: '行号', key: 'rowIndex' },
  { title: '学号', key: 'student_id_no' },
  { title: '姓名', key: 'full_name' },
  { title: '错误原因', key: 'error' }
];

// Custom upload request handler
const customRequest = ({ file }: UploadCustomRequestOptions) => {
  if (!file) return;
  
  const reader = new FileReader();
  fileName.value = file.name;
  
  reader.onload = (e) => {
    const content = e.target?.result as string;
    if (content) {
      fileData.value = content;
      parseCSV(content);
    }
  };
  
  if (file.file) {
    reader.readAsText(file.file as Blob);
  }
};

// Parse CSV content
const parseCSV = (content: string) => {
  if (!content) return;
  
  try {
    // Split by lines and remove empty lines
    const lines = content.split('\n').filter(line => line.trim());
    if (lines.length < 2) {
      message.error('CSV文件格式不正确或为空');
      return;
    }
    
    // Get headers (first line)
    const headers = lines[0].split(',').map(header => {
      // 去除标题中的星号和空格
      return header.trim().replace(/^\*+/, '').toLowerCase();
    });
    
    // Required fields mapping
    const fieldMapping = {
      'student_id_no': ['学号', 'studentidno', 'student_id_no', 'id'],
      'full_name': ['姓名', 'fullname', 'full_name', 'name'],
      'class_id': ['班级id', 'classid', 'class_id', '班级'],
      'gender': ['性别', 'gender'],
      'birth_date': ['出生日期', 'birthdate', 'birth_date', 'birth'],
      'phone': ['电话', 'phone', 'tel', 'telephone'],
      'email': ['邮箱', 'email', 'mail'],
      'contact_info': ['联系信息', 'contactinfo', 'contact_info', '备注', 'notes']
    };
    
    // 必需字段列表
    const requiredFields = ['student_id_no', 'full_name', 'class_id', 'gender'];
    
    // Map CSV columns to field names
    const columnIndexes: Record<string, number> = {};
    
    // For each required field, find its index in the CSV headers
    Object.entries(fieldMapping).forEach(([fieldName, possibleNames]) => {
      const index = headers.findIndex(header => 
        possibleNames.some(name => header === name.toLowerCase())
      );
      
      if (index !== -1) {
        columnIndexes[fieldName] = index;
      } else if (requiredFields.includes(fieldName)) {
        message.warning(`CSV文件缺少必需的字段: ${possibleNames[0]}`);
      }
    });
    
    // Check if required fields are present
    const missingRequiredFields = requiredFields.filter(
      field => !(field in columnIndexes)
    );
    
    if (missingRequiredFields.length > 0) {
      message.error(`CSV文件缺少必需的字段: ${missingRequiredFields.join(', ')}`);
      return;
    }
    
    // Parse data rows
    const parsedData = [];
    
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      // 跳过注释行和空行
      if (!line || line.startsWith('#')) continue;
      
      const values = line.split(',').map(val => val.trim());
      
      // Skip rows with insufficient values
      if (values.length < 3) continue;
      
      const rowData: Record<string, any> = {
        rowIndex: i
      };
      
      // Map values based on column indexes
      Object.entries(columnIndexes).forEach(([fieldName, index]) => {
        if (index < values.length) {
          rowData[fieldName] = values[index];
        }
      });
      
      // Process specific fields
      if (rowData.class_id) {
        // Try to map class name to ID if it's not a number
        if (isNaN(Number(rowData.class_id))) {
          const classMatch = classOptions.value.find(c => 
            c.name.toLowerCase() === rowData.class_id.toLowerCase());
          
          if (classMatch) {
            rowData.class_id = classMatch.id;
            rowData.class_name = classMatch.name;
          }
        } else {
          // If it's a number, get the class name for display
          const classId = Number(rowData.class_id);
          const classMatch = classOptions.value.find(c => c.id === classId);
          if (classMatch) {
            rowData.class_name = classMatch.name;
          }
        }
      }
      
      // Format gender for display - store both display and API value
      if (rowData.gender) {
        const normalizedGender = normalizeGender(rowData.gender);
        rowData.gender_display = formatGender(normalizedGender);
        rowData.gender = normalizedGender; // 保存API所需的male/female值
      }
      
      parsedData.push(rowData);
    }
    
    previewData.value = parsedData;
  } catch (error) {
    console.error('Failed to parse CSV:', error);
    message.error('解析CSV文件失败');
  }
};

// Normalize gender value to API format (male/female)
const normalizeGender = (value: string): string => {
  value = value.toLowerCase();
  if (['male', 'm', '男', '男性', '1'].includes(value)) {
    return 'male';
  }
  if (['female', 'f', '女', '女性', '0'].includes(value)) {
    return 'female';
  }
  return value;
};

// Format gender value for display
const formatGender = (value: string): string => {
  value = value.toLowerCase();
  if (['male', 'm', '男', '男性', '1'].includes(value)) {
    return '男';
  }
  if (['female', 'f', '女', '女性', '0'].includes(value)) {
    return '女';
  }
  return value;
};

// Download template
const downloadTemplate = () => {
  // 添加必填标记
  const header = '*学号,*姓名,*班级ID,*性别,出生日期,电话,邮箱,联系信息';
  
  // 准备示例数据和说明
  let content = `${header}\n`;
  content += '# 必填字段已用"*"标记。以下是示例数据，请删除并替换成您的数据\n';
  content += '# 性别取值: male(男)/female(女)\n';
  content += '# 日期格式必须为: YYYY-MM-DD (例如：2000-01-01)\n';
  content += '# 班级ID必须是系统中已存在的班级ID\n';
  content += '201901,张三,1,male,2000-01-01,13812345678,zhangsan@example.com,联系信息备注\n';
  content += '201902,李四,1,female,2000-02-02,13987654321,lisi@example.com,家长电话: 13800138000';
  
  // 添加 BOM 标记确保 UTF-8 编码被正确识别（防止Windows平台中文乱码）
  const BOM = new Uint8Array([0xEF, 0xBB, 0xBF]);
  const textEncoder = new TextEncoder();
  const contentArray = textEncoder.encode(content);
  
  // 合并BOM和内容
  const blob = new Blob([BOM, contentArray], { type: 'text/csv;charset=utf-8' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = '学生导入模板.csv';
  link.click();
};

// Reset upload
const resetUpload = () => {
  fileName.value = '';
  fileData.value = null;
  previewData.value = [];
  if (uploadRef.value) {
    // @ts-ignore: uploadRef实例在运行时存在clear方法
    uploadRef.value.clear();
  }
};

// Import students
const handleImport = async () => {
  if (!fileData.value || previewData.value.length === 0) return;
  
  importing.value = true;
  importResult.value = null;
  
  try {
    // Validate data before sending
    const validRecords: CreateStudentPayload[] = [];
    const invalidRecords: any[] = [];
    
    previewData.value.forEach((record) => {
      // Validate record
      const errors = validateStudentRecord(record);
      
      if (errors.length === 0) {
        // Valid record, transform data if needed
        validRecords.push({
          student_id_no: record.student_id_no,
          full_name: record.full_name,
          class_id: Number(record.class_id),
          gender: record.gender, // 已在parseCSV阶段标准化为male/female
          birth_date: record.birth_date || undefined,
          phone: record.phone || '',
          email: record.email || '',
          contact_info: record.contact_info || '',
          is_active: true // Default to active
        });
      } else {
        // Invalid record, add to failed list
        invalidRecords.push({
          ...record,
          error: errors.join('; ')
        });
      }
    });
    
    if (validRecords.length === 0) {
      message.error('没有有效的学生记录可以导入');
      importResult.value = {
        success: false,
        successCount: 0,
        failedCount: invalidRecords.length,
        failedRecords: invalidRecords
      };
      return;
    }
    
    // Show preview of valid/invalid records
    if (invalidRecords.length > 0) {
      message.warning(`有 ${invalidRecords.length} 条记录验证失败，将仅导入有效记录`);
    }
    
    // Proceed with import
    const response = await importStudents(validRecords);
    
    // Handle response
    if (response.data) {
      const { success, imported, failed, failedRecords } = response.data;
      
      importResult.value = {
        success: failed === 0,
        successCount: imported,
        failedCount: failed + invalidRecords.length,
        failedRecords: [
          ...invalidRecords,
          ...(failedRecords || [])
        ]
      };
      
      if (imported > 0) {
        message.success(`成功导入 ${imported} 条学生记录`);
        emit('success');
      } else {
        message.error('没有学生记录被成功导入');
      }
    } else {
      throw new Error('导入响应数据格式错误');
    }
  } catch (error: any) {
    console.error('Import failed:', error);
    message.error(error.response?.data?.error?.message || '导入学生数据失败');
    
    importResult.value = {
      success: false,
      successCount: 0,
      failedCount: previewData.value.length,
      failedRecords: previewData.value.map(record => ({
        ...record,
        error: error.response?.data?.error?.message || '服务器错误'
      }))
    };
  } finally {
    importing.value = false;
  }
};

// Validate student record
const validateStudentRecord = (record: any): string[] => {
  const errors: string[] = [];
  
  // Check required fields
  if (!record.student_id_no) {
    errors.push('学号不能为空');
  } else if (!/^[a-zA-Z0-9_-]{1,20}$/.test(record.student_id_no)) {
    errors.push('学号格式不正确 (应为1-20位字母、数字、下划线或连字符)');
  }
  
  if (!record.full_name) {
    errors.push('姓名不能为空');
  } else if (record.full_name.length > 50) {
    errors.push('姓名长度不能超过50个字符');
  }
  
  if (!record.class_id) {
    errors.push('班级ID不能为空');
  } else {
    // Verify class_id exists
    const classId = Number(record.class_id);
    const classExists = classOptions.value.some(c => c.id === classId);
    if (!classExists) {
      errors.push(`班级ID ${record.class_id} 不存在`);
    }
  }
  
  // Validate gender if present
  if (!record.gender) {
    errors.push('性别不能为空');
  } else if (!['male', 'female'].includes(record.gender)) {
    errors.push('性别必须为 male 或 female');
  }
  
  // Validate birth_date if present
  if (record.birth_date) {
    // 检查日期格式是否为 YYYY-MM-DD
    if (!/^\d{4}-\d{2}-\d{2}$/.test(record.birth_date)) {
      errors.push('出生日期格式必须为 YYYY-MM-DD，例如：2000-01-01');
    }
  }
  
  // Validate phone if present
  if (record.phone && !/^1[3-9]\d{9}$/.test(record.phone)) {
    errors.push('手机号码格式不正确');
  }
  
  // Validate email if present
  if (record.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(record.email)) {
    errors.push('邮箱格式不正确');
  }
  
  return errors;
};
</script>

<style scoped>
.text-primary {
  color: var(--primary-color);
  font-weight: 500;
}
</style> 