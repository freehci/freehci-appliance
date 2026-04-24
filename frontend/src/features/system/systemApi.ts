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

export function updateNow(): Promise<UpdateStartResponse> {
  return apiPost(`${P}/update-now`, {});
}

export function updateStatus(): Promise<UpdateStatusResponse> {
  return apiGet(`${P}/update-status`);
}

