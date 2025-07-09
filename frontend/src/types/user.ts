 /**
 * 用户基础信息
 */
export interface User {
    id: number;
    username: string;
    email: string;
    full_name: string;
    role_id?: number;
    role_name?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  }
  
  /**
   * 用户创建参数
   */
  export interface CreateUserPayload {
    username: string;
    email: string;
    password: string;
    full_name: string;
    role_id?: number;
    is_active?: boolean;
  }
  
  /**
   * 用户更新参数
   */
  export interface UpdateUserPayload {
    username?: string;
    email?: string;
    password?: string;
    full_name?: string;
    role_id?: number;
    is_active?: boolean;
  }
  
  /**
   * 用户登录参数
   */
  export interface LoginPayload {
    username: string;
    password: string;
    remember_me?: boolean;
  }
  
  /**
   * 用户登录响应
   */
  export interface LoginResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
    user: User;
  }
  
  /**
   * 更改密码参数
   */
  export interface ChangePasswordPayload {
    old_password: string;
    new_password: string;
  }