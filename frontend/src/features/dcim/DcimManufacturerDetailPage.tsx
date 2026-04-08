import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import styles from "./dcim.module.css";

export function DcimManufacturerDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const { manufacturerId } = useParams<{ manufacturerId: string }>();
  const id = Number(manufacturerId);
  const fileRef = useRef<HTMLInputElement>(null);
  const hydrated = useRef(false);

  const [err, setErr] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [logoVersion, setLogoVersion] = useState("");

  const detailQ = useQuery({
    queryKey: ["dcim", "manufacturers", id],
    queryFn: () => api.getManufacturer(id),
    enabled: Number.isFinite(id) && id > 0,
  });

  useEffect(() => {
    hydrated.current = false;
  }, [id]);

  useEffect(() => {
    const d = detailQ.data;
    if (!d || hydrated.current) return;
    setName(d.name);
    setDescription(d.description ?? "");
    setWebsiteUrl(d.website_url ?? "");
    if (d.has_logo) setLogoVersion(String(Date.now()));
    hydrated.current = true;
  }, [detailQ.data]);

  const saveMu = useMutation({
    mutationFn: () =>
      api.updateManufacturer(id, {
        name: name.trim(),
        description: description.trim() === "" ? null : description.trim(),
        website_url: websiteUrl.trim() === "" ? null : websiteUrl.trim(),
      }),
    onSuccess: () => {
      setErr(null);
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers", id] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const uploadMu = useMutation({
    mutationFn: (file: File) => api.uploadManufacturerLogo(id, file),
    onSuccess: () => {
      setErr(null);
      setLogoVersion(String(Date.now()));
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers", id] });
      if (fileRef.current) fileRef.current.value = "";
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const removeLogoMu = useMutation({
    mutationFn: () => api.deleteManufacturerLogo(id),
    onSuccess: () => {
      setErr(null);
      setLogoVersion("");
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers", id] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const deleteMu = useMutation({
    mutationFn: () => api.deleteManufacturer(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dcim", "manufacturers"] });
      void navigate("/dcim/equipment");
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!Number.isFinite(id) || id < 1) {
    return (
      <Panel title={t("dcim.equip.mfr.detailTitle")}>
        <p className={styles.err}>{t("dcim.equip.mfr.invalidId")}</p>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          {t("dcim.equip.mfr.backToList")}
        </Link>
      </Panel>
    );
  }

  if (detailQ.isError) {
    return (
      <Panel title={t("dcim.equip.mfr.detailTitle")}>
        <p className={styles.err}>{(detailQ.error as Error).message}</p>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          {t("dcim.equip.mfr.backToList")}
        </Link>
      </Panel>
    );
  }

  if (detailQ.isLoading || !detailQ.data) {
    return (
      <Panel title={t("dcim.equip.mfr.detailTitle")}>
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      </Panel>
    );
  }

  const d = detailQ.data;

  return (
    <>
      <p className={styles.mfrDetailBack}>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          ← {t("dcim.equip.mfr.backToList")}
        </Link>
        {" · "}
        <Link to={`/dcim/equipment?prefillManufacturer=${id}`} className={styles.tableLink}>
          {t("dcim.equip.mfr.addModel")}
        </Link>
      </p>

      <Panel title={d.name}>
        {err ? <p className={styles.err}>{err}</p> : null}

        <div className={styles.mfrDetailGrid}>
          <section className={styles.mfrDetailSection}>
            <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.mfr.sectionProfile")}</h3>
            <form
              className={styles.formRow}
              style={{ flexDirection: "column", alignItems: "stretch" }}
              onSubmit={(e) => {
                e.preventDefault();
                saveMu.mutate();
              }}
            >
              <label>
                {t("dcim.common.name")}
                <input value={name} onChange={(e) => setName(e.target.value)} required />
              </label>
              <label>
                {t("dcim.equip.mfr.description")}
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  className={styles.mfrTextarea}
                />
              </label>
              <label>
                {t("dcim.equip.mfr.website")}
                <input
                  type="url"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  placeholder="https://"
                />
              </label>
              <div>
                <button type="submit" className={styles.btn} disabled={saveMu.isPending}>
                  {saveMu.isPending ? "…" : t("dcim.equip.mfr.save")}
                </button>
              </div>
            </form>
          </section>

          <section className={styles.mfrDetailSection}>
            <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.mfr.sectionLogo")}</h3>
            {d.has_logo ? (
              <div className={styles.mfrLogoPreview}>
                <img
                  src={api.manufacturerLogoUrl(id, logoVersion)}
                  alt=""
                  className={styles.mfrLogoLarge}
                />
              </div>
            ) : (
              <p className={styles.muted}>{t("dcim.equip.mfr.noLogo")}</p>
            )}
            <div className={styles.mfrLogoActions}>
              <input
                ref={fileRef}
                type="file"
                accept="image/png,image/jpeg,image/webp,image/svg+xml"
                className={styles.srOnly}
                tabIndex={-1}
              />
              <button
                type="button"
                className={styles.btn}
                disabled={uploadMu.isPending}
                onClick={() => fileRef.current?.click()}
              >
                {t("dcim.equip.mfr.chooseFile")}
              </button>
              <button
                type="button"
                className={styles.btn}
                disabled={uploadMu.isPending}
                onClick={() => {
                  const f = fileRef.current?.files?.[0];
                  if (f) uploadMu.mutate(f);
                }}
              >
                {uploadMu.isPending ? "…" : t("dcim.equip.mfr.uploadLogo")}
              </button>
              {d.has_logo ? (
                <button
                  type="button"
                  className={styles.btnDanger}
                  disabled={removeLogoMu.isPending}
                  onClick={() => removeLogoMu.mutate()}
                >
                  {removeLogoMu.isPending ? "…" : t("dcim.equip.mfr.removeLogo")}
                </button>
              ) : null}
            </div>
            <p className={styles.muted} style={{ fontSize: "0.65rem", marginTop: "var(--space-2)" }}>
              {t("dcim.equip.mfr.logoHint")}
            </p>
          </section>
        </div>

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.dm.title")}</h3>
          {d.device_models.length === 0 ? (
            <p className={styles.muted}>{t("dcim.equip.mfr.noModels")}</p>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>{t("dcim.common.id")}</th>
                  <th>{t("dcim.common.name")}</th>
                  <th>{t("dcim.equip.dm.u")}</th>
                </tr>
              </thead>
              <tbody>
                {d.device_models.map((m) => (
                  <tr key={m.id}>
                    <td>{m.id}</td>
                    <td>{m.name}</td>
                    <td>{m.u_height}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <section className={styles.mfrDetailSection}>
          <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.mfr.dangerZone")}</h3>
          <button
            type="button"
            className={styles.btnDanger}
            disabled={deleteMu.isPending}
            onClick={() => {
              if (window.confirm(t("dcim.equip.mfr.deleteConfirm"))) deleteMu.mutate();
            }}
          >
            {deleteMu.isPending ? "…" : t("dcim.common.delete")}
          </button>
        </section>
      </Panel>
    </>
  );
}
