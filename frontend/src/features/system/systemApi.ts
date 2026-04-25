import { apiGet, apiPost } from "@/lib/api";

const P = "/api/v1/system";

export type UpdateStartResponse = { job_id: string };

export type UpdateStatusResponse = {
  running: boolean;
  job_id: string | null;
  started_at: string | null;
  finished_at: string | null;
  exit_code: number | null;
  detail: string | null;
  log_tail: string[];
};

export type UpdateCheckResponse = {
  local_version: string;
  remote_version: string | null;
  update_available: boolean;
  remote_error: string | null;
};

export type SystemStatusResponse = {
  update_check: UpdateCheckResponse;
  updater_available: boolean;
  updater_error: string | null;
  updater_status: UpdateStatusResponse | null;
};

export function updateNow(): Promise<UpdateStartResponse> {
  return apiPost(`${P}/update-now`, {});
}

export function updateStatus(): Promise<UpdateStatusResponse> {
  return apiGet(`${P}/update-status`);
}

export function updateCheck(): Promise<UpdateCheckResponse> {
  return apiGet(`${P}/update-check`);
}

export function systemStatus(): Promise<SystemStatusResponse> {
  return apiGet(`${P}/status`);
}

