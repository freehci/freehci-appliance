/** Base-URL: tom = same origin (nginx / vite proxy). */
export function getApiBase(): string {
  const v = import.meta.env.VITE_API_BASE_URL;
  return v != null && v !== "" ? v.replace(/\/$/, "") : "";
}

function apiUrl(path: string): string {
  const base = getApiBase();
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

/** Lesbar feilmelding fra FastAPI `detail` når mulig. */
async function failMessage(res: Response, fallback: string): Promise<string> {
  try {
    const j: unknown = await res.json();
    if (j && typeof j === "object" && "detail" in j) {
      const d = (j as { detail: unknown }).detail;
      if (typeof d === "string") return d;
      if (Array.isArray(d))
        return d.map((x) => (typeof x === "object" && x && "msg" in x ? String((x as { msg: unknown }).msg) : String(x))).join("; ");
    }
  } catch {
    /* ignore */
  }
  return fallback;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path), { credentials: "include" });
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}

export async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "PATCH",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}

export async function apiDelete(path: string): Promise<void> {
  const res = await fetch(apiUrl(path), { method: "DELETE", credentials: "include" });
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
}
