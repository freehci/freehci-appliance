import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { NavLink, Outlet, useParams } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { Panel } from "@/components/ui/Panel";
import dcimTabStyles from "@/features/dcim/DcimInnerTabs.module.css";
import { useI18n } from "@/i18n/I18nProvider";
import * as api from "./iamApi";
import { IamUserTabIcon } from "./IamUserTabIcon";
import styles from "./iam.module.css";

function initials(displayName: string | null | undefined, username: string): string {
  const s = (displayName ?? "").trim() || username.trim();
  const parts = s.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) return (parts[0]![0]! + parts[1]![0]!).toUpperCase();
  if (parts.length === 1 && parts[0]!.length >= 2) return parts[0]!.slice(0, 2).toUpperCase();
  return (s.slice(0, 2) || "??").toUpperCase();
}

function tabClass({ isActive }: { isActive: boolean }): string {
  return `${dcimTabStyles.tab} ${isActive ? dcimTabStyles.tabActive : ""}`.trim();
}

export function IamUserDetailLayout() {
  const { t } = useI18n();
  const { userId } = useParams<{ userId: string }>();
  const id = Number(userId);
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement | null>(null);
  const [avatarBust, setAvatarBust] = useState<number>(0);
  const [avatarImgOk, setAvatarImgOk] = useState(true);

  const q = useQuery({
    queryKey: ["iam", "person", id],
    queryFn: () => api.getPerson(id),
    enabled: Number.isFinite(id),
  });

  const person = q.data;
  useEffect(() => {
    setAvatarImgOk(true);
  }, [id, avatarBust, person?.avatar_file]);

  const uploadAvatarM = useMutation({
    mutationFn: (f: File) => api.uploadPersonAvatar(id, f),
    onSuccess: () => {
      setAvatarBust(Date.now());
      void qc.invalidateQueries({ queryKey: ["iam", "person", id] });
      void qc.invalidateQueries({ queryKey: ["iam", "directory"] });
    },
  });

  const deleteAvatarM = useMutation({
    mutationFn: () => api.deletePersonAvatar(id),
    onSuccess: () => {
      setAvatarBust(Date.now());
      void qc.invalidateQueries({ queryKey: ["iam", "person", id] });
      void qc.invalidateQueries({ queryKey: ["iam", "directory"] });
    },
  });
  const title =
    q.isLoading || !person ? t("iam.userDetailLoading") : person.display_name?.trim() || person.username;

  if (!Number.isFinite(id)) {
    return (
      <Panel title={t("iam.invalidId")}>
        <p className={styles.err}>{t("iam.invalidId")}</p>
      </Panel>
    );
  }

  const about = person?.notes?.trim() || "";

  const tabsNav = (
    <nav className={dcimTabStyles.wrap} aria-label={t("iam.userInnerNavAria")}>
      <div className={dcimTabStyles.list} role="tablist">
        <NavLink to="user" className={tabClass} role="tab" end>
          <span className={dcimTabStyles.iconWrap}>
            <IamUserTabIcon name="user" />
          </span>
          <span>{t("iam.userTabUser")}</span>
        </NavLink>
        <NavLink to="login-devices" className={tabClass} role="tab">
          <span className={dcimTabStyles.iconWrap}>
            <IamUserTabIcon name="loginDevices" />
          </span>
          <span>{t("iam.userTabLoginDevices")}</span>
        </NavLink>
        <NavLink to="groups" className={tabClass} role="tab">
          <span className={dcimTabStyles.iconWrap}>
            <IamUserTabIcon name="groups" />
          </span>
          <span>{t("iam.userTabGroups")}</span>
        </NavLink>
        <NavLink to="roles" className={tabClass} role="tab">
          <span className={dcimTabStyles.iconWrap}>
            <IamUserTabIcon name="roles" />
          </span>
          <span>{t("iam.userTabRoles")}</span>
        </NavLink>
        <NavLink to="applications" className={tabClass} role="tab">
          <span className={dcimTabStyles.iconWrap}>
            <IamUserTabIcon name="applications" />
          </span>
          <span>{t("iam.userTabApplications")}</span>
        </NavLink>
        <NavLink to="company" className={tabClass} role="tab">
          <span className={dcimTabStyles.iconWrap}>
            <IamUserTabIcon name="company" />
          </span>
          <span>{t("iam.userTabCompany")}</span>
        </NavLink>
        <NavLink to="log" className={tabClass} role="tab">
          <span className={dcimTabStyles.iconWrap}>
            <IamUserTabIcon name="log" />
          </span>
          <span>{t("iam.userTabLog")}</span>
        </NavLink>
      </div>
    </nav>
  );

  const showUserShell = Number.isFinite(id) && !q.isError && (q.isLoading || !!person);

  return (
    <Panel title={title}>
      {q.isError ? <p className={styles.err}>{(q.error as Error).message}</p> : null}
      {!q.isLoading && !person && !q.isError ? <p className={styles.err}>{t("iam.notFound")}</p> : null}
      {showUserShell ? (
        <div className={styles.userDetailRoot}>
          {tabsNav}
          <div className={styles.userDetailGrid}>
            <aside className={styles.userDetailSidebar}>
              {person ? (
                <>
                  <div className={styles.userDetailAvatarWrap}>
                    <button
                      type="button"
                      className={`${styles.userDetailAvatar} ${styles.userDetailAvatarBtn}`.trim()}
                      title={t("iam.avatarClickToUpload")}
                      onClick={() => fileRef.current?.click()}
                    >
                      {avatarImgOk && person.avatar_file ? (
                        <img
                          className={styles.userDetailAvatarImg}
                          src={api.avatarUrl(person.id, avatarBust || person.avatar_file)}
                          alt={t("iam.avatarAlt")}
                          onError={() => setAvatarImgOk(false)}
                        />
                      ) : null}
                      {!(avatarImgOk && person.avatar_file) ? (
                        <span className={styles.userDetailAvatarInitials} aria-hidden>
                          {initials(person.display_name, person.username)}
                        </span>
                      ) : null}
                      <span className={styles.userDetailAvatarOverlay} aria-hidden>
                        <i className="fas fa-camera" />
                      </span>
                    </button>
                    {person.avatar_file ? (
                      <button
                        type="button"
                        className={styles.userDetailAvatarRemove}
                        title={t("iam.avatarRemove")}
                        aria-label={t("iam.avatarRemove")}
                        disabled={deleteAvatarM.isPending}
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          deleteAvatarM.mutate();
                        }}
                      >
                        <i className="fas fa-trash-can" aria-hidden />
                      </button>
                    ) : null}
                  </div>
                  <input
                    ref={fileRef}
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    style={{ display: "none" }}
                    onChange={(e) => {
                      const f = e.target.files?.[0];
                      e.target.value = "";
                      if (!f) return;
                      uploadAvatarM.mutate(f);
                    }}
                  />
                  <h2 className={styles.userDetailName}>{person.display_name?.trim() || person.username}</h2>
                  {person.email ? (
                    <p className={styles.userDetailMeta}>
                      <a href={`mailto:${person.email}`}>{person.email}</a>
                    </p>
                  ) : null}
                  <p className={styles.userDetailMeta}>{person.username}</p>
                  <h3 className={styles.userDetailAboutTitle}>{t("iam.about")}</h3>
                  <p className={styles.userDetailAbout}>{about || "—"}</p>
                </>
              ) : (
                <p className={styles.userDetailSidebarLoading}>…</p>
              )}
            </aside>
            <div className={styles.userDetailMain}>
              <Outlet />
            </div>
          </div>
        </div>
      ) : null}
    </Panel>
  );
}
