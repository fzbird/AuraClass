import http from '../http';
import { LoginRequest, LoginResponse, User } from '@/types';

export const login = async (credentials: LoginRequest) => {
  return http.post<LoginResponse>('/auth/login', credentials);
};

export const refreshToken = async (refreshToken: string) => {
  return http.post<LoginResponse>('/auth/refresh', { refresh_token: refreshToken });
};

export const logout = async () => {
  return http.post('/auth/logout');
};

export const getCurrentUser = async () => {
  return http.get<User>('/auth/me');
};
