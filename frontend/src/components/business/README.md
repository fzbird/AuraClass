# AuraClass 业务组件库

本文档提供 AuraClass 前端业务组件的使用说明和示例。这些组件基于通用组件库和 Naive UI 组件库开发，专为 AuraClass 系统的业务场景定制。

## 组件引入方式

```vue
<script setup lang="ts">
// 方式一：单独引入
import { StudentCard } from '@/components/business';

// 方式二：按需引入
import StudentCard from '@/components/business/StudentCard.vue';
</script>
```

## 组件列表

### StudentCard - 学生卡片组件

用于展示学生信息和量化分数的卡片组件。

**基础用法**:

```vue
<StudentCard
  :student="student"
  :showScore="true"
  :showStats="true"
  @action="handleStudentAction"
/>
```

**属性**:
- `student`: 学生信息对象（必填）
  - `id`: 学生ID
  - `name`: 姓名
  - `studentId`: 学号
  - `className`: 班级名称
  - `role`: 角色标识
  - `avatar`: 头像URL
  - `score`: 量化分数
  - `stats`: 统计信息
    - `positive`: 加分数
    - `negative`: 减分数
    - `records`: 记录数
  - `tags`: 标签数组
- `showHeader`: 是否显示头部信息，默认 `true`
- `showScore`: 是否显示分数，默认 `true`
- `showStats`: 是否显示统计信息，默认 `true`
- `showTags`: 是否显示标签，默认 `true`
- `showActions`: 是否显示操作按钮，默认 `true`
- `actions`: 要显示的操作按钮配置
  - `view`: 查看按钮，默认 `true`
  - `edit`: 编辑按钮，默认 `false`
  - `records`: 量化记录按钮，默认 `false`
  - `delete`: 删除按钮，默认 `false`
- `bordered`: 是否显示边框，默认 `true`
- `hoverable`: 是否悬停效果，默认 `true`
- `size`: 卡片大小，可选值: 'small', 'medium', 'large'，默认 'medium'
- `style`: 自定义样式
- `className`: 自定义类名

**事件**:
- `action`: 操作按钮点击事件，返回 `{ action, student }` 对象
  - `action`: 操作类型，如 'view', 'edit', 'records', 'delete'
  - `student`: 学生信息对象

**插槽**:
- 默认插槽: 在卡片内容区域添加自定义内容
- `footer`: 自定义底部内容

### QuantItemCard - 量化项目卡片组件

用于展示量化项目信息的卡片组件。

**基础用法**:

```vue
<QuantItemCard
  :quantItem="quantItem"
  :showDescription="true"
  @action="handleQuantItemAction"
/>
```

**属性**:
- `quantItem`: 量化项目信息对象（必填）
  - `id`: 项目ID
  - `name`: 项目名称
  - `score`: 分数值（正数为加分项，负数为减分项）
  - `type`: 类型，可选值: 'positive'(加分项), 'negative'(减分项), 'neutral'(中性项)
  - `description`: 描述文本
  - `category`: 分类信息
    - `id`: 分类ID
    - `name`: 分类名称
  - `creator`: 创建者信息
    - `id`: 创建者ID
    - `name`: 创建者姓名
  - `createdAt`: 创建时间
  - `tags`: 标签数组
- `showHeader`: 是否显示头部，默认 `true`
- `showType`: 是否显示类型标签，默认 `true`
- `showDescription`: 是否显示描述，默认 `true`
- `showCategory`: 是否显示分类，默认 `true`
- `showCreator`: 是否显示创建者，默认 `false`
- `showDate`: 是否显示创建日期，默认 `false`
- `showTags`: 是否显示标签，默认 `true`
- `showActions`: 是否显示操作按钮，默认 `true`
- `actions`: 要显示的操作按钮配置
  - `view`: 查看按钮，默认 `true`
  - `edit`: 编辑按钮，默认 `false`
  - `record`: 记录按钮，默认 `true`
  - `delete`: 删除按钮，默认 `false`
- `bordered`: 是否显示边框，默认 `true`
- `hoverable`: 是否悬停效果，默认 `true`
- `size`: 卡片大小，可选值: 'small', 'medium', 'large'，默认 'medium'
- `style`: 自定义样式
- `className`: 自定义类名

**事件**:
- `action`: 操作按钮点击事件，返回 `{ action, quantItem }` 对象
  - `action`: 操作类型，如 'view', 'edit', 'record', 'delete'
  - `quantItem`: 量化项目信息对象

**插槽**:
- 默认插槽: 在卡片内容区域添加自定义内容
- `footer`: 自定义底部内容

### ClassCard - 班级卡片组件

用于展示班级信息的卡片组件。

**基础用法**:

```vue
<ClassCard
  :classInfo="classInfo"
  :showStats="true"
  @action="handleClassAction"
/>
```

**属性**:
- `classInfo`: 班级信息对象（必填）
  - `id`: 班级ID
  - `name`: 班级名称
  - `gradeLevel`: 年级
  - `teacherName`: 班主任姓名
  - `teacherId`: 班主任ID
  - `avatar`: 班级头像
  - `isActive`: 是否活跃
  - `stats`: 统计信息
    - `studentCount`: 学生数
    - `averageScore`: 平均分
    - `recordCount`: 记录数
  - `tags`: 标签数组
- `showHeader`: 是否显示头部，默认 `true`
- `showStats`: 是否显示统计信息，默认 `true`
- `showTags`: 是否显示标签，默认 `true`
- `showActions`: 是否显示操作按钮，默认 `true`
- `actions`: 要显示的操作按钮配置
  - `view`: 查看按钮，默认 `true`
  - `edit`: 编辑按钮，默认 `false`
  - `students`: 学生管理按钮，默认 `false`
  - `delete`: 删除按钮，默认 `false`
- `bordered`: 是否显示边框，默认 `true`
- `hoverable`: 是否悬停效果，默认 `true`
- `size`: 卡片大小，可选值: 'small', 'medium', 'large'，默认 'medium'

**事件**:
- `action`: 操作按钮点击事件，返回 `{ action, classInfo }` 对象
  - `action`: 操作类型，如 'view', 'edit', 'students', 'delete'
  - `classInfo`: 班级信息对象

**插槽**:
- 默认插槽: 在卡片内容区域添加自定义内容
- `actions`: 自定义操作按钮

### TeacherCard - 教师卡片组件

用于展示教师信息的卡片组件。

**基础用法**:

```vue
<TeacherCard
  :teacher="teacher"
  :showContact="true"
  :showClasses="true"
  @action="handleTeacherAction"
  @class-action="handleClassAction"
/>
```

**属性**:
- `teacher`: 教师信息对象（必填）
  - `id`: 教师ID
  - `name`: 姓名
  - `teacherId`: 工号
  - `subject`: 任教科目
  - `role`: 角色
  - `email`: 邮箱
  - `phone`: 电话
  - `avatar`: 头像URL
  - `stats`: 统计信息
    - `classCount`: 班级数
    - `studentCount`: 学生数
    - `recordCount`: 记录数
  - `tags`: 标签数组
  - `classes`: 班级数组
- `showHeader`: 是否显示头部，默认 `true`
- `showContact`: 是否显示联系信息，默认 `true`
- `showStats`: 是否显示统计信息，默认 `true`
- `showTags`: 是否显示标签，默认 `true`
- `showClasses`: 是否显示班级信息，默认 `true`
- `showActions`: 是否显示操作按钮，默认 `true`
- `actions`: 要显示的操作按钮配置
  - `view`: 查看按钮，默认 `true`
  - `edit`: 编辑按钮，默认 `false`
  - `classes`: 班级管理按钮，默认 `false`
  - `message`: 留言按钮，默认 `false`
  - `delete`: 删除按钮，默认 `false`
- `bordered`: 是否显示边框，默认 `true`
- `hoverable`: 是否悬停效果，默认 `true`
- `size`: 卡片大小，可选值: 'small', 'medium', 'large'，默认 'medium'

**事件**:
- `action`: 操作按钮点击事件，返回 `{ action, teacher }` 对象
  - `action`: 操作类型，如 'view', 'edit', 'classes', 'message', 'delete'
  - `teacher`: 教师信息对象
- `class-action`: 班级点击事件，返回 `{ action, classItem, teacher }` 对象
  - `action`: 操作类型，目前只有 'view'
  - `classItem`: 班级信息对象
  - `teacher`: 教师信息对象

**插槽**:
- 默认插槽: 在卡片内容区域添加自定义内容
- `actions`: 自定义操作按钮

## 使用示例

### 学生管理页面示例

```vue
<template>
  <div class="student-management">
    <div class="search-bar">
      <app-search
        v-model:value="searchText"
        placeholder="搜索学生..."
        @search="searchStudents"
      />
      <app-button type="primary" @click="addStudent">添加学生</app-button>
    </div>
    
    <div class="student-list">
      <student-card
        v-for="student in students"
        :key="student.id"
        :student="student"
        :actions="{
          view: true,
          edit: true,
          records: true,
          delete: hasDeletePermission
        }"
        @action="handleStudentAction"
      />
    </div>
    
    <app-pagination
      v-if="totalStudents > 0"
      :page="page"
      :pageSize="pageSize"
      :itemCount="totalStudents"
      @update:page="onPageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { AppSearch, AppButton, AppPagination } from '@/components/common';
import { StudentCard } from '@/components/business';
import { usePermission } from '@/composables/usePermission';

const { hasPermission } = usePermission();
const hasDeletePermission = hasPermission('student:delete');

const searchText = ref('');
const students = ref([]);
const page = ref(1);
const pageSize = ref(10);
const totalStudents = ref(0);

onMounted(() => {
  fetchStudents();
});

const fetchStudents = async () => {
  // 实际项目中应该调用API
  students.value = [
    {
      id: 1,
      name: '张三',
      studentId: '20220101',
      className: '高一(1)班',
      score: 95,
      stats: {
        positive: 10,
        negative: 2,
        records: 12
      },
      tags: [
        { id: 1, name: '班长', type: 'success' },
        { id: 2, name: '数学优秀', type: 'info' }
      ]
    },
    // 更多学生数据...
  ];
  totalStudents.value = 100; // 模拟总数
};

const searchStudents = () => {
  page.value = 1;
  fetchStudents();
};

const addStudent = () => {
  // 实现添加学生逻辑
};

const handleStudentAction = ({ action, student }) => {
  switch (action) {
    case 'view':
      // 查看学生详情
      break;
    case 'edit':
      // 编辑学生信息
      break;
    case 'records':
      // 查看量化记录
      break;
    case 'delete':
      // 删除学生
      break;
  }
};

const onPageChange = (newPage) => {
  page.value = newPage;
  fetchStudents();
};
</script>

<style scoped>
.student-management {
  padding: 20px;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.student-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
</style>
```

### 量化记录页面示例

```vue
<template>
  <div class="quant-records">
    <div class="filter-bar">
      <app-select
        v-model:value="selectedType"
        placeholder="选择类型"
        :options="typeOptions"
        clearable
      />
      <app-button @click="applyFilters">筛选</app-button>
    </div>
    
    <div class="quant-items">
      <quant-item-card
        v-for="item in quantItems"
        :key="item.id"
        :quantItem="item"
        :showCreator="true"
        :showDate="true"
        :actions="{
          view: true,
          edit: canEdit,
          record: true,
          delete: canDelete
        }"
        @action="handleQuantItemAction"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { AppSelect, AppButton } from '@/components/common';
import { QuantItemCard } from '@/components/business';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const canEdit = computed(() => userStore.hasRole('teacher'));
const canDelete = computed(() => userStore.hasRole('admin'));

const selectedType = ref(null);
const typeOptions = [
  { label: '加分项', value: 'positive' },
  { label: '减分项', value: 'negative' },
  { label: '中性项', value: 'neutral' }
];

const quantItems = ref([
  {
    id: 1,
    name: '课堂积极发言',
    score: 2,
    type: 'positive',
    description: '课堂上主动回答问题或参与讨论',
    category: { id: 1, name: '课堂表现' },
    creator: { id: 1, name: '王老师' },
    createdAt: '2023-09-15T08:30:00Z',
    tags: [{ id: 1, name: '课堂', type: 'info' }]
  },
  {
    id: 2,
    name: '无故旷课',
    score: -5,
    type: 'negative',
    description: '无正当理由缺席课程',
    category: { id: 2, name: '纪律表现' },
    creator: { id: 2, name: '李老师' },
    createdAt: '2023-09-10T10:15:00Z',
    tags: [{ id: 2, name: '纪律', type: 'error' }]
  }
  // 更多量化项目数据...
]);

const applyFilters = () => {
  // 实际项目中应该调用API进行筛选
  if (selectedType.value) {
    // 模拟筛选
    quantItems.value = quantItems.value.filter(
      item => item.type === selectedType.value
    );
  } else {
    // 重置筛选，加载所有数据
    loadAllItems();
  }
};

const loadAllItems = () => {
  // 实际项目中加载所有项目的逻辑
};

const handleQuantItemAction = ({ action, quantItem }) => {
  switch (action) {
    case 'view':
      // 查看量化项详情
      break;
    case 'edit':
      // 编辑量化项
      break;
    case 'record':
      // 记录该量化项
      break;
    case 'delete':
      // 删除量化项
      break;
  }
};
</script>

<style scoped>
.quant-records {
  padding: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.quant-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
</style>
```

### 班级管理页面示例

```vue
<template>
  <div class="class-management">
    <div class="header">
      <h2 class="title">班级管理</h2>
      <app-button type="primary" @click="addClass">添加班级</app-button>
    </div>
    
    <div class="class-list">
      <class-card
        v-for="classItem in classes"
        :key="classItem.id"
        :classInfo="classItem"
        :actions="{
          view: true,
          edit: true,
          students: true,
          delete: isAdmin
        }"
        @action="handleClassAction"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { AppButton } from '@/components/common';
import { ClassCard } from '@/components/business';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const isAdmin = computed(() => userStore.hasRole('admin'));

const classes = ref([
  {
    id: 1,
    name: '高一(1)班',
    gradeLevel: '2023',
    teacherName: '张老师',
    teacherId: 101,
    isActive: true,
    stats: {
      studentCount: 45,
      averageScore: 89.5,
      recordCount: 156
    },
    tags: [
      { id: 1, name: '示范班', type: 'success' },
      { id: 2, name: '优秀班级', type: 'info' }
    ]
  },
  // 更多班级数据...
]);

const addClass = () => {
  // 实现添加班级逻辑
};

const handleClassAction = ({ action, classInfo }) => {
  switch (action) {
    case 'view':
      // 查看班级详情
      break;
    case 'edit':
      // 编辑班级信息
      break;
    case 'students':
      // 管理班级学生
      break;
    case 'delete':
      // 删除班级
      break;
  }
};
</script>

<style scoped>
.class-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title {
  font-size: 22px;
  margin: 0;
}

.class-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}
</style>
```

### 教师管理页面示例

```vue
<template>
  <div class="teacher-management">
    <div class="header">
      <h2 class="title">教师管理</h2>
      <app-button type="primary" @click="addTeacher">添加教师</app-button>
    </div>
    
    <div class="teacher-list">
      <teacher-card
        v-for="teacher in teachers"
        :key="teacher.id"
        :teacher="teacher"
        :actions="{
          view: true,
          edit: true,
          classes: true,
          message: true,
          delete: isAdmin
        }"
        @action="handleTeacherAction"
        @class-action="handleClassAction"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { AppButton } from '@/components/common';
import { TeacherCard } from '@/components/business';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const isAdmin = computed(() => userStore.hasRole('admin'));

const teachers = ref([
  {
    id: 1,
    name: '王老师',
    teacherId: 'T2023001',
    subject: '数学',
    role: '班主任',
    email: 'wang@example.com',
    phone: '13800138000',
    stats: {
      classCount: 2,
      studentCount: 90,
      recordCount: 128
    },
    tags: [
      { id: 1, name: '骨干教师', type: 'success' },
      { id: 2, name: '数学教研组', type: 'info' }
    ],
    classes: [
      { id: 1, name: '高一(1)班' },
      { id: 2, name: '高一(2)班' }
    ]
  },
  // 更多教师数据...
]);

const addTeacher = () => {
  // 实现添加教师逻辑
};

const handleTeacherAction = ({ action, teacher }) => {
  switch (action) {
    case 'view':
      // 查看教师详情
      break;
    case 'edit':
      // 编辑教师信息
      break;
    case 'classes':
      // 管理教师班级
      break;
    case 'message':
      // 发送消息
      break;
    case 'delete':
      // 删除教师
      break;
  }
};

const handleClassAction = ({ action, classItem, teacher }) => {
  // 处理班级相关操作
  if (action === 'view') {
    // 查看班级详情
    console.log(`查看${teacher.name}的班级:`, classItem.name);
  }
};
</script>

<style scoped>
.teacher-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title {
  font-size: 22px;
  margin: 0;
}

.teacher-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}
</style>
```

## 注意事项

1. 所有业务组件都提供了灵活的配置选项，可通过属性控制显示内容和行为
2. 组件设计遵循一致的样式和交互模式，确保整个应用的用户体验统一
3. 建议根据具体业务场景适当配置组件选项，避免信息过载
4. 组件支持通过插槽扩展内容，可以根据需要添加自定义内容
5. 事件处理遵循统一的格式，方便在父组件中统一处理各种操作 