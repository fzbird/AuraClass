# AuraClass 通用组件库

本文档提供 AuraClass 前端通用组件的使用说明和示例。这些组件基于 Naive UI 组件库进行二次封装，提供了统一的界面风格和简化的 API。

## 组件引入方式

```vue
<script setup lang="ts">
// 方式一：单独引入
import { AppButton } from '@/components/common';

// 方式二：按需引入
import AppButton from '@/components/common/AppButton.vue';
</script>
```

## 组件列表

### AppAlert - 提示组件

封装 Naive UI 的 NAlert 组件，用于显示提示信息。

**基础用法**:

```vue
<AppAlert
  title="成功提示"
  type="success"
  :closable="true"
>
  操作已成功完成
</AppAlert>
```

**属性**:
- `type`: 提示类型，可选值: 'default', 'info', 'success', 'warning', 'error'
- `title`: 提示标题
- `closable`: 是否可关闭
- `showIcon`: 是否显示图标
- `bordered`: 是否显示边框

### AppAvatar - 头像组件

封装 Naive UI 的 NAvatar 组件，用于显示用户头像。

**基础用法**:

```vue
<AppAvatar 
  src="https://example.com/avatar.jpg" 
  size="medium" 
  round 
/>
```

**属性**:
- `src`: 头像图片地址
- `size`: 尺寸，可选值: 'small', 'medium', 'large' 或数字
- `round`: 是否显示为圆形
- `text`: 当没有图片时显示的文字
- `color`: 背景颜色

### AppBadge - 徽章组件

封装 Naive UI 的 NBadge 组件，用于显示徽章。

**基础用法**:

```vue
<AppBadge :value="5" type="error">
  <AppButton>消息</AppButton>
</AppBadge>
```

**属性**:
- `value`: 徽章数值
- `max`: 最大显示数值，超过后显示 {max}+
- `dot`: 是否只显示小圆点
- `type`: 徽章类型，可选值: 'default', 'error', 'info', 'success', 'warning'
- `show`: 是否显示徽章
- `showZero`: 当值为 0 时是否显示徽章
- `processing`: 是否显示动画效果
- `color`: 自定义颜色

### AppButton - 按钮组件

封装 Naive UI 的 NButton 组件，提供统一样式的按钮。

**基础用法**:

```vue
<AppButton type="primary" @click="handleClick">
  点击按钮
</AppButton>
```

**属性**:
- `type`: 按钮类型，可选值: 'default', 'primary', 'info', 'success', 'warning', 'error'
- `size`: 按钮大小，可选值: 'tiny', 'small', 'medium', 'large'
- `ghost`: 是否为透明背景
- `round`: 是否为圆角按钮
- `circle`: 是否为圆形按钮
- `disabled`: 是否禁用
- `loading`: 是否显示加载状态
- `dashed`: 是否显示虚线边框

### AppCard - 卡片组件

封装 Naive UI 的 NCard 组件，用于内容分组展示。

**基础用法**:

```vue
<AppCard title="卡片标题" :bordered="true">
  <template #header-extra>
    <AppButton size="small">更多</AppButton>
  </template>
  卡片内容区域
</AppCard>
```

**属性**:
- `title`: 卡片标题
- `bordered`: 是否显示边框
- `size`: 卡片大小，可选值: 'small', 'medium', 'large'
- `hoverable`: 是否在悬停时显示阴影
- `segmented`: 分段设置

### AppCopy - 复制组件

提供文本复制功能的组件。

**基础用法**:

```vue
<AppCopy text="要复制的文本">
  点击复制
</AppCopy>
```

**属性**:
- `text`: 要复制的文本
- `buttonText`: 按钮文本
- `successMessage`: 复制成功提示
- `errorMessage`: 复制失败提示
- `hideText`: 是否隐藏按钮文本
- `buttonType`: 按钮类型

**事件**:
- `copy`: 复制动作触发时
- `success`: 复制成功时
- `error`: 复制失败时

### AppDataList - 数据列表组件

基于 Naive UI 组件实现的数据列表，支持分页和加载状态。

**基础用法**:

```vue
<AppDataList
  :data="listData"
  :loading="loading"
  :pagination="true"
  :page="page"
  :pageSize="pageSize"
  :total="total"
  emptyText="暂无数据"
  @pageChange="handlePageChange"
  @pageSizeChange="handlePageSizeChange"
>
  <template #item="{ item }">
    {{ item.name }}
  </template>
</AppDataList>
```

**属性**:
- `data`: 列表数据数组
- `loading`: 是否处于加载状态
- `title`: 列表标题
- `bordered`: 是否显示边框
- `pagination`: 是否显示分页
- `page`: 当前页码
- `pageSize`: 每页条数
- `total`: 数据总数
- `emptyText`: 空数据提示文本

**事件**:
- `pageChange`: 页码变化时触发
- `pageSizeChange`: 每页条数变化时触发
- `itemClick`: 点击列表项时触发

### AppDivider - 分割线组件

封装 Naive UI 的 NDivider 组件，用于内容分割。

**基础用法**:

```vue
<AppDivider titlePlacement="center">分割线标题</AppDivider>
```

**属性**:
- `titlePlacement`: 标题位置，可选值: 'left', 'right', 'center'
- `dashed`: 是否显示为虚线
- `vertical`: 是否为垂直分割线
- `color`: 分割线颜色
- `thickness`: 分割线粗细

### AppIcon - 图标组件

封装 Naive UI 的 NIcon 组件，提供图标展示功能。

**基础用法**:

```vue
<AppIcon :icon="BookOutline" size="24" color="#1890ff" />
```

**属性**:
- `icon`: 图标组件
- `size`: 图标大小
- `color`: 图标颜色
- `depth`: 图标深度

### AppInput - 输入框组件

封装 Naive UI 的 NInput 组件，提供输入框功能。

**基础用法**:

```vue
<AppInput
  v-model:value="inputValue"
  placeholder="请输入内容"
  clearable
/>
```

**属性**:
- `value`: 输入值
- `type`: 输入框类型，如 'text', 'password', 'textarea'
- `placeholder`: 占位提示
- `disabled`: 是否禁用
- `clearable`: 是否可清空
- `round`: 是否为圆角输入框
- `maxlength`: 最大输入长度

**事件**:
- `update:value`: 输入值更新
- `focus`: 获得焦点
- `blur`: 失去焦点

### AppModal - 模态框组件

封装 Naive UI 的 NModal 组件，提供弹窗功能。

**基础用法**:

```vue
<AppModal
  title="标题"
  :show="showModal"
  @update:show="showModal = $event"
  @confirm="handleConfirm"
>
  模态框内容
</AppModal>
```

**属性**:
- `show`: 是否显示
- `title`: 标题
- `width`: 宽度
- `preset`: 预设样式，可选值: 'dialog', 'card'
- `closable`: 是否显示关闭按钮
- `maskClosable`: 点击遮罩是否关闭
- `positiveText`: 确认按钮文本
- `negativeText`: 取消按钮文本

**事件**:
- `update:show`: 显示状态变化
- `confirm`: 点击确认按钮
- `cancel`: 点击取消按钮

### AppPagination - 分页组件

封装 Naive UI 的 NPagination 组件，提供分页功能。

**基础用法**:

```vue
<AppPagination
  :page="currentPage"
  :pageSize="pageSize"
  :pageCount="pageCount"
  :itemCount="total"
  @update:page="handlePageChange"
  @update:pageSize="handlePageSizeChange"
/>
```

**属性**:
- `page`: 当前页码
- `pageSize`: 每页条数
- `pageCount`: 总页数
- `itemCount`: 总条目数
- `pageSizes`: 可选的每页条数
- `showSizePicker`: 是否显示每页条数选择

**事件**:
- `update:page`: 页码变化
- `update:pageSize`: 每页条数变化

### AppSearch - 搜索组件

封装 Naive UI 的 NInput 组件，专用于搜索功能。

**基础用法**:

```vue
<AppSearch
  v-model:value="searchValue"
  placeholder="搜索..."
  @search="handleSearch"
/>
```

**属性**:
- `value`: 搜索值
- `placeholder`: 占位提示
- `loading`: 是否处于加载状态
- `clearable`: 是否可清空

**事件**:
- `update:value`: 输入值更新
- `search`: 搜索触发，点击搜索按钮或按回车键

### AppSelect - 选择器组件

封装 Naive UI 的 NSelect 组件，提供下拉选择功能。

**基础用法**:

```vue
<AppSelect
  v-model:value="selectedValue"
  :options="options"
  placeholder="请选择"
  clearable
/>
```

**属性**:
- `value`: 选中值
- `options`: 选项数组，每项含 label 和 value
- `placeholder`: 占位提示
- `disabled`: 是否禁用
- `clearable`: 是否可清空
- `multiple`: 是否多选
- `filterable`: 是否可搜索

**事件**:
- `update:value`: 选中值更新
- `change`: 选中值变化

### AppSpinner - 加载组件

封装 Naive UI 的 NSpin 组件，提供加载动画。

**基础用法**:

```vue
<AppSpinner :show="loading" size="medium">
  <div>加载中的内容</div>
</AppSpinner>
```

**属性**:
- `show`: 是否显示加载动画
- `size`: 尺寸，可选值: 'small', 'medium', 'large'
- `description`: 加载描述文本
- `stroke`: 加载图标的颜色

### AppTable - 表格组件

封装 Naive UI 的 NDataTable 组件，提供数据表格功能。

**基础用法**:

```vue
<AppTable
  :columns="columns"
  :data="tableData"
  :pagination="true"
  :page="page"
  :pageSize="pageSize"
  :itemCount="total"
  :loading="loading"
  @update:page="handlePageChange"
  @update:pageSize="handlePageSizeChange"
/>
```

**属性**:
- `columns`: 表格列定义
- `data`: 表格数据
- `pagination`: 是否显示分页
- `page`: 当前页码
- `pageSize`: 每页条数
- `itemCount`: 总条目数
- `loading`: 加载状态
- `bordered`: 是否显示边框
- `striped`: 是否显示斑马纹

**事件**:
- `update:page`: 页码变化
- `update:pageSize`: 每页条数变化
- `update:sorter`: 排序变化
- `update:filters`: 筛选条件变化

### AppTabs - 标签页组件

封装 Naive UI 的 NTabs 组件，提供标签页切换功能。

**基础用法**:

```vue
<AppTabs v-model:value="activeTab" type="line">
  <AppTabPane name="tab1" tab="标签1">标签1内容</AppTabPane>
  <AppTabPane name="tab2" tab="标签2">标签2内容</AppTabPane>
</AppTabs>
```

**属性**:
- `value`: 当前激活的标签名
- `type`: 标签类型，可选值: 'bar', 'line', 'card'
- `animated`: 是否使用动画
- `size`: 尺寸，可选值: 'small', 'medium', 'large'
- `tabStyle`: 标签样式

**事件**:
- `update:value`: 激活标签变化

### AppTimeLabel - 时间标签组件

提供友好的时间显示功能，支持相对时间和绝对时间显示。

**基础用法**:

```vue
<AppTimeLabel :time="new Date()" format="relative" />
```

**属性**:
- `time`: 时间值，可以是 Date 对象、时间戳或日期字符串
- `format`: 时间格式，可选值: 'relative' (相对时间), 'absolute' (绝对时间), 'auto' (自动选择)
- `hoverable`: 是否可悬停切换格式
- `options`: 配置选项，如地区、是否显示秒等

### AppUpload - 上传组件

封装 Naive UI 的 NUpload 组件，提供文件上传功能。

**基础用法**:

```vue
<AppUpload
  action="/api/upload"
  :headers="headers"
  :data="uploadData"
  list-type="image-card"
  :file-list="fileList"
  @update:fileList="handleFileListChange"
  @finish="handleUploadFinish"
>
  点击上传
</AppUpload>
```

**属性**:
- `action`: 上传 URL
- `headers`: 请求头
- `data`: 附带数据
- `fileList`: 文件列表
- `listType`: 列表类型，可选值: 'text', 'image', 'image-card'
- `multiple`: 是否支持多选
- `accept`: 接受的文件类型
- `max-size`: 文件大小限制

**事件**:
- `update:fileList`: 文件列表更新
- `finish`: 上传完成
- `error`: 上传错误
- `before-upload`: 上传前钩子
- `remove`: 文件移除

## 使用示例

### 表单示例

```vue
<template>
  <AppCard title="用户信息表单">
    <div class="form-row">
      <AppInput
        v-model:value="form.name"
        placeholder="请输入姓名"
        label="姓名"
        required
      />
    </div>
    
    <div class="form-row">
      <AppSelect
        v-model:value="form.gender"
        :options="genderOptions"
        placeholder="请选择性别"
        label="性别"
      />
    </div>
    
    <div class="form-row">
      <AppUpload
        list-type="image-card"
        :file-list="form.avatarList"
        @update:fileList="form.avatarList = $event"
      />
    </div>
    
    <div class="form-actions">
      <AppButton type="primary" @click="handleSubmit">提交</AppButton>
      <AppButton @click="handleReset">重置</AppButton>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { 
  AppCard, 
  AppInput, 
  AppSelect, 
  AppUpload, 
  AppButton 
} from '@/components/common';

const form = reactive({
  name: '',
  gender: null,
  avatarList: []
});

const genderOptions = [
  { label: '男', value: 'male' },
  { label: '女', value: 'female' }
];

const handleSubmit = () => {
  // 提交表单逻辑
};

const handleReset = () => {
  form.name = '';
  form.gender = null;
  form.avatarList = [];
};
</script>

<style scoped>
.form-row {
  margin-bottom: 16px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
</style>
```

### 数据列表示例

```vue
<template>
  <AppCard title="用户列表">
    <div class="list-header">
      <AppSearch
        v-model:value="searchText"
        placeholder="搜索用户..."
        @search="handleSearch"
      />
      <AppButton type="primary" @click="handleAdd">添加用户</AppButton>
    </div>
    
    <AppTable
      :columns="columns"
      :data="tableData"
      :loading="loading"
      :pagination="true"
      :page="page"
      :pageSize="pageSize"
      :itemCount="total"
      @update:page="handlePageChange"
    />
  </AppCard>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { 
  AppCard, 
  AppSearch, 
  AppButton, 
  AppTable 
} from '@/components/common';

const searchText = ref('');
const loading = ref(false);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const tableData = ref([]);

const columns = [
  { title: '姓名', key: 'name' },
  { title: '年龄', key: 'age' },
  { title: '性别', key: 'gender' },
  { 
    title: '操作', 
    key: 'actions',
    render: (row) => {
      return h('div', { class: 'action-buttons' }, [
        h(AppButton, { 
          size: 'small', 
          onClick: () => handleEdit(row) 
        }, { default: () => '编辑' }),
        h(AppButton, { 
          size: 'small', 
          type: 'error', 
          onClick: () => handleDelete(row) 
        }, { default: () => '删除' })
      ]);
    }
  }
];

const handleSearch = () => {
  // 执行搜索逻辑
  loadData();
};

const handleAdd = () => {
  // 添加用户逻辑
};

const handleEdit = (row) => {
  // 编辑用户逻辑
};

const handleDelete = (row) => {
  // 删除用户逻辑
};

const handlePageChange = (newPage) => {
  page.value = newPage;
  loadData();
};

const loadData = () => {
  loading.value = true;
  // 模拟API请求
  setTimeout(() => {
    tableData.value = [
      { id: 1, name: '张三', age: 25, gender: '男' },
      { id: 2, name: '李四', age: 30, gender: '女' },
      // ...其他数据
    ];
    total.value = 100;
    loading.value = false;
  }, 500);
};

// 初始加载数据
loadData();
</script>

<style scoped>
.list-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}
</style>
```

## 注意事项

1. 所有组件都支持通过 `style` 和 `className` 属性进行样式自定义
2. 大部分组件提供了与 Naive UI 原始组件一致的事件和属性支持
3. 在使用前请确保已安装所有必要的依赖包 