import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Panel } from "@/components/ui/Panel";
import { useI18n } from "@/i18n/I18nProvider";
import { ApiError } from "@/lib/api";
import * as api from "./dcimApi";
import { deviceModelListThumbSrc } from "./modelImages";
import styles from "./dcim.module.css";

export function DcimDeviceModelDetailPage() {
  const { t } = useI18n();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const { deviceModelId } = useParams<{ deviceModelId: string }>();
  const [searchParams] = useSearchParams();
  const isNew = deviceModelId === "new";
  const id = isNew ? NaN : Number(deviceModelId);
  const fileFrontRef = useRef<HTMLInputElement | null>(null);
  const fileBackRef = useRef<HTMLInputElement | null>(null);
  const fileProductRef = useRef<HTMLInputElement | null>(null);

  const [err, setErr] = useState<string | null>(null);
  const [mfr, setMfr] = useState("");
  const [dt, setDt] = useState("");
  const [name, setName] = useState("");
  const [u, setU] = useState("1");
  const [snmp, setSnmp] = useState("");
  const [imgFront, setImgFront] = useState("");
  const [imgBack, setImgBack] = useState("");
  const [imgProduct, setImgProduct] = useState("");
  const [imgVersion, setImgVersion] = useState("");
  const [deleteOpen, setDeleteOpen] = useState(false);

  const manufacturersQ = useQuery({ queryKey: ["dcim", "manufacturers"], queryFn: api.listManufacturers });
  const deviceTypesQ = useQuery({ queryKey: ["dcim", "device-types"], queryFn: api.listDeviceTypes });

  const modelQ = useQuery({
    queryKey: ["dcim", "device-models", id],
    queryFn: () => api.getDeviceModel(id),
    enabled: !isNew && Number.isFinite(id) && id > 0,
  });

  const mo = modelQ.data;

  useEffect(() => {
    const raw = searchParams.get("prefillManufacturer");
    if (raw == null || raw === "") return;
    const n = Number(raw);
    if (!Number.isFinite(n) || n < 1) return;
    setMfr(String(n));
  }, [searchParams]);

  useEffect(() => {
    if (!mo) return;
    setName(mo.name);
    setU(String(mo.u_height));
    setMfr(mo.manufacturer_id != null ? String(mo.manufacturer_id) : "");
    setDt(mo.device_type_id != null ? String(mo.device_type_id) : "");
    setSnmp(mo.snmp_sys_object_id_prefix ?? "");
    setImgFront(mo.image_front_url ?? "");
    setImgBack(mo.image_back_url ?? "");
    setImgProduct(mo.image_product_url ?? "");
  }, [mo]);

  const createM = useMutation({
    mutationFn: () => {
      const uN = Number(u);
      const u_height = Number.isFinite(uN) && uN >= 0 ? uN : 1;
      const snmpT = snmp.trim();
      return api.createDeviceModel({
        name: name.trim(),
        u_height,
        manufacturer_id: mfr === "" ? null : Number(mfr),
        device_type_id: dt === "" ? null : Number(dt),
        image_front_url: imgFront.trim() === "" ? null : imgFront.trim(),
        image_back_url: imgBack.trim() === "" ? null : imgBack.trim(),
        image_product_url: imgProduct.trim() === "" ? null : imgProduct.trim(),
        snmp_sys_object_id_prefix: snmpT === "" ? null : snmpT,
      });
    },
    onSuccess: async (created) => {
      const ff = fileFrontRef.current?.files?.[0];
      const fb = fileBackRef.current?.files?.[0];
      const fp = fileProductRef.current?.files?.[0];
      try {
        if (ff) await api.uploadDeviceModelImageFront(created.id, ff);
        if (fb) await api.uploadDeviceModelImageBack(created.id, fb);
        if (fp) await api.uploadDeviceModelImageProduct(created.id, fp);
        setErr(null);
      } catch (e) {
        setErr(e instanceof ApiError ? e.message : (e as Error).message);
      }
      if (fileFrontRef.current) fileFrontRef.current.value = "";
      if (fileBackRef.current) fileBackRef.current.value = "";
      if (fileProductRef.current) fileProductRef.current.value = "";
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models"] });
      void navigate(`/dcim/equipment/device-models/${created.id}`, { replace: true });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const saveM = useMutation({
    mutationFn: () => {
      const uN = Number(u);
      const u_height = Number.isFinite(uN) && uN >= 0 ? uN : 1;
      const snmpT = snmp.trim();
      return api.updateDeviceModel(id, {
        name: name.trim(),
        u_height,
        manufacturer_id: mfr === "" ? null : Number(mfr),
        device_type_id: dt === "" ? null : Number(dt),
        image_front_url: imgFront.trim() === "" ? null : imgFront.trim(),
        image_back_url: imgBack.trim() === "" ? null : imgBack.trim(),
        image_product_url: imgProduct.trim() === "" ? null : imgProduct.trim(),
        snmp_sys_object_id_prefix: snmpT === "" ? null : snmpT,
      });
    },
    onSuccess: async () => {
      const ff = fileFrontRef.current?.files?.[0];
      const fb = fileBackRef.current?.files?.[0];
      const fp = fileProductRef.current?.files?.[0];
      try {
        if (ff) await api.uploadDeviceModelImageFront(id, ff);
        if (fb) await api.uploadDeviceModelImageBack(id, fb);
        if (fp) await api.uploadDeviceModelImageProduct(id, fp);
        setErr(null);
      } catch (e) {
        setErr(e instanceof ApiError ? e.message : (e as Error).message);
      }
      if (fileFrontRef.current) fileFrontRef.current.value = "";
      if (fileBackRef.current) fileBackRef.current.value = "";
      if (fileProductRef.current) fileProductRef.current.value = "";
      setImgVersion(String(Date.now()));
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models", id] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const deleteM = useMutation({
    mutationFn: () => api.deleteDeviceModel(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models"] });
      void qc.invalidateQueries({ queryKey: ["dcim", "devices"] });
      void navigate("/dcim/equipment");
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  const removeFrontM = useMutation({
    mutationFn: () => api.deleteDeviceModelImageFront(id),
    onSuccess: () => {
      setErr(null);
      setImgVersion(String(Date.now()));
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models", id] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const removeBackM = useMutation({
    mutationFn: () => api.deleteDeviceModelImageBack(id),
    onSuccess: () => {
      setErr(null);
      setImgVersion(String(Date.now()));
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models", id] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });
  const removeProductM = useMutation({
    mutationFn: () => api.deleteDeviceModelImageProduct(id),
    onSuccess: () => {
      setErr(null);
      setImgVersion(String(Date.now()));
      void qc.invalidateQueries({ queryKey: ["dcim", "device-models", id] });
    },
    onError: (e: Error) => setErr(e instanceof ApiError ? e.message : e.message),
  });

  if (!isNew && (!Number.isFinite(id) || id < 1)) {
    return (
      <Panel title={t("dcim.equip.dm.detailTitle")}>
        <p className={styles.err}>{t("dcim.equip.dm.invalidId")}</p>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          {t("dcim.equip.dev.backToList")}
        </Link>
      </Panel>
    );
  }

  if (!isNew && modelQ.isError) {
    return (
      <Panel title={t("dcim.equip.dm.detailTitle")}>
        <p className={styles.err}>{(modelQ.error as Error).message}</p>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          {t("dcim.equip.dev.backToList")}
        </Link>
      </Panel>
    );
  }

  if (!isNew && (modelQ.isLoading || !mo)) {
    return (
      <Panel title={t("dcim.equip.dm.detailTitle")}>
        <p className={styles.muted}>{t("dcim.common.loading")}</p>
      </Panel>
    );
  }

  const thumbSrc = !isNew && mo ? deviceModelListThumbSrc(mo, imgVersion) : null;

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    if (isNew) {
      if (!name.trim()) {
        setErr(t("dcim.equip.dm.modelName") + " —");
        return;
      }
      createM.mutate();
      return;
    }
    saveM.mutate();
  };

  const busy = createM.isPending || saveM.isPending;

  return (
    <>
      <p className={styles.mfrDetailBack}>
        <Link to="/dcim/equipment" className={styles.tableLink}>
          ← {t("dcim.equip.dev.backToList")}
        </Link>
      </p>
      <Panel title={isNew ? t("dcim.equip.dm.newPageTitle") : mo!.name}>
        {err ? <p className={styles.err}>{err}</p> : null}
        {!isNew && mo ? (
          <div className={styles.mfrLogoPreview} style={{ marginBottom: "var(--space-3)" }}>
            {thumbSrc ? (
              <img src={thumbSrc} alt="" className={styles.mfrLogoLarge} />
            ) : (
              <p className={styles.muted}>{t("dcim.equip.dm.noThumb")}</p>
            )}
          </div>
        ) : null}

        <form className={styles.formRow} style={{ flexDirection: "column", alignItems: "stretch" }} onSubmit={submit}>
          <label>
            {t("dcim.equip.dm.mfr")}
            <select value={mfr} onChange={(e) => setMfr(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {(manufacturersQ.data ?? []).map((x) => (
                <option key={x.id} value={String(x.id)}>
                  {x.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.dm.dt")}
            <select value={dt} onChange={(e) => setDt(e.target.value)}>
              <option value="">{t("dcim.common.none")}</option>
              {(deviceTypesQ.data ?? []).map((d) => (
                <option key={d.id} value={String(d.id)}>
                  {d.name} ({d.slug})
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("dcim.equip.dm.modelName")}
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <label>
            {t("dcim.equip.dm.u")}
            <input type="number" min={0} max={64} value={u} onChange={(e) => setU(e.target.value)} />
          </label>
          <label title={t("dcim.equip.dm.snmpOidPrefixHint")}>
            {t("dcim.equip.dm.snmpOidPrefix")}
            <input value={snmp} onChange={(e) => setSnmp(e.target.value)} placeholder="1.3.6.1.4.1.…" spellCheck={false} />
          </label>
          <label>
            {t("dcim.equip.dm.imageFront")}
            <input type="url" value={imgFront} onChange={(e) => setImgFront(e.target.value)} placeholder="https://" />
          </label>
          <label>
            {t("dcim.equip.dm.imageBack")}
            <input type="url" value={imgBack} onChange={(e) => setImgBack(e.target.value)} placeholder="https://" />
          </label>
          <label>
            {t("dcim.equip.dm.imageProduct")}
            <input
              type="url"
              value={imgProduct}
              onChange={(e) => setImgProduct(e.target.value)}
              placeholder="https://"
              title={t("dcim.equip.dm.imageProductHint")}
            />
          </label>
          <label>
            {t("dcim.equip.dm.imageFrontFile")}
            <input ref={fileFrontRef} type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" />
          </label>
          <label>
            {t("dcim.equip.dm.imageBackFile")}
            <input ref={fileBackRef} type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" />
          </label>
          <label>
            {t("dcim.equip.dm.imageProductFile")}
            <input
              ref={fileProductRef}
              type="file"
              accept="image/png,image/jpeg,image/webp,image/svg+xml"
              title={t("dcim.equip.dm.imageProductHint")}
            />
          </label>
          <p className={styles.muted} style={{ marginTop: 0 }}>
            {t("dcim.equip.dm.uHintZero")}
          </p>
          <div>
            <button type="submit" className={styles.btn} disabled={busy}>
              {busy ? "…" : isNew ? t("dcim.equip.dm.create") : t("dcim.equip.dm.editSave")}
            </button>
          </div>
        </form>

        {!isNew && mo ? (
          <section className={styles.mfrDetailSection} style={{ marginTop: "var(--space-4)" }}>
            <h3 className={styles.mfrDetailSectionTitle}>{t("dcim.equip.dm.removeUploadedImages")}</h3>
            <div className={styles.mfrLogoActions}>
              <button
                type="button"
                className={styles.btnMuted}
                disabled={!mo.has_image_front_file || removeFrontM.isPending}
                onClick={() => removeFrontM.mutate()}
              >
                {t("dcim.equip.dm.removeImageFront")}
              </button>
              <button
                type="button"
                className={styles.btnMuted}
                disabled={!mo.has_image_back_file || removeBackM.isPending}
                onClick={() => removeBackM.mutate()}
              >
                {t("dcim.equip.dm.removeImageBack")}
              </button>
              <button
                type="button"
                className={styles.btnMuted}
                disabled={!mo.has_image_product_file || removeProductM.isPending}
                onClick={() => removeProductM.mutate()}
              >
                {t("dcim.equip.dm.removeImageProduct")}
              </button>
            </div>
          </section>
        ) : null}

        {!isNew ? (
          <section className={styles.mfrDetailSection} style={{ marginTop: "var(--space-4)" }}>
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
        ) : null}
      </Panel>
      {!isNew && mo ? (
        <ConfirmModal
          open={deleteOpen}
          onClose={() => {
            if (!deleteM.isPending) setDeleteOpen(false);
          }}
          title={t("ui.confirmTitle")}
          message={t("dcim.equip.dm.deleteModelConfirm", { name: mo.name })}
          confirmLabel={t("dcim.common.delete")}
          cancelLabel={t("dcim.common.cancel")}
          danger
          pending={deleteM.isPending}
          onConfirm={() => {
            deleteM.mutate(undefined as void, { onSettled: () => setDeleteOpen(false) });
          }}
        />
      ) : null}
    </>
  );
}
