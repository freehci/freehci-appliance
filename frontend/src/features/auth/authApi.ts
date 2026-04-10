import { apiGet, apiPost, apiPostNoContent } from "@/lib/api";

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type AdminMeResponse = {
  username: string;
};

export function fetchMe(): Promise<AdminMeResponse> {
  return apiGet<AdminMeResponse>("/api/v1/auth/me");
}

export function login(username: string, password: string): Promise<TokenResponse> {
  return apiPost<TokenResponse>("/api/v1/auth/login", { username, password });
}

export function changePassword(current_password: string, new_password: string): Promise<void> {
  return apiPostNoContent("/api/v1/auth/change-password", { current_password, new_password });
}
