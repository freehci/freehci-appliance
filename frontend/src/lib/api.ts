/** Base-URL: tom = same origin (nginx / vite proxy). */
export function getApiBase(): string {
  const v = import.meta.env.VITE_API_BASE_URL;
  return v != null && v !== "" ? v.replace(/\/$/, "") : "";
}

export async function apiGet<T>(path: string): Promise<T> {
  const base = getApiBase();
  const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}
