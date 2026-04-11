import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { MessageKey } from "./messages/en";
import { en } from "./messages/en";
import { nb } from "./messages/nb";

export type Locale = "nb" | "en";

const STORAGE_KEY = "freehci.locale";

const dictionaries: Record<Locale, Record<MessageKey, string>> = {
  en,
  nb,
};

type I18nContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: MessageKey, vars?: Record<string, string>) => string;
};

const I18nContext = createContext<I18nContextValue | null>(null);

function detectInitialLocale(): Locale {
  try {
    const s = localStorage.getItem(STORAGE_KEY);
    if (s === "en" || s === "nb") return s;
  } catch {
    /* ignore */
  }
  if (typeof navigator !== "undefined") {
    const lang = navigator.language.toLowerCase();
    if (lang.startsWith("nb") || lang.startsWith("no")) return "nb";
  }
  return "en";
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(detectInitialLocale);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, locale);
    } catch {
      /* ignore */
    }
    document.documentElement.lang = locale === "nb" ? "nb-NO" : "en";
  }, [locale]);

  const t = useCallback(
    (key: MessageKey, vars?: Record<string, string>): string => {
      let s = dictionaries[locale][key] ?? en[key] ?? key;
      if (vars) {
        for (const [vk, vv] of Object.entries(vars)) {
          s = s.split(`{${vk}}`).join(vv);
        }
      }
      return s;
    },
    [locale],
  );

  const value = useMemo<I18nContextValue>(
    () => ({ locale, setLocale, t }),
    [locale, setLocale, t],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
