import { useQuery } from "@tanstack/react-query";
import { Panel } from "@/components/ui/Panel";
import dcimStyles from "@/features/dcim/dcim.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import * as systemApi from "./systemApi";

function fmtDate(v: string | null | undefined): string {
  if (!v) return "-";
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return v;
  return d.toLocaleString();
}

function boolText(v: boolean, yes: string, no: string): string {
  return v ? yes : no;
}

export function SystemStatusPage() {
  const { t } = useI18n();
  const q = useQuery({
    queryKey: ["system", "status"],
    queryFn: () => systemApi.systemStatus(),
    refetchInterval: 15_000,
  });

  const status = q.data;
  const updateCheck = status?.update_check;
  const updater = status?.updater_status;
  const logText = (updater?.log_tail ?? []).join("\n");

  return (
    <Panel title={t("system.statusTitle")}>
      <p className={dcimStyles.muted}>{t("system.statusIntro")}</p>
      {q.isError ? <p className={dcimStyles.err}>{(q.error as Error).message}</p> : null}

      <div style={{ display: "flex", gap: "var(--space-2)", flexWrap: "wrap", marginBottom: "var(--space-3)" }}>
        <button type="button" className={dcimStyles.btnMuted} onClick={() => void q.refetch()} disabled={q.isFetching}>
          {q.isFetching ? t("system.statusRefreshing") : t("system.statusRefresh")}
        </button>
      </div>

      <table className={dcimStyles.table} style={{ marginBottom: "var(--space-3)" }}>
        <tbody>
          <tr>
            <th>{t("system.statusLocalVersion")}</th>
            <td>{updateCheck?.local_version ?? "-"}</td>
          </tr>
          <tr>
            <th>{t("system.statusRemoteVersion")}</th>
            <td>{updateCheck?.remote_version ?? "-"}</td>
          </tr>
          <tr>
            <th>{t("system.statusUpdateAvailable")}</th>
            <td>
              {updateCheck
                ? boolText(updateCheck.update_available, t("system.statusYes"), t("system.statusNo"))
                : "-"}
            </td>
          </tr>
          {updateCheck?.remote_error ? (
            <tr>
              <th>{t("system.statusVersionError")}</th>
              <td className={dcimStyles.err}>{updateCheck.remote_error}</td>
            </tr>
          ) : null}
          <tr>
            <th>{t("system.statusUpdaterService")}</th>
            <td>
              {status
                ? boolText(status.updater_available, t("system.statusAvailable"), t("system.statusUnavailable"))
                : "-"}
            </td>
          </tr>
          {status?.updater_error ? (
            <tr>
              <th>{t("system.statusUpdaterError")}</th>
              <td className={dcimStyles.err}>{status.updater_error}</td>
            </tr>
          ) : null}
          <tr>
            <th>{t("system.statusUpdaterRunning")}</th>
            <td>{updater ? boolText(updater.running, t("system.statusYes"), t("system.statusNo")) : "-"}</td>
          </tr>
          <tr>
            <th>{t("system.statusJobId")}</th>
            <td>{updater?.job_id ?? "-"}</td>
          </tr>
          <tr>
            <th>{t("system.statusStartedAt")}</th>
            <td>{fmtDate(updater?.started_at)}</td>
          </tr>
          <tr>
            <th>{t("system.statusFinishedAt")}</th>
            <td>{fmtDate(updater?.finished_at)}</td>
          </tr>
          <tr>
            <th>{t("system.statusExitCode")}</th>
            <td>{updater?.exit_code ?? "-"}</td>
          </tr>
          <tr>
            <th>{t("system.statusDetail")}</th>
            <td>{updater?.detail ?? "-"}</td>
          </tr>
        </tbody>
      </table>

      <h2 style={{ fontSize: "var(--text-sm)", margin: "0 0 var(--space-2)" }}>{t("system.statusLog")}</h2>
      <pre
        style={{
          margin: 0,
          padding: "0.75rem",
          border: "1px solid var(--shell-border)",
          borderRadius: "var(--radius-sm)",
          maxHeight: "28rem",
          overflow: "auto",
          background: "var(--color-bg)",
          whiteSpace: "pre-wrap",
          fontFamily:
            'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
          fontSize: "0.8rem",
          lineHeight: 1.35,
        }}
      >
        {logText || t("system.statusNoLog")}
      </pre>
    </Panel>
  );
}
