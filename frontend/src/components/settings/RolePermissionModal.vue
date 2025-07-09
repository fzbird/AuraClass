<script setup lang="ts">
import { ref, reactive, watchEffect, onMounted, watch, computed, h } from 'vue';
import { 
  NModal, NCard, NButton, NSpace, NTree, NCheckbox, 
  NInput, NSelect, NDivider, NInputGroup, NTag, useMessage 
} from 'naive-ui';
import { 
  getRolePermissions, 
  updateRolePermissions, 
  getPermissionResources, 
  getPermissionActions,
  getAPIResources,
  reloadPermissions
} from '@/services/api/admin';
import { useUserStore } from '@/stores/user';

const props = defineProps({
  show: Boolean,
  roleName: String,
  roleId: Number,
  isSystemRole: Boolean
});

const emit = defineEmits(['update:show', 'success']);

const message = useMessage();

// 本地模态框状态，用于避免直接修改props
const localShow = ref(false);

// 同步props.show和localShow
watch(() => props.show, (newVal) => {
  localShow.value = newVal;
  
  // 当模态框显示时，主动加载权限数据
  if (newVal && props.roleName) {
    console.log('模态框显示，加载角色权限:', props.roleName);
    loadRolePermissions();
  }
});

// 当localShow变化时通知父组件
watch(localShow, (newVal) => {
  if (newVal !== props.show) {
    emit('update:show', newVal);
  }
});

// 监听角色名称变化，当角色切换时重新加载权限
watch(() => props.roleName, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal && localShow.value) {
    console.log('角色名称变化，重新加载权限:', newVal);
    loadRolePermissions();
  }
});

// 加载状态
const loading = ref(false);
const saving = ref(false);

// 资源和操作列表
const resources = ref<string[]>([]);
const actions = ref<string[]>([]);
const currentRolePermissions = ref<any[]>([]);

// 已选权限
const selectedPermissions = reactive(new Map<string, Set<string>>());

// 新权限设置
const newResource = ref('');
const newAction = ref('*');
const resourceOptions = ref<{ label: string, value: string }[]>([]);
const actionOptions = ref<{ label: string, value: string }[]>([]);

// 对API路径进行分类
const categorizeResource = (resource: string): string => {
  // 根据路径前缀进行分类
  if (resource.includes('/quant-records')) {
    return '量化记录管理';
  } else if (resource.includes('/students')) {
    return '学生管理';
  } else if (resource.includes('/classes')) {
    return '班级管理';
  } else if (resource.includes('/users')) {
    return '用户管理';
  } else if (resource.includes('/auth')) {
    return '认证与授权';
  } else if (resource.includes('/permissions')) {
    return '权限管理';
  } else if (resource.includes('/ai-assistant')) {
    return 'AI助手';
  } else if (resource.includes('/reports')) {
    return '报表管理';
  } else if (resource.includes('/statistics')) {
    return '统计分析';
  } else if (resource.includes('/quant-items')) {
    return '量化项管理';
  } else {
    return '其他API';
  }
};

// 优化资源选项，添加分类和可用状态信息
const updateResourceOptions = () => {
  console.log('=== 开始更新资源选项 ===');
  console.log('输入参数 - 所有资源数量:', resources.value.length);
  console.log('输入参数 - 已选权限映射大小:', selectedPermissions.size);
  console.log('输入参数 - 前3个资源:', resources.value.slice(0, 3));
  
  // 所有可用资源
  const allResources = resources.value;
  
  console.log('更新资源选项 - 所有资源数量:', allResources.length);
  console.log('更新资源选项 - 已有权限资源数量:', selectedPermissions.size);
  
  if (allResources.length > 0) {
    console.log('资源示例:', allResources.slice(0, 5));
  }
  
  // 如果没有资源，直接返回空数组
  if (allResources.length === 0) {
    console.warn('没有可用的API资源');
    resourceOptions.value = [];
    return;
  }
  
  // 将所有资源转换为选项，只过滤掉完全授权的资源
  const availableOptions = allResources.map(resource => {
    // 检查资源是否已有权限
    const hasPermissions = selectedPermissions.has(resource);
    const actions = selectedPermissions.get(resource);
    const hasAllPermission = actions && actions.has('*');
    
    console.log(`资源 ${resource}: 有权限=${hasPermissions}, 全部权限=${hasAllPermission}`);
    
    // 只过滤掉拥有*权限的资源，其他都应该显示
    if (hasAllPermission) {
      return null;
    }
    
    // 构建标签，显示已有权限状态
    let label = resource;
    if (hasPermissions && actions && actions.size > 0) {
      const actionsList = Array.from(actions).join(', ');
      label = `${resource} (已授权: ${actionsList})`;
    }
    
    // 直接返回平面格式的选项，不使用分组
    return {
      label,
      value: resource
    };
  }).filter(item => item !== null) as any[];
  
  console.log('过滤后资源选项数量:', availableOptions.length);
  console.log('过滤后前3个选项:', availableOptions.slice(0, 3));
  
  // 直接使用平面选项，不使用分组格式
  resourceOptions.value = availableOptions;
  
  console.log(`更新资源选项完成：共${allResources.length}个资源，过滤后剩余${availableOptions.length}个可选资源，最终选项数量: ${resourceOptions.value.length}`);
  console.log('最终resourceOptions数组前3项:', resourceOptions.value.slice(0, 3));
  console.log('=== 资源选项更新完成 ===');
};

// 修改 loadResourcesAndActions 函数，获取真实API路径
const loadResourcesAndActions = async () => {
  try {
    console.log('开始加载API资源和操作...');
    
    // 使用useUserStore获取token
    const userStore = useUserStore();
    const token = userStore.token || '';
    
    if (!token) {
      console.error('未找到认证Token，无法请求API资源');
      message.error('未找到认证Token，请重新登录');
      return;
    }
    
    console.log('使用Token获取API资源列表:', token.substring(0, 10) + '...');
    
    const headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
    
    console.log('准备发送API请求...');
    
    try {
      // 先尝试使用Axios获取API路径（原始方式）
      console.log('使用Axios获取API路径...');
      const apiResourcesResp = await getAPIResources();
      console.log('Axios API路径响应:', apiResourcesResp);
      
      // 处理响应数据，支持多种响应格式
      let resourceData: string[] = [];
      if (Array.isArray(apiResourcesResp)) {
        resourceData = apiResourcesResp;
      } else if (apiResourcesResp && apiResourcesResp.data && Array.isArray(apiResourcesResp.data)) {
        resourceData = apiResourcesResp.data;
      } else if (apiResourcesResp && typeof apiResourcesResp === 'object') {
        // 检查其他可能的数据字段
        const possibleArrays = Object.values(apiResourcesResp).filter(Array.isArray);
        if (possibleArrays.length > 0) {
          resourceData = possibleArrays[0] as string[];
        }
      }
      
      if (resourceData.length > 0) {
        console.log('成功通过Axios获取API路径，数量:', resourceData.length);
        resources.value = resourceData;
      } else {
        console.warn('Axios获取API路径为空，尝试使用fetch...');
        
        // 如果Axios获取到空数据，尝试使用fetch
        const response = await fetch('/api/v1/permissions/api-paths', { headers });
        if (!response.ok) {
          throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Fetch API路径响应:', data);
        
        resources.value = Array.isArray(data) ? data : [];
        console.log('通过fetch获取API路径，数量:', resources.value.length);
      }
      
      // 获取操作列表
      const actionsResp = await getPermissionActions();
      console.log('操作列表响应:', actionsResp);
      
      // 解析操作响应
      actions.value = Array.isArray(actionsResp) ? actionsResp : 
                     (actionsResp && actionsResp.data) ? actionsResp.data : [];
      
      // 创建操作选项
      actionOptions.value = actions.value.map(a => ({ label: a, value: a }));
      
      // 记录资源数量
      console.log(`已加载 ${resources.value.length} 个API资源路径和 ${actions.value.length} 种操作类型`);
      
      // 更新资源选项
      updateResourceOptions();
      
      // 检查资源数组是否为空
      if (resources.value.length === 0) {
        console.error('API资源数组为空，请检查API返回格式或网络连接');
        console.warn('使用硬编码的备用资源列表');
        
        // 提供备用的硬编码资源列表
        const fallbackResources = [
          "/api/v1/users",
          "/api/v1/users/{user_id}",
          "/api/v1/roles",
          "/api/v1/roles/{role_id}",
          "/api/v1/classes",
          "/api/v1/classes/{class_id}",
          "/api/v1/students",
          "/api/v1/students/{student_id}",
          "/api/v1/quant-items",
          "/api/v1/quant-items/{item_id}",
          "/api/v1/quant-records",
          "/api/v1/quant-records/{record_id}",
          "/api/v1/notifications",
          "/api/v1/ai-assistant/chat",
          "/api/v1/permissions/policies",
          "/api/v1/permissions/role-policies/{role_name}",
          "/api/v1/statistics/dashboard",
          "/api/v1/admin/config"
        ];
        
        resources.value = fallbackResources;
        console.log('已使用备用资源列表，数量:', resources.value.length);
        message.warning('无法从服务器加载API资源列表，已使用备用列表');
      } else {
        console.log('API资源加载成功，前5个资源:', resources.value.slice(0, 5));
      }
    } catch (fetchError) {
      console.error('请求API资源失败:', fetchError);
      message.error('请求API资源失败: ' + (fetchError as Error).message);
    }
  } catch (error) {
    console.error('加载资源和操作失败:', error);
    message.error('无法加载权限资源和操作');
  }
};

// 加载角色当前权限
const loadRolePermissions = async () => {
  if (!props.roleName) {
    console.warn('无法加载权限：角色名称为空');
    return;
  }
  
  loading.value = true;
  console.log(`开始加载角色[${props.roleName}]的权限数据`);
  
  try {
    // 调用API获取角色权限
    const response = await getRolePermissions(props.roleName);
    
    // 日志输出响应内容，确定正确的数据结构
    console.log(`成功获取角色[${props.roleName}]权限数据:`, response);
    
    // 根据日志显示，API返回的数据直接就是数组，不需要访问.data
    // 前端HTTP拦截器在某些情况下会自动提取响应中的data字段
    const permissions = Array.isArray(response) ? response : 
                        (response && response.data && Array.isArray(response.data)) ? response.data : [];
    
    currentRolePermissions.value = permissions;
    
    // 清空现有的权限映射，重新构建
    selectedPermissions.clear();
    
    // 处理每个权限项
    permissions.forEach((p: any) => {
      // 确保从正确的属性中获取资源和动作
      const resource = p.resource;
      const action = p.action;
      
      // 权限资源或动作为空则跳过
      if (!resource || !action) {
        console.warn('跳过无效的权限项:', p);
        return;
      }
      
      if (!selectedPermissions.has(resource)) {
        selectedPermissions.set(resource, new Set());
      }
      
      selectedPermissions.get(resource)?.add(action);
    });
    
    // 输出加载结果
    console.log(`角色[${props.roleName}]权限数据已加载，共${permissions.length}条权限，处理后资源数:${selectedPermissions.size}`);
    
    // 调试输出当前权限映射
    if (selectedPermissions.size > 0) {
      console.log('当前加载的权限映射:');
      selectedPermissions.forEach((actions, resource) => {
        console.log(`- ${resource}: ${Array.from(actions).join(', ')}`);
      });
    } else if (permissions.length > 0) {
      console.warn('权限数据加载异常：API返回了权限但未能正确处理', permissions);
    }
    
    // 更新资源选项，确保显示所有未授予完全权限的资源
    if (resources.value.length > 0) {
      console.log(`更新资源选项 - 角色权限加载后 - 资源数量: ${resources.value.length}`);
      updateResourceOptions();
    } else {
      console.warn('角色权限加载完成，但资源列表为空，需要先加载API资源');
    }
    
  } catch (error) {
    console.error(`加载角色[${props.roleName}]权限失败:`, error);
    message.error('无法加载角色权限');
  } finally {
    loading.value = false;
  }
};

// 检查某个资源的某个操作是否已选择
const isPermissionSelected = (resource: string, action: string): boolean => {
  return selectedPermissions.get(resource)?.has(action) || false;
};

// 切换权限选择状态
const togglePermission = (resource: string, action: string) => {
  if (!selectedPermissions.has(resource)) {
    selectedPermissions.set(resource, new Set());
  }
  
  const actions = selectedPermissions.get(resource)!;
  
  if (actions.has(action)) {
    actions.delete(action);
    if (actions.size === 0) {
      selectedPermissions.delete(resource);
    }
  } else {
    actions.add(action);
  }
  
  // 更新资源选项
  updateResourceOptions();
};

// 添加新权限
const addPermission = () => {
  console.log('准备添加权限:', { resource: newResource.value, action: newAction.value });
  
  if (!newResource.value || !newAction.value) {
    message.warning('请选择资源和操作');
    return;
  }
  
  // 检查权限是否已存在
  const existingActions = selectedPermissions.get(newResource.value);
  if (existingActions && existingActions.has(newAction.value)) {
    message.warning(`权限 "${newResource.value} - ${newAction.value}" 已存在`);
    return;
  }
  
  if (!selectedPermissions.has(newResource.value)) {
    selectedPermissions.set(newResource.value, new Set());
  }
  
  selectedPermissions.get(newResource.value)?.add(newAction.value);
  
  console.log('权限已添加:', { resource: newResource.value, action: newAction.value });
  console.log('当前已选权限数量:', selectedPermissions.size);
  
  // 添加权限后更新资源选项
  updateResourceOptions();
  
  // 重置输入
  newResource.value = '';
  newAction.value = '*';
  
  message.success('权限已添加');
};

// 全选/取消全选
const setAllActionsForResource = (resource: string, selected: boolean) => {
  if (selected) {
    // 全选
    if (!selectedPermissions.has(resource)) {
      selectedPermissions.set(resource, new Set());
    }
    
    const actionSet = selectedPermissions.get(resource)!;
    actions.value.forEach(action => actionSet.add(action));
  } else {
    // 取消全选
    selectedPermissions.delete(resource);
  }
  
  // 更新资源选项
  updateResourceOptions();
};

// 全部选择 * 操作
const setAllResourcesAll = () => {
  resources.value.forEach(resource => {
    if (!selectedPermissions.has(resource)) {
      selectedPermissions.set(resource, new Set());
    }
    selectedPermissions.get(resource)?.add('*');
  });
  
  // 更新资源选项
  updateResourceOptions();
  
  message.success('已设置所有资源对应"*"操作');
};

// 保存权限设置
const handleSave = async () => {
  if (!props.roleName) {
    message.error('角色名不能为空');
    return;
  }
  
  saving.value = true;
  
  try {
    // 转换权限设置为后端格式
    const policies: any[] = [];
    
    selectedPermissions.forEach((actions, resource) => {
      actions.forEach(action => {
        policies.push({
          resource,
          action
        });
      });
    });
    
    await updateRolePermissions(props.roleName, policies);
    
    // 重新加载权限策略
    await reloadPermissions();
    
    message.success('角色权限已保存');
    emit('success');
    localShow.value = false;
  } catch (error) {
    console.error('Failed to save role permissions:', error);
    message.error('保存角色权限失败');
  } finally {
    saving.value = false;
  }
};

// 关闭模态框
const handleClose = () => {
  localShow.value = false;
  // 清空资源列表，确保下次打开时能重新获取
  resources.value = [];
  resourceOptions.value = [];
};

// 组件挂载时加载资源和操作列表（不加载角色权限）
onMounted(() => {
  loadResourcesAndActions();
  // 初始化本地状态
  localShow.value = props.show;
});

// 添加自定义渲染函数
const renderResourceLabel = (option: any) => {
  // 仅返回资源路径，不带分类信息
  return h('span', {}, option?.label || '');
};

const renderResourceOption = (option: any) => {
  // 现在只处理资源项，不需要分组标题处理
  const label = option?.label || '';
  const isPartial = typeof label === 'string' && label.includes('(已授权:');
  
  return h('div', { 
    style: `
      display: flex; 
      flex-direction: column;
      padding: 4px 0;
    `
  }, [
    h('span', {}, label),
    isPartial ? h('span', { 
      style: 'font-size: 12px; color: #d03050;' 
    }, '已授予部分权限，可继续添加其他操作') : null
  ]);
};

// 打开模态框时的处理
const onOpen = async () => {
  loading.value = true;
  console.log('模态框打开，开始加载数据...');
  
  try {
    // 先清空现有数据，确保不受上次加载的影响
    resourceOptions.value = [];
    resources.value = [];
    actions.value = [];
    selectedPermissions.clear();
    newResource.value = '';
    newAction.value = '*';
    
    // 始终先加载API资源和操作
    console.log('开始加载API资源...');
    await loadResourcesAndActions();
    console.log(`API资源加载完成，共${resources.value.length}个资源`);
    
    // 如果传入了角色名称，则加载该角色的权限
    if (props.roleName) {
      console.log(`开始加载角色[${props.roleName}]权限...`);
      await loadRolePermissions();
      console.log(`角色[${props.roleName}]权限加载完成`);
    }
    
    // 确保更新资源选项
    console.log('更新资源选项列表...');
    updateResourceOptions();
    
    loading.value = false;
    console.log('模态框数据加载完成');
  } catch (error) {
    console.error('加载角色权限数据失败:', error);
    message.error('加载权限数据失败，请刷新重试');
    loading.value = false;
  }
};
</script>

<template>
  <NModal 
    :show="localShow" 
    @update:show="localShow = $event"
    @show="onOpen"
    preset="card" 
    style="width: 800px;"
    :title="`编辑角色权限: ${props.roleName || ''}`"
    :closable="true"
    :mask-closable="false"
    :bordered="false"
  >
    <div class="permission-modal-content">
      <div class="header-info">
        <h3>角色: {{ roleName }} <NTag v-if="isSystemRole" type="info">系统角色</NTag></h3>
        <p class="role-warning" v-if="isSystemRole">
          注意：修改系统角色权限可能会影响系统功能，请谨慎操作。
        </p>
        <p class="resource-info">
          权限管理基于后端API路径，为每个资源路径分配操作权限（GET、POST、PUT、DELETE等）。
          添加「*」操作表示授予该资源所有操作权限。
        </p>
      </div>
      
      <NDivider>已配置权限</NDivider>
      
      <div class="permissions-list" :class="{ 'is-loading': loading }">
        <div v-if="loading" class="loading-indicator">
          正在加载角色权限...
        </div>
        
        <div v-else-if="Array.from(selectedPermissions.keys()).length === 0" class="empty-permissions">
          <p>该角色暂无权限配置</p>
        </div>
        
        <div v-else class="resource-groups">
          <div 
            v-for="resource in Array.from(selectedPermissions.keys()).sort()" 
            :key="resource"
            class="resource-group"
          >
            <div class="resource-header">
              <div class="resource-name">{{ resource }}</div>
              <div class="resource-actions">
                <NButton 
                  size="tiny" 
                  type="error"
                  @click="setAllActionsForResource(resource, false)"
                >
                  移除
                </NButton>
              </div>
            </div>
            
            <div class="action-tags">
              <NTag 
                v-for="action in Array.from(selectedPermissions.get(resource) || [])" 
                :key="`${resource}-${action}`"
                closable
                @close="togglePermission(resource, action)"
                :type="action === '*' ? 'success' : 'info'"
              >
                {{ action }}
              </NTag>
            </div>
          </div>
        </div>
      </div>
      
      <NDivider>添加权限</NDivider>
      
      <div class="add-permission">
        <div class="permission-helper-text" v-if="loading">
          正在加载可用API资源...
        </div>
        <div class="permission-helper-text" v-else-if="resources.length === 0">
          无法加载API资源列表，请刷新页面重试或联系管理员
        </div>
        <div class="permission-helper-text" v-else-if="resourceOptions.length === 0">
          <div>已授予所有API资源完全权限，无可添加项</div>
          <div style="font-size: 12px; margin-top: 8px; color: #666;">
            调试信息：API资源总数 {{ resources.length }}，已授权资源数 {{ selectedPermissions.size }}，可选资源数 {{ resourceOptions.length }}
          </div>
        </div>
        <div v-else>
          <div style="font-size: 12px; margin-bottom: 8px; color: #666;">
            调试信息：API资源总数 {{ resources.length }}，已授权资源数 {{ selectedPermissions.size }}，可选资源数 {{ resourceOptions.length }}
          </div>
          <div style="font-size: 11px; margin-bottom: 8px; color: #999; max-height: 60px; overflow-y: auto;">
            资源选项详情：{{ JSON.stringify(resourceOptions.slice(0, 3), null, 2) }}
          </div>
          <NInputGroup>
            <NSelect 
              v-model:value="newResource" 
              :options="resourceOptions" 
              placeholder="选择未授权或部分授权的API路径"
              filterable
              style="width: 60%"
              :key="'resource-select-' + resourceOptions.length + '-' + Date.now()"
            />
            
            <NSelect 
              v-model:value="newAction" 
              :options="actionOptions" 
              placeholder="选择操作"
              style="width: 25%"
            />
            
            <NButton type="info" @click="addPermission" style="width: 15%">添加</NButton>
          </NInputGroup>
        </div>
        
        <div class="quick-actions">
          <NButton size="small" @click="setAllResourcesAll">
            授予所有资源"*"权限
          </NButton>
          <NSpace size="small" justify="end" style="margin-top: 8px">
            <NTag type="info">提示：API路径中的{id}表示路径参数，如学生ID、角色ID等</NTag>
          </NSpace>
        </div>
      </div>
      
      <div class="modal-footer">
        <NSpace justify="end">
          <NButton @click="handleClose">取消</NButton>
          <NButton type="primary" @click="handleSave" :loading="saving">保存</NButton>
        </NSpace>
      </div>
    </div>
  </NModal>
</template>

<style scoped>
.permission-modal-content {
  max-height: 70vh;
  overflow-y: auto;
}

.header-info {
  margin-bottom: 16px;
}

.role-warning {
  color: #d03050;
  font-size: 12px;
  margin-top: 8px;
}

.permissions-list {
  margin-bottom: 20px;
  min-height: 100px;
  position: relative;
}

.permissions-list.is-loading {
  opacity: 0.7;
}

.loading-indicator {
  text-align: center;
  padding: 20px;
  color: #2080f0;
  font-size: 14px;
}

.empty-permissions {
  color: #999;
  text-align: center;
  padding: 20px 0;
}

.resource-groups {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.resource-group {
  border: 1px solid #e5e5e5;
  border-radius: 4px;
  padding: 12px;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.resource-name {
  font-weight: bold;
  font-size: 14px;
}

.action-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.add-permission {
  margin-bottom: 24px;
}

.quick-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.modal-footer {
  margin-top: 24px;
}

.permission-helper-text {
  text-align: center;
  color: #999;
  padding: 12px;
  border: 1px dashed #e0e0e0;
  border-radius: 4px;
  margin-bottom: 12px;
}

.resource-info {
  margin: 12px 0;
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.5;
  color: #606266;
}
</style> 