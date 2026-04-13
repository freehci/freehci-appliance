import type { languages } from "monaco-editor";

/** SMI v1/v2-nøkkelord og vanlige konstruksjoner for MIB-visning i Monaco. */
export const mibMonarchLanguage: languages.IMonarchLanguage = {
  ignoreCase: true,
  defaultToken: "",
  tokenizer: {
    root: [
      [/--.*$/, "comment"],
      [/"([^"\\]|\\.)*"/, "string"],
      [
        /\b(?:DEFINITIONS|BEGIN|END|IMPORTS|FROM|SEQUENCE|OF|CHOICE|OPTIONAL|INTEGER|OBJECT-TYPE|MODULE-IDENTITY|OBJECT-IDENTITY|OBJECT\s+IDENTITY|OBJECT\s+GROUP|NOTIFICATION-TYPE|TEXTUAL-CONVENTION|MODULE-COMPLIANCE|AGENT-CAPABILITIES|MAX-ACCESS|MIN-ACCESS|SYNTAX|STATUS|ACCESS|DESCRIPTION|REVISION|ORGANIZATION|CONTACT-INFO|LAST-UPDATED|AUGMENTS|INDEX|DEFVAL|UNITS|REFERENCE|NOTIFICATION-GROUP|TRAP-TYPE|ENTERPRISE|VARIABLES|Opaque|::=)\b/,
        "keyword",
      ],
      [/\{[^}\n]{0,400}\}/, "type"],
    ],
  },
};
