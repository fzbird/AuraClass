<template>
  <div>
    <n-card title="批量导入量化记录" class="mb-4">
      <n-space vertical>
        <n-alert type="info" class="mb-4">
          <template #icon>
            <n-icon>
              <InformationCircleOutline />
            </n-icon>
          </template>
          <p>请上传包含量化记录信息的CSV文件，或下载模板后填写再上传。</p>
          <p>文件第一行需要包含以下列（列名不分大小写）：</p>
          <p>
            <span class="text-primary">"学号", "项目ID", "分数", "原因", "记录日期"</span>
          </p>
          <p>如果导入后出现中文乱码，请尝试切换文件编码重新导入。</p>
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
            :custom-request="handleCustomUpload"
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
          
          <n-select 
            v-model:value="selectedEncoding" 
            :options="encodingOptions"
            placeholder="选择文件编码"
            style="width: 140px;"
          />
          
          <n-button 
            v-if="fileData" 
            @click="reloadWithEncoding" 
            type="warning"
          >
            <template #icon>
              <n-icon>
                <RefreshOutline />
              </n-icon>
            </template>
            重新加载
          </n-button>
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
          
          <div class="flex justify-between mt-4">
            <div>
              <n-button @click="downloadTemplate" type="primary" ghost>
                下载模板
              </n-button>
            </div>
            <div>
              <n-button v-if="previewData.length" @click="fixAllDates" class="mr-2" type="warning" ghost>
                修复日期格式
              </n-button>
              <n-button v-if="previewData.length" @click="resetUpload" class="mr-2">
                重置
              </n-button>
              <n-button 
                v-if="previewData.length" 
                @click="handleImport" 
                type="primary"
                :loading="importing"
              >
                导入
              </n-button>
            </div>
          </div>
        </template>
      </n-space>
    </n-card>
    
    <!-- 导入结果 -->
    <n-card v-if="importResult" title="导入结果" class="mb-4">
      <n-space vertical>
        <n-alert :type="importResult.success ? 'success' : 'warning'">
          <template #icon>
            <n-icon>
              <component :is="importResult.success ? CheckmarkCircleOutline : AlertCircleOutline" />
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
import { ref, defineEmits, onMounted, computed, h, watch } from 'vue';
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
  useMessage,
  NTag,
  NDivider,
  NSelect
} from 'naive-ui';
import InformationCircleOutline from '@vicons/ionicons5/es/InformationCircleOutline';
import DownloadOutline from '@vicons/ionicons5/es/DownloadOutline';
import CloudUploadOutline from '@vicons/ionicons5/es/CloudUploadOutline';
import CloseCircleOutline from '@vicons/ionicons5/es/CloseCircleOutline';
import CheckmarkCircleOutline from '@vicons/ionicons5/es/CheckmarkCircleOutline';
import AlertCircleOutline from '@vicons/ionicons5/es/AlertCircleOutline';
import RefreshOutline from '@vicons/ionicons5/es/RefreshOutline';
// @ts-ignore
import { createQuantRecords, importRecords } from '@/services/api/records';
// @ts-ignore
import { getQuantItems } from '@/services/api/quant-items';
// @ts-ignore
import { getStudents } from '@/services/api/students';
import type { UploadCustomRequestOptions, UploadInst, DataTableColumns } from 'naive-ui';
import type { CreateQuantRecordPayload } from '@/types/record';
import type { UploadFileInfo } from 'naive-ui';
import type { Student } from '@/types/student';
import type { QuantItem } from '@/types/quant-item';
import { useUserStore } from '@/stores/user';

// 使用 any 类型替代命名空间
type UploadRef = any;  // 替代 UploadInst
type TableColumn = any;  // 替代 DataTableColumns
type CustomRequestOptions = any;  // 替代 UploadCustomRequestOptions

// 组件属性
const props = defineProps({
  classId: { type: Number, default: undefined }
});

// 事件
const emit = defineEmits(['success']);

// 工具
const message = useMessage();
const userStore = useUserStore();

// 编码选项
const encodingOptions = [
  { label: 'UTF-8', value: 'UTF-8' },
  { label: 'GB18030', value: 'GB18030' },
  { label: 'GBK', value: 'GBK' },
  { label: 'GB2312', value: 'GB2312' },
];
const selectedEncoding = ref('UTF-8');

// 状态
const uploadRef = ref<UploadRef | null>(null);
const fileName = ref('');
const fileData = ref<string | null>(null);
const previewData = ref<Record<string, any>[]>([]);
const importing = ref(false);
const importResult = ref<{
  success: boolean;
  successCount: number;
  failedCount: number;
  failedRecords?: Array<Record<string, any>>;
} | null>(null);

// 数据源
const students = ref<Student[]>([]);
const quantItems = ref<QuantItem[]>([]);

// 加载学生和量化项目数据
onMounted(async () => {
  try {
    // 获取学生数据
    const studentsRes = await getStudents({ page_size: 1000 });
    console.log('获取到学生数据:', studentsRes);
    
    // 使用类型断言处理响应数据
    try {
      // @ts-ignore - 忽略类型错误，使用动态访问方式获取数据
      const studentsData = studentsRes?.data?.data || studentsRes?.data || [];
      students.value = Array.isArray(studentsData) ? studentsData : [];
      console.log(`成功加载 ${students.value.length} 名学生数据`);
    } catch (e) {
      console.error('解析学生数据失败:', e);
      students.value = [];
    }
    
    // 获取量化项目数据
    const quantItemsRes = await getQuantItems();
    console.log('获取到量化项目数据:', quantItemsRes);
    
    // 使用类型断言处理响应数据
    try {
      // @ts-ignore - 忽略类型错误，使用动态访问方式获取数据
      const itemsData = quantItemsRes?.data?.data || quantItemsRes?.data || [];
      quantItems.value = Array.isArray(itemsData) ? itemsData : [];
      console.log(`成功加载 ${quantItems.value.length} 个量化项目数据`);
    } catch (e) {
      console.error('解析量化项目数据失败:', e);
      quantItems.value = [];
    }
  } catch (error) {
    console.error('加载基础数据失败:', error);
    message.error('加载学生和量化项目数据失败');
  }
});

// 预览表格列
const previewColumns = computed(() => [
  { title: '行号', key: 'rowIndex' },
  { title: '学号', key: 'student_id_no' },
  { title: '学生', key: 'student_name' },
  { title: '量化项目', key: 'item_name' },
  { title: '分数', key: 'score' },
  { title: '原因', key: 'reason' },
  { 
    title: '日期', 
    key: 'record_date',
    render: (row: any) => {
      const isValidFormat = /^\d{4}-\d{2}-\d{2}$/.test(String(row.record_date));
      if (!isValidFormat) {
        return h(
          'div',
          {
            style: {
              color: 'var(--error-color)',
              display: 'flex',
              alignItems: 'center'
            }
          },
          [
            h('span', { style: { marginRight: '4px' } }, row.record_date),
            h(
              NTag,
              { type: 'error', size: 'small' },
              { default: () => '格式错误' }
            )
          ]
        );
      }
      return row.record_date;
    }
  }
]);

// 错误列表列
const errorColumns = computed(() => [
  { title: '行号', key: 'rowIndex' },
  { title: '学号', key: 'student_id_no' },
  { title: '项目ID', key: 'item_id' },
  { title: '错误原因', key: 'error' }
]);

// 修改自定义上传处理函数名称，确保与模板中一致
const handleCustomUpload = ({ file }: CustomRequestOptions) => {
  if (!file) {
    console.error('上传失败：未获取到文件');
    message.error('文件上传失败');
    return;
  }
  
  console.log('开始处理上传文件:', file.name);
  const reader = new FileReader();
  fileName.value = file.name;
  
  reader.onload = (e) => {
    let content = e.target?.result as string;
    if (content) {
      console.log('文件读取成功，内容长度:', content.length);
      
      // 检测并处理BOM标记
      if (content.charCodeAt(0) === 0xFEFF) {
        console.log('检测到BOM标记，将移除');
        content = content.substring(1);
      }
      
      fileData.value = content;
      parseCSV(content);
    } else {
      console.error('文件内容为空');
      message.error('文件内容为空或格式错误');
    }
  };
  
  reader.onerror = (error) => {
    console.error('文件读取错误:', error);
    message.error('文件读取失败，请检查文件格式或编码是否正确');
  };
  
  // 使用用户选择的编码读取文件
  if (file.file) {
    try {
      console.log(`使用 ${selectedEncoding.value} 编码读取文件`);
      reader.readAsText(file.file as Blob, selectedEncoding.value);
    } catch (error) {
      console.error('文件读取错误:', error);
      message.error('文件读取失败，请尝试更换编码方式');
    }
  } else {
    console.error('上传文件格式错误');
    message.error('文件格式错误');
  }
};

// 解析CSV内容
const parseCSV = (content: string) => {
  if (!content) {
    console.error('CSV内容为空');
    return;
  }
  
  console.log('开始解析CSV内容');
  
  try {
    // 按行分割并移除空行
    const lines = content.split(/\r?\n/).filter(line => line.trim());
    console.log(`解析到 ${lines.length} 行数据`);
    
    if (lines.length < 2) {
      console.error('CSV文件格式不正确或为空');
      message.error('CSV文件格式不正确或为空');
      return;
    }
    
    // 获取表头（第一行）
    const headers = parseCSVLine(lines[0]).map(header => header.trim().toLowerCase());
    console.log('解析到表头:', headers);
    
    // 必要字段映射
    const fieldMapping = {
      'student_id_no': ['学号', 'studentidno', 'student_id_no', 'student_id'],
      'item_id': ['项目id', 'itemid', 'item_id', '量化项目id', 'quant_item_id', '项目'],
      'score': ['分数', 'score', '分值', 'value'],
      'reason': ['原因', 'reason', '备注', 'note', 'remark'],
      'record_date': ['记录日期', 'recorddate', 'record_date', 'date']
    };
    
    // 映射CSV列到字段名
    const columnIndexes: Record<string, number> = {};
    
    // 为每个必要字段找到对应的列索引
    Object.entries(fieldMapping).forEach(([fieldName, possibleNames]) => {
      const index = headers.findIndex(header => 
        possibleNames.includes(header));
      
      if (index !== -1) {
        columnIndexes[fieldName] = index;
        console.log(`字段 ${fieldName} 对应列索引: ${index}`);
      } else {
        console.warn(`未找到字段 ${fieldName} 对应的列`);
      }
    });
    
    // 检查必要字段是否存在
    if (!('student_id_no' in columnIndexes) || !('item_id' in columnIndexes) || !('score' in columnIndexes)) {
      console.error('缺少必要字段', columnIndexes);
      message.error('CSV必须包含学号、项目ID和分数字段');
      return;
    }
    
    // 解析数据行
    const parsedData = [];
    let successRows = 0;
    let skippedRows = 0;
    
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) {
        console.log(`第 ${i} 行为空，跳过`);
        continue;
      }
      
      // 使用改进的CSV行解析
      const values = parseCSVLine(line);
      
      // 跳过数据不足的行
      if (values.length < 3) {
        console.log(`第 ${i} 行数据不足，跳过: ${line}`);
        skippedRows++;
        continue;
      }
      
      // 跳过注释行（以#开头）
      if (values[0].startsWith('#')) {
        console.log(`第 ${i} 行为注释行，跳过: ${line}`);
        skippedRows++;
        continue;
      }
      
      const rowData: Record<string, any> = {
        rowIndex: i
      };
      
      // 根据列索引映射值
      Object.entries(columnIndexes).forEach(([fieldName, index]) => {
        if (index < values.length) {
          rowData[fieldName] = values[index];
        }
      });
      
      // 处理特定字段
      // 查找学生信息
      if (rowData.student_id_no) {
        const student = students.value.find(s => 
          s.student_id_no === rowData.student_id_no);
        
        if (student) {
          rowData.student_id = student.id;
          rowData.student_name = student.full_name;
        } else {
          console.warn(`未找到学号为 ${rowData.student_id_no} 的学生`);
          // 仍然保留这条记录，后端会处理学生ID验证
        }
      }
      
      // 查找量化项目信息
      if (rowData.item_id) {
        const itemId = Number(rowData.item_id);
        const item = quantItems.value.find(i => i.id === itemId);
        if (item) {
          rowData.item_name = item.name;
        } else {
          console.warn(`未找到ID为 ${rowData.item_id} 的量化项目`);
          // 仍然保留这条记录，后端会处理项目ID验证
        }
      }
      
      // 处理日期格式
      if (!rowData.record_date) {
        // 如果没有日期，使用当前日期
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        rowData.record_date = `${year}-${month}-${day}`;
      } else {
        // 确保日期格式正确
        try {
          // 尝试解析日期字符串
          const dateStr = String(rowData.record_date).trim();
          
          // 检查是否已经是YYYY-MM-DD格式
          if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
            // 格式已正确，验证是否有效
            const date = new Date(dateStr);
            if (isNaN(date.getTime())) {
              throw new Error('Invalid date');
            }
            rowData.record_date = dateStr;
          } else if (/^\d{4}\/\d{1,2}\/\d{1,2}$/.test(dateStr)) {
            // 处理YYYY/MM/DD格式
            const parts = dateStr.split('/');
            const year = parts[0];
            const month = String(parseInt(parts[1], 10)).padStart(2, '0');
            const day = String(parseInt(parts[2], 10)).padStart(2, '0');
            rowData.record_date = `${year}-${month}-${day}`;
          } else if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateStr)) {
            // 处理MM/DD/YYYY格式
            const parts = dateStr.split('/');
            const year = parts[2];
            const month = parts[0].padStart(2, '0');
            const day = parts[1].padStart(2, '0');
            rowData.record_date = `${year}-${month}-${day}`;
          } else {
            // 尝试使用Date对象解析
            const date = new Date(dateStr);
            if (!isNaN(date.getTime())) {
              const year = date.getFullYear();
              const month = String(date.getMonth() + 1).padStart(2, '0');
              const day = String(date.getDate()).padStart(2, '0');
              rowData.record_date = `${year}-${month}-${day}`;
            } else {
              // 如果无法解析，使用当前日期
              console.warn(`无效的日期格式 "${dateStr}"，使用当前日期`);
              const now = new Date();
              const year = now.getFullYear();
              const month = String(now.getMonth() + 1).padStart(2, '0');
              const day = String(now.getDate()).padStart(2, '0');
              rowData.record_date = `${year}-${month}-${day}`;
            }
          }
        } catch (error) {
          console.error('日期解析错误:', error);
          // 解析错误，使用当前日期
          const now = new Date();
          const year = now.getFullYear();
          const month = String(now.getMonth() + 1).padStart(2, '0');
          const day = String(now.getDate()).padStart(2, '0');
          rowData.record_date = `${year}-${month}-${day}`;
        }
      }
      
      parsedData.push(rowData);
      successRows++;
    }
    
    console.log(`解析完成: 成功 ${successRows} 行, 跳过 ${skippedRows} 行`);
    previewData.value = parsedData;
    
    if (parsedData.length === 0) {
      message.warning('没有解析到有效的记录数据');
    } else {
      message.success(`成功解析 ${parsedData.length} 条记录`);
    }
  } catch (error) {
    console.error('CSV解析错误:', error);
    message.error('文件解析失败，请检查文件格式');
  }
};

// 处理CSV行，正确处理引号包围的情况
const parseCSVLine = (line: string): string[] => {
  const result = [];
  let current = '';
  let inQuotes = false;
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    
    if (char === '"') {
      // 引号处理
      if (inQuotes && i < line.length - 1 && line[i + 1] === '"') {
        // 双引号转义为单引号
        current += '"';
        i++; // 跳过下一个引号
      } else {
        // 切换引号状态
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      // 当不在引号内时，逗号作为分隔符
      result.push(current);
      current = '';
    } else {
      // 普通字符
      current += char;
    }
  }
  
  // 添加最后一个字段
  result.push(current);
  return result;
};

// 重新加载文件
const reloadWithEncoding = () => {
  if (!fileData.value) return;
  
  console.log(`使用 ${selectedEncoding.value} 编码重新加载文件`);
  // 重新解析当前文件数据
  parseCSV(fileData.value);
  message.success(`使用 ${selectedEncoding.value} 编码重新加载文件`);
};

// 监听编码变化
watch(selectedEncoding, (newEncoding, oldEncoding) => {
  if (fileData.value && newEncoding !== oldEncoding) {
    console.log(`编码从 ${oldEncoding} 变更为 ${newEncoding}`);
    // 重新加载文件时先重置
    resetUpload();
    message.info(`编码已更改为 ${newEncoding}，请重新上传文件`);
  }
});

// 下载模板
const downloadTemplate = () => {
  const header = 'student_id_no,item_id,score,reason,record_date';
  
  // 添加不同格式的示例
  const samples = [
    '# 学号,量化项目ID,分数,原因,记录日期(YYYY-MM-DD格式)',
    '201901,1,85,表现优秀,2023-04-10',
    '201902,2,92.5,课堂活跃,2023-04-10',
    '201903,3,75,作业完成度不错,2023/04/10', 
    '201904,1,60,上课注意力不集中,04/10/2023',
    '201905,2,95,无,2023-04-10' // 原因可以为空
  ].join('\n');
  
  const content = `${header}\n${samples}`;
  
  // 添加UTF-8 BOM标记，确保Excel等应用能正确识别中文
  const BOM = '\uFEFF';
  const contentWithBOM = BOM + content;
  
  // 使用GB18030编码，这是中文Windows系统上Excel默认支持的编码
  let blob;
  try {
    // 尝试使用TextEncoder转换为GB18030编码
    if (window.TextEncoder) {
      // 由于大多数浏览器不支持GB18030，我们使用UTF-8并添加BOM
      const encoder = new TextEncoder();
      const uint8Array = encoder.encode(contentWithBOM);
      blob = new Blob([uint8Array], { type: 'text/csv;charset=utf-8' });
    } else {
      // 回退方案
      blob = new Blob([contentWithBOM], { type: 'text/csv;charset=utf-8' });
    }
  } catch (e) {
    console.error('编码转换失败:', e);
    // 回退方案
    blob = new Blob([contentWithBOM], { type: 'text/csv;charset=utf-8' });
  }
  
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = '量化记录导入模板.csv';
  link.click();
  
  // 解释日期格式支持
  message.info('导入支持多种日期格式，包括YYYY-MM-DD、YYYY/MM/DD和MM/DD/YYYY，最终会被转换为YYYY-MM-DD格式');
};

// 重置上传
const resetUpload = () => {
  fileName.value = '';
  fileData.value = null;
  previewData.value = [];
  if (uploadRef.value) {
    // @ts-ignore: uploadRef实例在运行时存在clear方法
    uploadRef.value.clear();
  }
};

// 导入记录
const handleImport = async () => {
  if (!previewData.value.length) {
    message.warning('没有可导入的记录数据');
    return;
  }
  
  importing.value = true;
  importResult.value = null;
  
  try {
    // 检查日期格式问题
    let fixedDatesCount = 0;
    if (hasDateFormatIssues.value) {
      // 自动修复日期问题
      fixedDatesCount = fixAllDates();
      
      // 告知用户已修复日期
      if (fixedDatesCount > 0) {
        message.success(`已自动修复 ${fixedDatesCount} 条记录的日期格式`);
      }
    }
    
    // 获取当前用户ID
    const currentUserId = userStore.user?.id;
    if (!currentUserId) {
      message.error('获取当前用户信息失败，请重新登录后再试');
      importing.value = false;
      return;
    }
    
    // 格式化数据，添加recorder_id字段
    const records = previewData.value.map(item => ({
      student_id: item.student_id,
      student_id_no: item.student_id_no,
      item_id: Number(item.item_id),
      score: Number(item.score),
      reason: item.reason || '',
      record_date: item.record_date,
      recorder_id: currentUserId // 添加记录者ID
    }));
    
    console.log('准备导入的记录数据:', records);
    
    // 调用API
    const response = await importRecords(records);
    
    // 安全处理响应数据
    // @ts-ignore: 忽略响应类型检查
    const resultData = response.data || {};
    
    // 显示结果
    importResult.value = {
      // @ts-ignore: 忽略响应类型检查
      success: !resultData.failed || resultData.failed.length === 0,
      // @ts-ignore: 忽略响应类型检查
      successCount: resultData.success || 0,
      // @ts-ignore: 忽略响应类型检查
      failedCount: resultData.failed?.length || 0,
      // @ts-ignore: 忽略响应类型检查
      failedRecords: resultData.failed?.map(item => ({
        ...item.data,
        error: item.reason,
        rowIndex: previewData.value.find(d => 
          d.student_id_no === item.data.student_id_no && 
          d.item_id === String(item.data.item_id))?.rowIndex
      }))
    };
    
    if (importResult.value.success) {
      message.success(`成功导入 ${importResult.value.successCount} 条记录`);
      emit('success');
    } else {
      message.warning(`导入完成，${importResult.value.successCount} 成功，${importResult.value.failedCount} 失败`);
    }
  } catch (error) {
    console.error('Failed to import records:', error);
    message.error('导入记录失败');
  } finally {
    importing.value = false;
  }
};

// 修复所有日期问题并返回修复数量
const fixAllDates = () => {
  if (!previewData.value.length) {
    return 0;
  }
  
  let fixedCount = 0;
  
  previewData.value = previewData.value.map(item => {
    // 只处理不符合YYYY-MM-DD格式的日期
    if (!/^\d{4}-\d{2}-\d{2}$/.test(String(item.record_date))) {
      fixedCount++;
      try {
        const dateStr = String(item.record_date).trim();
        
        if (/^\d{4}\/\d{1,2}\/\d{1,2}$/.test(dateStr)) {
          // 处理YYYY/MM/DD格式
          const parts = dateStr.split('/');
          const year = parts[0];
          const month = String(parseInt(parts[1], 10)).padStart(2, '0');
          const day = String(parseInt(parts[2], 10)).padStart(2, '0');
          item.record_date = `${year}-${month}-${day}`;
        } else if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateStr)) {
          // 处理MM/DD/YYYY格式
          const parts = dateStr.split('/');
          const year = parts[2];
          const month = parts[0].padStart(2, '0');
          const day = parts[1].padStart(2, '0');
          item.record_date = `${year}-${month}-${day}`;
        } else {
          // 尝试使用Date对象解析
          const date = new Date(dateStr);
          if (!isNaN(date.getTime())) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            item.record_date = `${year}-${month}-${day}`;
          } else {
            // 如果无法解析，使用当前日期
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            item.record_date = `${year}-${month}-${day}`;
          }
        }
      } catch (error) {
        // 解析错误，使用当前日期
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        item.record_date = `${year}-${month}-${day}`;
      }
    }
    return item;
  });
  
  return fixedCount;
};

// 检查是否有日期格式问题
const hasDateFormatIssues = computed(() => {
  if (!previewData.value.length) return false;
  return previewData.value.some(item => 
    !/^\d{4}-\d{2}-\d{2}$/.test(String(item.record_date))
  );
});

// 获取有问题的行数
const invalidDateRowCount = computed(() => {
  if (!previewData.value.length) return 0;
  return previewData.value.filter(item => 
    !/^\d{4}-\d{2}-\d{2}$/.test(String(item.record_date))
  ).length;
});

// 在模板中显示日期问题警告
const dateWarningText = computed(() => {
  const count = invalidDateRowCount.value;
  if (count === 0) return '';
  
  return `检测到 ${count} 条记录的日期格式有问题，请在导入前修复或使用"修复日期格式"按钮自动转换。`;
});
</script>

<style scoped>
.text-primary {
  color: var(--primary-color);
  font-weight: 500;
}
</style> 