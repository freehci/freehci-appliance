import type { Monaco } from "@monaco-editor/react";

import { jsonMonarchLanguage } from "./jsonMonarch";
import { mibMonarchLanguage } from "./mibMonarch";

let customLanguagesRegistered = false;

/**
 * Egendefinerte språk (MIB, JSON) + Monaco basic-languages lastes via sideeffekt-imports i SourceCodeEditor.
 */
export function registerEditorLanguages(monaco: Monaco): void {
  if (customLanguagesRegistered) return;
  const known = new Set(monaco.languages.getLanguages().map((l: { id: string }) => l.id));

  if (!known.has("mib")) {
    monaco.languages.register({ id: "mib", extensions: [".mib", ".my", ".txt"], aliases: ["MIB", "SMI"] });
  }
  monaco.languages.setMonarchTokensProvider("mib", mibMonarchLanguage);
  monaco.languages.setLanguageConfiguration("mib", {
    comments: { lineComment: "--" },
    brackets: [
      ["{", "}"],
      ["[", "]"],
      ["(", ")"],
    ],
  });

  if (!known.has("json")) {
    monaco.languages.register({ id: "json", extensions: [".json"], aliases: ["JSON"] });
  }
  monaco.languages.setMonarchTokensProvider("json", jsonMonarchLanguage);

  customLanguagesRegistered = true;
}
