import type { languages } from "monaco-editor";

/**
 * Enkel JSON-utheving uten egen contribution-fil i nyere Monaco-bygg.
 * God nok for visning og senere redigering.
 */
export const jsonMonarchLanguage: languages.IMonarchLanguage = {
  defaultToken: "",
  tokenizer: {
    root: [
      [/[{}[\]]/, "delimiter.bracket"],
      [/"(?:[^"\\]|\\.)*"/, "string"],
      [/\b(?:true|false|null)\b/, "keyword"],
      [/-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/, "number"],
      [/[,:]/, "delimiter"],
      [/\s+/, "white"],
    ],
  },
};
