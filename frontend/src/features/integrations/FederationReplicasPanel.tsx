import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Panel } from "@/components/ui/Panel";
import dcimStyles from "@/features/dcim/dcim.module.css";
import * as federationApi from "@/features/integrations/federationApi";
import { useI18n } from "@/i18n/I18nProvider";

export function FederationReplicasPanel() {
  const { t } = useI18n();
  const qc = useQueryClient();
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

  return (
    <Panel title={t("integrations.replicasTitle")}>
      <p style={{ marginTop: 0, fontSize: "var(--text-sm)", color: "var(--color-text-muted)" }}>
        {t("integrations.replicasIntro")}
      </p>
      {message ? (
        <p style={{ color: "var(--color-text-muted)", fontSize: "var(--text-sm)" }}>{message}</p>
      ) : null}
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
  );
}
