import { apiDelete, apiGet, apiPost, apiPostNoContent } from "@/lib/api";

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type AdminMeResponse = {
  id: number;
  username: string;
};

export type AdminAccount = {
  id: number;
  username: string;
  updated_at: string;
  is_self: boolean;
};

export type ApiToken = {
  id: number;
  name: string;
  token_prefix: string;
  created_at: string;
  last_used_at: string | null;
  expires_at: string | null;
  scopes?: string[] | null;
};

export type ApiTokenCreated = ApiToken & {
  token: string;
};

export type AgentConnectInfo = {
  app_name: string;
  api_prefix: string;
  openapi_url: string;
  docs_url: string;
  auth: {
    type: string;
    header: string;
    login_url: string;
    tokens_url: string;
    token_prefix: string;
    notes: string[];
  };
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

export function listAccounts(): Promise<AdminAccount[]> {
  return apiGet("/api/v1/auth/accounts");
}

export function createAccount(username: string, password: string): Promise<AdminAccount> {
  return apiPost("/api/v1/auth/accounts", { username, password });
}

export function resetAccountPassword(accountId: number, new_password: string): Promise<void> {
  return apiPostNoContent(`/api/v1/auth/accounts/${accountId}/reset-password`, { new_password });
}

export function deleteAccount(accountId: number): Promise<void> {
  return apiDelete(`/api/v1/auth/accounts/${accountId}`);
}

export function listApiTokens(): Promise<ApiToken[]> {
  return apiGet("/api/v1/auth/tokens");
}

export function createApiToken(name: string, scopes?: string[] | null): Promise<ApiTokenCreated> {
  return apiPost("/api/v1/auth/tokens", { name, scopes: scopes ?? undefined });
}

export function deleteApiToken(tokenId: number): Promise<void> {
  return apiDelete(`/api/v1/auth/tokens/${tokenId}`);
}

export function fetchAgentInfo(): Promise<AgentConnectInfo> {
  return apiGet("/api/v1/auth/agent");
}
