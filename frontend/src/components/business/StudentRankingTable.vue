<template>
  <div>
    <div class="text-gray-500 mb-4">{{ description }}</div>
    
    <n-data-table
      :columns="columns"
      :data="data"
      :loading="loading"
      :pagination="pagination"
      :bordered="false"
      striped
    />
  </div>
</template>

<script setup lang="ts">
import { h, computed } from 'vue';
import { NDataTable, NTag, NButton, NAvatar } from 'naive-ui';
import { useRouter } from 'vue-router';

// 定义学生排名项类型
interface StudentRankingItem {
  id?: number;
  student_id?: number;
  student_id_no?: string;
  full_name?: string;
  name?: string;
  class_name?: string;
  total_score?: number;
  positive_score?: number;
  negative_score?: number;
  record_count?: number;
  total_records?: number;
  avatar?: string;
  rank?: number;
  [key: string]: any;
}

const router = useRouter();

const props = defineProps({
  data: {
    type: Array as () => StudentRankingItem[],
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  scoreField: {
    type: String,
    default: 'total_score'
  },
  scoreLabel: {
    type: String,
    default: '分数'
  },
  description: {
    type: String,
    default: ''
  }
});

const pagination = {
  pageSize: 10
};

const getRankTagType = (rank: number): string => {
  if (rank === 1) return 'error';
  if (rank === 2) return 'warning';
  if (rank === 3) return 'info';
  return 'default';
};

const columns = computed(() => [
  {
    title: '排名',
    key: 'rank',
    width: 80,
    render: (row: StudentRankingItem) => {
      return h(
        NTag,
        {
          type: getRankTagType(row.rank || 0),
          bordered: false,
          style: {
            padding: '2px 10px'
          }
        },
        { default: () => row.rank }
      );
    }
  },
  {
    title: '学生',
    key: 'student',
    render: (row: StudentRankingItem) => {
      const studentName = row.full_name || row.name || '未知学生';
      
      return h(
        'div',
        {
          class: 'flex items-center'
        },
        [
          h(
            NAvatar,
            {
              size: 'small',
              round: true,
              src: row.avatar || null,
              style: {
                marginRight: '8px',
                background: row.avatar ? 'transparent' : getAvatarColor(studentName)
              }
            },
            {
              default: () => row.avatar ? null : studentName.substring(0, 1)
            }
          ),
          h(
            'span',
            {
              class: 'ml-2'
            },
            studentName
          )
        ]
      );
    }
  },
  {
    title: '学号',
    key: 'student_id_no',
    width: 120
  },
  {
    title: '班级',
    key: 'class_name',
    width: 150
  },
  {
    title: props.scoreField === 'record_count' ? '总分' : props.scoreLabel,
    key: props.scoreField === 'record_count' ? 'total_score' : props.scoreField,
    width: 100,
    render: (row: StudentRankingItem) => {
      const fieldKey = props.scoreField === 'record_count' ? 'total_score' : props.scoreField;
      const value = row[fieldKey];
      const isNegative = fieldKey === 'negative_score' && (value < 0 || Math.abs(value) > 0);
      const color = isNegative ? 'text-red-500' : '';
      return h(
        'span',
        {
          class: color
        },
        typeof value === 'number' ? value.toFixed(1) : (value || '0.0')
      );
    }
  },
  {
    title: '记录数',
    key: 'record_count',
    width: 100,
    render: (row: StudentRankingItem) => {
      const count = row.record_count !== undefined ? row.record_count : (row.total_records || 0);
      return h('span', {}, count);
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row: StudentRankingItem) => {
      console.log('学生数据:', row); // 调试输出
      // 优先使用student_id，如果没有则尝试使用id
      const studentId = row.student_id !== undefined ? row.student_id : row.id;
      
      // 添加调试日志，记录传递的ID和完整row数据
      console.log('查看学生详情 - 完整数据:', JSON.stringify(row));
      console.log('查看学生详情 - 使用ID:', studentId, '原始ID字段:', row.student_id, 'ID字段:', row.id);
      
      return h(
        NButton,
        {
          size: 'small',
          onClick: () => {
            console.log('点击查看学生详情 - 跳转路径:', `/app/students/${studentId}`);
            
            // 如果student_id存在且与id不同，记录这个差异
            if (row.student_id !== undefined && row.id !== undefined && row.student_id !== row.id) {
              console.warn('警告: student_id与id不一致:', 
                'student_id =', row.student_id, 
                'id =', row.id, 
                '使用student_id =', studentId);
            }
            
            // 确保使用正确的ID
            const finalId = row.student_id || row.id;
            console.log('最终使用的学生ID:', finalId);
            
            // 增加时间戳参数确保路由变化被检测到，强制刷新
            router.push({
              path: `/app/students/${finalId}`,
              query: { _t: Date.now() }  // 添加时间戳参数
            });
          }
        },
        { default: () => '查看详情' }
      );
    }
  }
]);

const getAvatarColor = (name: string): string => {
  const colors = [
    '#3366FF', '#52C41A', '#FAAD14', '#F5222D', '#722ED1',
    '#13C2C2', '#1890FF', '#EB2F96', '#FA8C16', '#A0D911'
  ];
  
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  return colors[Math.abs(hash) % colors.length];
};
</script>
