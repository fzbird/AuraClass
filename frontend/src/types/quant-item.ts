/**
 * 量化项目实体接口
 */
export interface QuantItem {
  id: number;
  name: string;
  category: string;
  description?: string;
  min_score: number;
  max_score: number;
  default_score?: number;
  default_reason?: string;
  weight: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * 创建量化项目负载接口
 */
export interface CreateQuantItemPayload {
  name: string;
  category: string;
  description?: string;
  min_score: number;
  max_score: number;
  default_score?: number;
  default_reason?: string;
  weight?: number;
  is_active?: boolean;
}

/**
 * 更新量化项目负载接口
 */
export interface UpdateQuantItemPayload {
  name?: string;
  category?: string;
  description?: string;
  min_score?: number;
  max_score?: number;
  default_score?: number;
  default_reason?: string;
  weight?: number;
  is_active?: boolean;
}

/**
 * 量化项目过滤参数接口
 */
export interface QuantItemFilter {
  name?: string;
  category?: string | string[];
  is_active?: boolean | string;
}

/**
 * 量化项目分类接口
 */
export interface QuantItemCategory {
  id: number;
  name: string;
  description?: string;
  order?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * 创建量化项目分类负载接口
 */
export interface CreateQuantItemCategoryPayload {
  name: string;
  description?: string;
  order?: number;
  is_active?: boolean;
}

/**
 * 更新量化项目分类负载接口
 */
export interface UpdateQuantItemCategoryPayload {
  name?: string;
  description?: string;
  order?: number;
  is_active?: boolean;
} 