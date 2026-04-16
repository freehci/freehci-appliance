import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { apiGet, apiPost, apiPostMultipart } from "@/lib/api";

const PLUGIN_INSTALL = "/api/v1/plugin-install";

type InstalledRow = { slug: string; path: string; has_plugin_py: boolean };
type InstalledResponse = { items: InstalledRow[] };
type InstallResult = { slug: string; path: string; restart_hint: string };
type GitRefsResponse = { refs: string[] };
type GitScanResponse = { ref_used: string; plugin_py_relative_paths: string[] };

export function IntegrationsPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const [slugZip, setSlugZip] = useState("");
  const [gitUrl, setGitUrl] = useState("");
  const [gitRef, setGitRef] = useState("main");
  const [slugGit, setSlugGit] = useState("");
  const [subpath, setSubpath] = useState("");
  const [scanResult, setScanResult] = useState<GitScanResponse | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const installedQ = useQuery({
    queryKey: ["plugin-install", "installed"],
    queryFn: () => apiGet<InstalledResponse>(`${PLUGIN_INSTALL}/installed`),
  });

  const refsM = useMutation({
    mutationFn: () =>
      apiPost<GitRefsResponse>(`${PLUGIN_INSTALL}/git/refs`, {
        git_url: gitUrl.trim(),
        ref: gitRef.trim() || "main",
      }),
  });

  const scanM = useMutation({
    mutationFn: () =>
      apiPost<GitScanResponse>(`${PLUGIN_INSTALL}/git/scan`, {
        git_url: gitUrl.trim(),
        ref: gitRef.trim() || "main",
      }),
    onSuccess: (data) => {
      setScanResult(data);
      setMessage(null);
    },
    onError: (e: Error) => setMessage(e.message),
  });

  const installGitM = useMutation({
    mutationFn: () =>
      apiPost<InstallResult>(`${PLUGIN_INSTALL}/git/install`, {
        git_url: gitUrl.trim(),
        ref: gitRef.trim() || "main",
        slug: slugGit.trim(),
        plugin_subpath: subpath.trim() || null,
      }),
    onSuccess: async (data) => {
      setMessage(data.restart_hint);
      await qc.invalidateQueries({ queryKey: ["plugin-install", "installed"] });
    },
    onError: (e: Error) => setMessage(e.message),
  });

  const uploadM = useMutation({
    mutationFn: async (file: File) => {
      const fd = new FormData();
      fd.append("slug", slugZip.trim());
      fd.append("file", file);
      return apiPostMultipart<InstallResult>(`${PLUGIN_INSTALL}/upload`, fd);
    },
    onSuccess: async (data) => {
      setMessage(data.restart_hint);
      await qc.invalidateQueries({ queryKey: ["plugin-install", "installed"] });
    },
    onError: (e: Error) => setMessage(e.message),
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      <Panel title={t("integrations.title")}>
        <p style={{ marginTop: 0 }}>{t("integrations.intro")}</p>
        {message ? (
          <p style={{ color: "var(--color-text-muted)", fontSize: "var(--text-sm)" }}>{message}</p>
        ) : null}
      </Panel>

      <Panel title={t("integrations.installedTitle")}>
        {installedQ.isLoading ? (
          <p>{t("dcim.common.loading")}</p>
        ) : installedQ.isError ? (
          <p>{(installedQ.error as Error).message}</p>
        ) : installedQ.data?.items?.length ? (
          <ul style={{ margin: 0, paddingLeft: "1.25rem" }}>
            {installedQ.data.items.map((row) => (
              <li key={row.slug}>
                <code>{row.slug}</code> —{" "}
                {row.has_plugin_py ? t("integrations.hasPluginPy") : t("integrations.missingPluginPy")}
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ color: "var(--color-text-muted)" }}>{t("integrations.installedEmpty")}</p>
        )}
      </Panel>

      <Panel title={t("integrations.uploadTitle")}>
        <p style={{ marginTop: 0, fontSize: "var(--text-sm)", color: "var(--color-text-muted)" }}>
          {t("integrations.uploadHint")}
        </p>
        <label style={{ display: "block", marginBottom: "0.5rem" }}>
          {t("integrations.slugLabel")}
          <input
            style={{ display: "block", width: "100%", maxWidth: "24rem", marginTop: "0.25rem" }}
            value={slugZip}
            onChange={(e) => setSlugZip(e.target.value)}
            autoComplete="off"
          />
        </label>
        <input
          type="file"
          accept=".zip"
          disabled={!slugZip.trim()}
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f && slugZip.trim()) uploadM.mutate(f);
            e.target.value = "";
          }}
        />
        {uploadM.isPending ? <p>{t("integrations.uploading")}</p> : null}
      </Panel>

      <Panel title={t("integrations.gitTitle")}>
        <p style={{ marginTop: 0, fontSize: "var(--text-sm)", color: "var(--color-text-muted)" }}>
          {t("integrations.gitHint")}
        </p>
        <label style={{ display: "block", marginBottom: "0.5rem" }}>
          Git URL
          <input
            style={{ display: "block", width: "100%", maxWidth: "36rem", marginTop: "0.25rem" }}
            value={gitUrl}
            onChange={(e) => setGitUrl(e.target.value)}
            placeholder="https://github.com/org/repo.git"
            autoComplete="off"
          />
        </label>
        <label style={{ display: "block", marginBottom: "0.5rem" }}>
          {t("integrations.refLabel")}
          <input
            style={{ display: "block", width: "100%", maxWidth: "16rem", marginTop: "0.25rem" }}
            value={gitRef}
            onChange={(e) => setGitRef(e.target.value)}
            autoComplete="off"
          />
        </label>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "0.75rem" }}>
          <button type="button" onClick={() => refsM.mutate()} disabled={!gitUrl.trim() || refsM.isPending}>
            {refsM.isPending ? "…" : t("integrations.listRefs")}
          </button>
          <button type="button" onClick={() => scanM.mutate()} disabled={!gitUrl.trim() || scanM.isPending}>
            {scanM.isPending ? "…" : t("integrations.scanPlugins")}
          </button>
        </div>
        {refsM.data?.refs?.length ? (
          <p style={{ fontSize: "var(--text-xs)", color: "var(--color-text-muted)" }}>
            {t("integrations.refsPreview")}: {refsM.data.refs.slice(0, 12).join(", ")}
            {refsM.data.refs.length > 12 ? " …" : ""}
          </p>
        ) : null}
        {scanResult?.plugin_py_relative_paths?.length ? (
          <div style={{ marginBottom: "0.75rem" }}>
            <div style={{ fontSize: "var(--text-sm)" }}>{t("integrations.foundPluginPy")}</div>
            <ul style={{ fontSize: "var(--text-xs)", margin: "0.25rem 0 0 1rem" }}>
              {scanResult.plugin_py_relative_paths.map((p) => (
                <li key={p}>
                  <code>{p}</code>
                </li>
              ))}
            </ul>
          </div>
        ) : scanResult ? (
          <p style={{ color: "var(--color-text-warn, orange)" }}>{t("integrations.scanNoPluginPy")}</p>
        ) : null}
        <label style={{ display: "block", marginBottom: "0.5rem" }}>
          {t("integrations.slugLabel")}
          <input
            style={{ display: "block", width: "100%", maxWidth: "24rem", marginTop: "0.25rem" }}
            value={slugGit}
            onChange={(e) => setSlugGit(e.target.value)}
            autoComplete="off"
          />
        </label>
        <label style={{ display: "block", marginBottom: "0.75rem" }}>
          {t("integrations.subpathLabel")}
          <input
            style={{ display: "block", width: "100%", maxWidth: "36rem", marginTop: "0.25rem" }}
            value={subpath}
            onChange={(e) => setSubpath(e.target.value)}
            placeholder="(tom hvis plugin.py ligger i rot)"
            autoComplete="off"
          />
        </label>
        <button
          type="button"
          onClick={() => installGitM.mutate()}
          disabled={!gitUrl.trim() || !slugGit.trim() || installGitM.isPending}
        >
          {installGitM.isPending ? "…" : t("integrations.installFromGit")}
        </button>
      </Panel>

      <Panel title={t("integrations.idracTitle")}>
        <p style={{ marginTop: 0, fontSize: "var(--text-sm)", color: "var(--color-text-muted)" }}>
          {t("integrations.idracHint")}
        </p>
      </Panel>
    </div>
  );
}
