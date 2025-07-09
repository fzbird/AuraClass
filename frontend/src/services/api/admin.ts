import http from '../http';

// 用户管理
export const getUsers = () => http.get('/users');
export const getUser = (id: number) => http.get(`/users/${id}`);
export const createUser = (data: any) => http.post('/users', data);
export const updateUser = (id: number, data: any) => http.put(`/users/${id}`, data);
export const deleteUser = (id: number) => http.delete(`/users/${id}`);

// 角色管理
export const getRoles = () => http.get('/roles');
export const getRole = (id: number) => http.get(`/roles/${id}`);
export const createRole = (data: any) => http.post('/roles', data);
export const updateRole = (id: number, data: any) => http.put(`/roles/${id}`, data);
export const deleteRole = (id: number) => http.delete(`/roles/${id}`);

// 权限管理
export const getPermissionPolicies = () => http.get('/permissions/policies');
export const getRolePermissions = (roleName: string) => http.get(`/permissions/role-policies/${roleName}`);
export const updateRolePermissions = (roleName: string, policies: any[]) => http.post(`/permissions/role-policies/${roleName}`, policies);
export const getPermissionResources = () => http.get('/permissions/resources');
export const getPermissionActions = () => http.get('/permissions/actions');
export const getAPIResources = () => http.get('/permissions/api-paths');
export const reloadPermissions = () => http.post('/permissions/reload');

// 系统设置
export const getSystemConfig = () => http.get('/admin/config');
export const updateSystemConfig = (data: any) => http.put('/admin/config', data);
export const restartServer = () => http.post('/admin/restart'); 