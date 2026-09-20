import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Panel } from "@/components/ui/Panel";
import dcimStyles from "@/features/dcim/dcim.module.css";
import * as federationApi from "@/features/integrations/federationApi";
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
  const [pairingToken, setPairingToken] = useState<string | null>(null);
  const [peerUrl, setPeerUrl] = useState("");
  const [connectToken, setConnectToken] = useState("");
  const [advertisedUrl, setAdvertisedUrl] = useState("");
  const [consistencyMsg, setConsistencyMsg] = useState<string | null>(null);

  const fedQ = useQuery({
    queryKey: ["federation", "status"],
    queryFn: federationApi.federationStatus,
  });

  const pairM = useMutation({
    mutationFn: federationApi.createPairingToken,
    onSuccess: (data) => {
      setPairingToken(data.token);
      setMessage(null);
    },
    onError: (e: Error) => setMessage(e.message),
  });

  const connectM = useMutation({
    mutationFn: () =>
      federationApi.connectToExisting({
        base_url: peerUrl.trim(),
        pairing_token: connectToken.trim(),
        advertised_base_url: advertisedUrl.trim() || null,
      }),
    onSuccess: async () => {
      setConnectToken("");
      await qc.invalidateQueries({ queryKey: ["federation", "status"] });
    },
    onError: (e: Error) => setMessage(e.message),
  });

  const pingM = useMutation({
    mutationFn: (id: number) => federationApi.pingPeer(id),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["federation", "status"] });
    },
    onError: (e: Error) => setMessage(e.message),
  });

  const pullM = useMutation({
    mutationFn: (slug: string) => federationApi.pullTenant(slug),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["federation", "status"] });
    },
    onError: (e: Error) => setMessage(e.message),
  });

  const consM = useMutation({
    mutationFn: (slug: string) =>
      federationApi.consistency(slug, fedQ.data?.peers.length === 1 ? fedQ.data.peers[0].id : undefined),
    onSuccess: (data) => {
      if (data.match) setConsistencyMsg(t("integrations.checksumMatch"));
      else if (data.match === false) setConsistencyMsg(t("integrations.checksumMismatch"));
      else setConsistencyMsg(data.checksum);
    },
    onError: (e: Error) => setMessage(e.message),
  });

  const promoteM = useMutation({
    mutationFn: (slug: string) => federationApi.promoteTenant(slug),
    onSuccess: async (data) => {
      setConsistencyMsg(data.match ? t("integrations.promoteOk") : t("integrations.promoteBlocked"));
      await qc.invalidateQueries({ queryKey: ["federation", "status"] });
    },
    onError: (e: Error) => setMessage(e.message),
  });

  const freezeM = useMutation({
    mutationFn: ({ slug, frozen }: { slug: string; frozen: boolean }) => federationApi.freezeTenant(slug, frozen),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["federation", "status"] });
    },
    onError: (e: Error) => setMessage(e.message),
  });

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

      <Panel title={t("integrations.replicasTitle")}>
        <p style={{ marginTop: 0, fontSize: "var(--text-sm)", color: "var(--color-text-muted)" }}>
          {t("integrations.replicasIntro")}
        </p>
        {fedQ.isLoading ? <p>{t("dcim.common.loading")}</p> : null}
        {fedQ.isError ? <p>{(fedQ.error as Error).message}</p> : null}
        {fedQ.data ? (
          <p style={{ fontSize: "var(--text-sm)" }}>
            {t("integrations.thisInstance")}: <code>{fedQ.data.name}</code>{" "}
            <code>{fedQ.data.instance_uuid}</code>
          </p>
        ) : null}

        <div className={dcimStyles.formRow} style={{ gap: "0.75rem", flexWrap: "wrap" }}>
          <button type="button" onClick={() => pairM.mutate()} disabled={pairM.isPending}>
            {t("integrations.addReplica")}
          </button>
        </div>
        <p style={{ fontSize: "var(--text-sm)", color: "var(--color-text-muted)" }}>
          {t("integrations.addReplicaHint")}
        </p>
        {pairingToken ? (
          <p>
            {t("integrations.pairingToken")}: <code style={{ wordBreak: "break-all" }}>{pairingToken}</code>
          </p>
        ) : null}

        <h3 style={{ fontSize: "var(--text-sm)", margin: "1rem 0 0.5rem" }}>{t("integrations.connectExisting")}</h3>
        <div className={dcimStyles.formRow}>
          <label className={dcimStyles.wideField}>
            {t("integrations.peerBaseUrl")}
            <input
              value={peerUrl}
              onChange={(e) => setPeerUrl(e.target.value)}
              placeholder="http://192.168.1.10:8080"
              autoComplete="off"
            />
          </label>
        </div>
        <div className={dcimStyles.formRow}>
          <label className={dcimStyles.wideField}>
            {t("integrations.pairingToken")}
            <input value={connectToken} onChange={(e) => setConnectToken(e.target.value)} autoComplete="off" />
          </label>
        </div>
        <div className={dcimStyles.formRow}>
          <label className={dcimStyles.wideField}>
            {t("integrations.advertisedUrl")}
            <input value={advertisedUrl} onChange={(e) => setAdvertisedUrl(e.target.value)} autoComplete="off" />
          </label>
        </div>
        <button
          type="button"
          onClick={() => connectM.mutate()}
          disabled={!peerUrl.trim() || !connectToken.trim() || connectM.isPending}
        >
          {t("integrations.connect")}
        </button>

        <h3 style={{ fontSize: "var(--text-sm)", margin: "1rem 0 0.5rem" }}>{t("integrations.replicasTitle")}</h3>
        {fedQ.data?.peers.length ? (
          <ul style={{ margin: 0, paddingLeft: "1.25rem" }}>
            {fedQ.data.peers.map((p) => (
              <li key={p.id}>
                <code>{p.name}</code> — {p.base_url} ({p.status}){" "}
                <button type="button" onClick={() => pingM.mutate(p.id)} disabled={pingM.isPending}>
                  {t("integrations.peerPing")}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ color: "var(--color-text-muted)" }}>{t("integrations.peersEmpty")}</p>
        )}

        <h3 style={{ fontSize: "var(--text-sm)", margin: "1rem 0 0.5rem" }}>{t("integrations.tenantsTitle")}</h3>
        {consistencyMsg ? (
          <p style={{ fontSize: "var(--text-sm)", color: "var(--color-text-muted)" }}>{consistencyMsg}</p>
        ) : null}
        {fedQ.data?.tenants.length ? (
          <ul style={{ margin: 0, paddingLeft: "1.25rem" }}>
            {fedQ.data.tenants.map((ten) => (
              <li key={ten.tenant_id} style={{ marginBottom: "0.5rem" }}>
                <strong>{ten.tenant_name}</strong> ({ten.tenant_slug}) —{" "}
                {ten.is_primary_here ? t("integrations.rolePrimary") : t("integrations.roleReplica")}
                {ten.frozen ? ` · ${t("integrations.frozen")}` : ""}
                <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", marginTop: "0.25rem" }}>
                  <button type="button" onClick={() => consM.mutate(ten.tenant_slug)} disabled={consM.isPending}>
                    {t("integrations.consistency")}
                  </button>
                  <button type="button" onClick={() => freezeM.mutate({ slug: ten.tenant_slug, frozen: !ten.frozen })}>
                    {ten.frozen ? t("integrations.unfreeze") : t("integrations.freeze")}
                  </button>
                  {ten.is_primary_here ? null : (
                    <>
                      <button type="button" onClick={() => pullM.mutate(ten.tenant_slug)} disabled={pullM.isPending}>
                        {t("integrations.pull")}
                      </button>
                      <button type="button" onClick={() => promoteM.mutate(ten.tenant_slug)} disabled={promoteM.isPending}>
                        {t("integrations.promote")}
                      </button>
                    </>
                  )}
                </div>
              </li>
            ))}
          </ul>
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
        <div className={dcimStyles.formRow}>
          <label className={dcimStyles.wideField}>
            {t("integrations.slugLabel")}
            <input value={slugZip} onChange={(e) => setSlugZip(e.target.value)} autoComplete="off" />
          </label>
        </div>
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
        <div className={dcimStyles.formRow}>
          <label className={dcimStyles.wideField}>
            Git URL
            <input
              value={gitUrl}
              onChange={(e) => setGitUrl(e.target.value)}
              placeholder="https://github.com/org/repo.git"
              autoComplete="off"
            />
          </label>
        </div>
        <div className={dcimStyles.formRow}>
          <label>
            {t("integrations.refLabel")}
            <input value={gitRef} onChange={(e) => setGitRef(e.target.value)} autoComplete="off" />
          </label>
        </div>
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
        <div className={dcimStyles.formRow}>
          <label className={dcimStyles.wideField}>
            {t("integrations.slugLabel")}
            <input value={slugGit} onChange={(e) => setSlugGit(e.target.value)} autoComplete="off" />
          </label>
        </div>
        <div className={dcimStyles.formRow}>
          <label className={dcimStyles.wideField}>
            {t("integrations.subpathLabel")}
            <input
              value={subpath}
              onChange={(e) => setSubpath(e.target.value)}
              placeholder="(tom hvis plugin.py ligger i rot)"
              autoComplete="off"
            />
          </label>
        </div>
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
