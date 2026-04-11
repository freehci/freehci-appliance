import { getStoredAccessToken, setStoredAccessToken } from "./authStorage";

/** Base-URL: tom = same origin (nginx / vite proxy). */
export function getApiBase(): string {
  const v = import.meta.env.VITE_API_BASE_URL;
  return v != null && v !== "" ? v.replace(/\/$/, "") : "";
}

export function apiUrl(path: string): string {
  const base = getApiBase();
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

function authHeaders(): Record<string, string> {
  const t = getStoredAccessToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

async function onUnauthorized(path: string): Promise<void> {
  if (path.includes("/auth/login")) return;
  setStoredAccessToken(null);
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("freehci:auth-cleared"));
    if (!window.location.pathname.startsWith("/login")) {
      window.location.assign("/login");
    }
  }
}

/** Lesbar feilmelding fra FastAPI `detail` når mulig. */
async function failMessage(res: Response, fallback: string): Promise<string> {
  try {
    const j: unknown = await res.json();
    if (j && typeof j === "object" && "detail" in j) {
      const d = (j as { detail: unknown }).detail;
      if (typeof d === "string") return d;
      if (Array.isArray(d))
        return d
          .map((x) => (typeof x === "object" && x && "msg" in x ? String((x as { msg: unknown }).msg) : String(x)))
          .join("; ");
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
  const res = await fetch(apiUrl(path), {
    credentials: "include",
    headers: { ...authHeaders() },
  });
  if (res.status === 401) await onUnauthorized(path);
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}

/** GET som ren tekst (f.eks. text/plain MIB-kilde). */
export async function apiGetText(path: string): Promise<string> {
  const res = await fetch(apiUrl(path), {
    credentials: "include",
    headers: { ...authHeaders() },
  });
  if (res.status === 401) await onUnauthorized(path);
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
  return res.text();
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "POST",
    credentials: "include",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (res.status === 401) await onUnauthorized(path);
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}

export async function apiPostNoContent(path: string, body: unknown): Promise<void> {
  const res = await fetch(apiUrl(path), {
    method: "POST",
    credentials: "include",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (res.status === 401) await onUnauthorized(path);
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
}

export async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "PATCH",
    credentials: "include",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (res.status === 401) await onUnauthorized(path);
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}

export async function apiDelete(path: string): Promise<void> {
  const res = await fetch(apiUrl(path), {
    method: "DELETE",
    credentials: "include",
    headers: { ...authHeaders() },
  });
  if (res.status === 401) await onUnauthorized(path);
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
}

/** Multipart POST (f.eks. filopplasting); ikke sett Content-Type — nettleseren setter boundary. */
export async function apiPostMultipart<T>(path: string, formData: FormData): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "POST",
    credentials: "include",
    headers: { ...authHeaders() },
    body: formData,
  });
  if (res.status === 401) await onUnauthorized(path);
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}

export async function apiDeleteJson<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "DELETE",
    credentials: "include",
    headers: { ...authHeaders() },
  });
  if (res.status === 401) await onUnauthorized(path);
  if (!res.ok) {
    const msg = await failMessage(res, `${res.status} ${res.statusText}`);
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}
