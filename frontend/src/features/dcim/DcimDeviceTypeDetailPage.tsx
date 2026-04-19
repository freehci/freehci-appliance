import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { deviceTypeResolvedFaIconClass } from "./dcimTypeIcons";
import styles from "./dcim.module.css";

export function DcimDeviceTypeDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const { deviceTypeId } = useParams<{ deviceTypeId: string }>();
  const id = Number(deviceTypeId);
  const [err, setErr] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [faIcon, setFaIcon] = useState("");
  const [deleteOpen, setDeleteOpen] = useState(false);

  const q = useQuery({
    queryKey: ["dcim", "device-types", id],
    queryFn: () => api.getDeviceType(id),
    enabled: Number.isFinite(id) && id > 0,
  });

  const dt = q.data;
  useEffect(() => {
    if (!dt) return;
    setName(dt.name);
    setDescription(dt.description ?? "");
    setFaIcon(dt.fa_icon ?? "");
  }, [dt]);

  const saveM = useMutation({
    mutationFn: () =>
      api.updateDeviceType(id, {
        name: name.trim(),
        description: description.trim() === "" ? null : description.trim(),
        fa_icon: faIcon.trim() === "" ? null : faIcon.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "device-types"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "device-types", id] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const deleteM = useMutation({
    mutationFn: () => api.deleteDeviceType(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dcim", "device-types"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
      void navigate("/dcim/equipment");
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!Number.isFinite(id) || id < 1) {
    return (
      <Panel title={t("dcim.equip.dt.detailTitle")}>
        <p className={styles.err}>{t("dcim.equip.dt.invalidId")}</p>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          {t("dcim.equip.dev.backToList")}
        </Link>
      </Panel>
    );
  }

  if (q.isError) {
    return (
      <Panel title={t("dcim.equip.dt.detailTitle")}>
        <p className={styles.err}>{(q.error as Error).message}</p>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          {t("dcim.equip.dev.backToList")}
        </Link>
      </Panel>
    );
  }

  if (q.isLoading || !dt) {
    return (
      <Panel title={t("dcim.equip.dt.detailTitle")}>
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      </Panel>
    );
  }

  return (
    <>
      <p className={styles.mfrDetailBack}>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          ← {t("dcim.equip.dev.backToList")}
        </Link>
      </p>
      <Panel title={dt.name}>
        {err ? <p className={styles.err}>{err}</p> : null}
        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.mfr.sectionProfile")}</h3>
          <dl className={styles.dlInline}>
            <dt>{t("dcim.equip.dt.slug")}</dt>
            <dd>
              <code>{dt.slug}</code>
            </dd>
          </dl>
          <form
            className={styles.formRow}
            style={{ flexDirection: "column", alignItems: "stretch" }}
            onSubmit={(e) => {
              e.preventDefault();
              saveM.mutate();
            }}
          >
            <label>
              {t("dcim.common.name")}
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </label>
            <label>
              {t("dcim.equip.mfr.description")}
              <textarea
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className={styles.mfrTextarea}
              />
            </label>
            <p className={styles.muted} style={{ marginTop: 0 }}>
              <a
                href="https://fontawesome.com/icons?d=gallery&s=solid&m=free"
                target="_blank"
                rel="noreferrer"
                className={styles.tableLink}
              >
                {t("dcim.equip.dt.faIconHelpLink")}
              </a>
              {" — "}
              {t("dcim.equip.dt.faIconHelpSuffix")}
            </p>
            <div className={styles.formRow} style={{ alignItems: "flex-end", flexWrap: "wrap" }}>
              <label style={{ flex: "1 1 14rem" }}>
                {t("dcim.equip.dt.faIcon")}
                <input
                  value={faIcon}
                  onChange={(e) => setFaIcon(e.target.value)}
                  placeholder={t("dcim.equip.dt.faIconPlaceholder")}
                  spellCheck={false}
                  autoComplete="off"
                />
              </label>
              <div
                className={styles.mfrLogoCell}
                title={t("dcim.equip.dt.faIconPreview")}
                style={{ fontSize: "1.35rem", minWidth: "2rem", justifyContent: "center" }}
              >
                <i className={`fas ${deviceTypeResolvedFaIconClass(dt.slug, faIcon)}`} aria-hidden />
              </div>
            </div>
            <div>
              <button type="submit" className={styles.btn} disabled={saveM.isPending}>
                {saveM.isPending ? "…" : t("dcim.equip.mfr.save")}
              </button>
            </div>
          </form>
        </section>

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.mfr.dangerZone")}</h3>
          <button
            type="button"
            className={`${styles.tableIconBtn} ${styles.tableIconBtnDanger}`.trim()}
            title={t("dcim.common.delete")}
            aria-label={t("dcim.common.delete")}
            disabled={deleteM.isPending}
            onClick={() => setDeleteOpen(true)}
          >
            <i className="fas fa-trash-can" aria-hidden />
          </button>
        </section>
      </Panel>
      <ConfirmModal
        open={deleteOpen}
        onClose={() => {
          if (!deleteM.isPending) setDeleteOpen(false);
        }}
        title={t("dcim.equip.dt.deleteModalTitle", { name: dt.name })}
        message={t("dcim.equip.dt.deleteModalHint")}
        confirmLabel={t("dcim.common.delete")}
        cancelLabel={t("dcim.common.cancel")}
        danger
        pending={deleteM.isPending}
        onConfirm={() => {
          deleteM.mutate(undefined as void, { onSettled: () => setDeleteOpen(false) });
        }}
      />
    </>
  );
}
