<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NDataTable, NButton, NTag, NSpace, useMessage } from 'naive-ui';
import { h } from 'vue';
import { getRoles, deleteRole } from '@/services/api/admin';
import RolePermissionModal from './RolePermissionModal.vue';

const message = useMessage();

// 角色数据
const roles = ref<any[]>([]);
const loadingRoles = ref(true);

// 权限编辑弹窗
const showPermissionModal = ref(false);
const currentRole = ref<any>(null);

// 加载角色列表
const loadRoles = async () => {
  loadingRoles.value = true;
  try {
    const response = await getRoles();
    roles.value = response.data || [];
  } catch (error) {
    console.error('获取角色列表失败:', error);
    message.error('获取角色列表失败');
  } finally {
    loadingRoles.value = false;
  }
};

// 表格列定义
const columns = [
  {
    title: '角色名称',
    key: 'name'
  },
  {
    title: '描述',
    key: 'description'
  },
  {
    title: '类型',
    key: 'is_system',
    render(row) {
      return h(NTag, {
        type: row.is_system ? 'info' : 'success'
      }, { default: () => row.is_system ? '系统角色' : '自定义角色' });
    }
  },
  {
    title: '操作',
    key: 'actions',
    render(row) {
      return h(NSpace, null, {
        default: () => [
          h(NButton, {
            type: 'primary',
            size: 'small',
            onClick: () => handleEditPermissions(row)
          }, { default: () => '编辑权限' }),
          h(NButton, {
            disabled: row.is_system,
            size: 'small',
            type: 'error',
            onClick: () => handleDeleteRole(row)
          }, { default: () => '删除' })
        ]
      });
    }
  }
];

// 编辑角色权限
const handleEditPermissions = (role) => {
  currentRole.value = role;
  showPermissionModal.value = true;
};

// 删除角色
const handleDeleteRole = async (role) => {
  if (confirm(`确定要删除角色"${role.name}"吗？`)) {
    try {
      await deleteRole(role.id);
      message.success('角色删除成功');
      await loadRoles();
    } catch (error) {
      console.error('删除角色失败:', error);
      message.error('删除角色失败');
    }
  }
};

// 权限编辑成功
const handlePermissionSuccess = async () => {
  message.success('角色权限更新成功');
  await loadRoles();
};

// 添加新角色
const handleAddRole = () => {
  message.info('请前往角色管理页面添加新角色');
};

onMounted(() => {
  loadRoles();
});
</script>

<template>
  <div class="permission-management">
    <div class="header-actions">
      <NButton type="primary" @click="handleAddRole">添加角色</NButton>
    </div>
    
    <NDataTable 
      :columns="columns" 
      :data="roles" 
      :bordered="false" 
      :loading="loadingRoles"
    />
    
    <div class="permissions-tip">
      <p>系统角色不可删除，但可以编辑权限设置</p>
    </div>
    
    <!-- 权限编辑弹窗 -->
    <RolePermissionModal
      v-model:show="showPermissionModal"
      :role-name="currentRole?.name"
      :role-id="currentRole?.id"
      :is-system-role="currentRole?.is_system"
      @success="handlePermissionSuccess"
    />
  </div>
</template>

<style scoped>
.permission-management {
  width: 100%;
}

.header-actions {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}

.permissions-tip {
  margin-top: 16px;
  font-size: 12px;
  color: #888;
}
</style> 