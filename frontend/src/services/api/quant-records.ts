import http from '../http';
import { QuantRecord, ApiResponse } from '@/types';

export interface CreateQuantRecordPayload {
  student_id: number;
  item_id: number;
  score: number;
  reason?: string;
  record_date: string;
}

export interface UpdateQuantRecordPayload {
  score?: number;
  reason?: string;
  record_date?: string;
}

export const getQuantRecords = async (params = {}) => {
  return http.get<ApiResponse<QuantRecord[]>>('/quant-records', { params });
};

export const getQuantRecord = async (id: number) => {
  return http.get<ApiResponse<QuantRecord>>(`/quant-records/${id}`);
};

export const createQuantRecord = async (data: CreateQuantRecordPayload) => {
  return http.post<ApiResponse<QuantRecord>>('/quant-records', data);
};

export const createBatchQuantRecords = async (data: CreateQuantRecordPayload[]) => {
  return http.post<ApiResponse<{ created: number }>>('/quant-records/batch', data);
};

export const updateQuantRecord = async (id: number, data: UpdateQuantRecordPayload) => {
  return http.put<ApiResponse<QuantRecord>>(`/quant-records/${id}`, data);
};

export const deleteQuantRecord = async (id: number) => {
  return http.delete(`/quant-records/${id}`);
};
