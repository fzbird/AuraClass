<template>
  <div :class="[className, 'app-upload-wrapper']">
    <n-upload
      :action="action"
      :headers="headers"
      :data="data"
      :name="name"
      :max-size="maxSize"
      :multiple="multiple"
      :directory="directory"
      :disabled="disabled"
      :accept="accept"
      :default-upload="defaultUpload"
      :file-list="fileList"
      :list-type="listType"
      :show-file-list="showFileList"
      :show-preview-button="showPreviewButton"
      :show-remove-button="showRemoveButton"
      :show-download-button="showDownloadButton"
      :show-retry-button="showRetryButton"
      :show-cancel-button="showCancelButton"
      :with-credentials="withCredentials"
      :style="style"
      :class="uploadClass"
      :custom-request="customRequest"
      :abstract="abstract"
      :method="method"
      :xhrMap="xhrMap"
      @change="handleChange"
      @update:file-list="handleUpdateFileList"
      @before-upload="handleBeforeUpload"
      @finish="handleFinish"
      @error="handleError"
      @remove="handleRemove"
      @preview="handlePreview"
      @download="handleDownload"
    >
      <template v-if="$slots.default">
        <slot />
      </template>
      <template v-else-if="!isImageUploader">
        <n-button>
          {{ uploadButtonText }}
        </n-button>
      </template>
      <template #icon v-if="$slots.icon">
        <slot name="icon" />
      </template>
      <template #trigger v-if="$slots.trigger">
        <slot name="trigger" />
      </template>
      <template #file-list v-if="$slots['file-list']">
        <slot name="file-list" />
      </template>
      <template #default v-if="isImageUploader && !$slots.default">
        <div class="app-upload-image-card">
          <n-icon size="20" class="app-upload-image-icon">
            <UploadOutlined />
          </n-icon>
          <div class="app-upload-image-text">
            {{ uploadButtonText || '点击上传' }}
          </div>
        </div>
      </template>
    </n-upload>
    <div v-if="error" class="app-upload-error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { NUpload, NButton, NIcon } from 'naive-ui';
import { UploadOutlined } from 'naive-ui';
import type { CSSProperties, PropType } from 'vue';

// 文件列表类型
type UploadFileInfo = {
  id: string;
  name: string;
  status: 'pending' | 'uploading' | 'finished' | 'error' | 'removed';
  percentage?: number;
  file?: File;
  thumbnailUrl?: string;
  url?: string;
  type?: string;
  [key: string]: any;
};

// 上传组件类型
type ListType = 'text' | 'image' | 'image-card';

const props = defineProps({
  // 上传地址
  action: {
    type: String,
    default: ''
  },
  // 请求头
  headers: {
    type: Object,
    default: () => ({})
  },
  // 附带数据
  data: {
    type: Object,
    default: () => ({})
  },
  // 文件字段名
  name: {
    type: String,
    default: 'file'
  },
  // 文件大小限制（字节）
  maxSize: {
    type: Number,
    default: undefined
  },
  // 是否支持多选
  multiple: {
    type: Boolean,
    default: false
  },
  // 是否支持上传文件夹
  directory: {
    type: Boolean,
    default: false
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 接受的文件类型
  accept: {
    type: String,
    default: ''
  },
  // 是否默认上传
  defaultUpload: {
    type: Boolean,
    default: true
  },
  // 文件列表
  fileList: {
    type: Array as PropType<UploadFileInfo[]>,
    default: () => []
  },
  // 列表类型
  listType: {
    type: String as () => ListType,
    default: 'text'
  },
  // 是否显示文件列表
  showFileList: {
    type: Boolean,
    default: true
  },
  // 是否显示预览按钮
  showPreviewButton: {
    type: Boolean,
    default: true
  },
  // 是否显示删除按钮
  showRemoveButton: {
    type: Boolean,
    default: true
  },
  // 是否显示下载按钮
  showDownloadButton: {
    type: Boolean,
    default: false
  },
  // 是否显示重试按钮
  showRetryButton: {
    type: Boolean,
    default: true
  },
  // 是否显示取消按钮
  showCancelButton: {
    type: Boolean,
    default: true
  },
  // 是否发送 cookie
  withCredentials: {
    type: Boolean,
    default: false
  },
  // 是否为抽象上传组件
  abstract: {
    type: Boolean,
    default: false
  },
  // 上传请求方法
  method: {
    type: String,
    default: 'POST'
  },
  // 自定义请求函数
  customRequest: {
    type: Function,
    default: undefined
  },
  // 自定义上传按钮文本
  uploadButtonText: {
    type: String,
    default: '点击上传'
  },
  // 错误信息
  error: {
    type: String,
    default: ''
  },
  // 自定义样式
  style: {
    type: [String, Object] as unknown as PropType<string | CSSProperties>,
    default: () => ({})
  },
  // 自定义类名
  className: {
    type: String,
    default: ''
  },
  // 上传组件类名
  uploadClass: {
    type: String,
    default: ''
  },
  // XHR 映射表
  xhrMap: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits([
  'update:fileList',
  'change',
  'beforeUpload',
  'finish',
  'error',
  'remove',
  'preview',
  'download'
]);

// 是否为图片上传器
const isImageUploader = computed(() => props.listType === 'image-card');

// 处理文件列表更新
const handleUpdateFileList = (files: UploadFileInfo[]) => {
  emit('update:fileList', files);
};

// 处理上传变化
const handleChange = (options: { fileList: UploadFileInfo[], event?: Event }) => {
  emit('change', options);
};

// 处理上传前钩子
const handleBeforeUpload = (data: { file: UploadFileInfo, fileList: UploadFileInfo[] }) => {
  return emit('beforeUpload', data);
};

// 处理上传完成
const handleFinish = (data: { file: UploadFileInfo, event?: Event }) => {
  emit('finish', data);
};

// 处理上传错误
const handleError = (data: { file: UploadFileInfo, event?: Event }) => {
  emit('error', data);
};

// 处理移除文件
const handleRemove = (data: { file: UploadFileInfo, fileList: UploadFileInfo[] }) => {
  emit('remove', data);
};

// 处理预览文件
const handlePreview = (file: UploadFileInfo) => {
  emit('preview', file);
};

// 处理下载文件
const handleDownload = (file: UploadFileInfo) => {
  emit('download', file);
};
</script>

<style scoped>
.app-upload-wrapper {
  width: 100%;
  position: relative;
}

.app-upload-error {
  color: var(--error-color, #f5222d);
  font-size: 12px;
  line-height: 1.5;
  margin-top: 4px;
}

.app-upload-image-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  border: 1px dashed #d9d9d9;
  border-radius: 2px;
  cursor: pointer;
  padding: 16px;
  text-align: center;
  transition: border-color .3s;
}

.app-upload-image-card:hover {
  border-color: var(--primary-color, #1890ff);
}

.app-upload-image-icon {
  margin-bottom: 8px;
  color: rgba(0, 0, 0, 0.45);
}

.app-upload-image-text {
  color: rgba(0, 0, 0, 0.85);
  font-size: 14px;
}
</style> 