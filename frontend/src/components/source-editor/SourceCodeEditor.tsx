import Editor, { type BeforeMount, type OnMount } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import * as monacoApi from "monaco-editor";
import { useCallback, useEffect, useRef } from "react";

import { useTheme } from "@/theme/ThemeProvider";

import "monaco-editor/esm/vs/basic-languages/hcl/hcl.contribution.js";
import "monaco-editor/esm/vs/basic-languages/yaml/yaml.contribution.js";

import { inferEditorLanguageFromFilename } from "./inferEditorLanguage";
import { registerEditorLanguages } from "./registerEditorLanguages";
import styles from "./SourceCodeEditor.module.css";

export type SourceCodeEditorProps = {
  value: string;
  /** Monaco language id; default utledes fra `filename` eller plaintext. */
  language?: string;
  /** Brukes til språkvalg når `language` ikke er satt. */
  filename?: string;
  readOnly?: boolean;
  onChange?: (value: string) => void;
  /** Stabil modell-URI (f.eks. filnavn) — unngår at modeller kolliderer mellom faner. */
  path?: string;
  /** 1-baserte linjenumre (f.eks. diagnostikk). */
  problemLineNumbers?: ReadonlySet<number>;
  /** 1-basert linje som skal rulleres til og markeres. */
  focusedLine?: number | null;
  className?: string;
};

function themeId(appTheme: "dark" | "light"): string {
  return appTheme === "dark" ? "vs-dark" : "light";
}

export function SourceCodeEditor({
  value,
  language: languageProp,
  filename = "",
  readOnly = true,
  onChange,
  path,
  problemLineNumbers,
  focusedLine,
  className,
}: SourceCodeEditorProps) {
  const { theme: appTheme } = useTheme();
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<typeof monacoApi | null>(null);
  const decoIdsRef = useRef<string[]>([]);

  const language =
    languageProp ?? (filename ? inferEditorLanguageFromFilename(filename) : "plaintext");

  const modelPath = path ?? filename ?? "inmemory://model.txt";

  const handleBeforeMount: BeforeMount = useCallback((monaco) => {
    registerEditorLanguages(monaco);
  }, []);

  const handleMount: OnMount = useCallback((ed, monaco) => {
    editorRef.current = ed;
    monacoRef.current = monaco;
  }, []);

  useEffect(() => {
    const monaco = monacoRef.current;
    const ed = editorRef.current;
    if (!monaco || !ed) return;
    monaco.editor.setTheme(themeId(appTheme));
  }, [appTheme]);

  useEffect(() => {
    const monaco = monacoRef.current;
    const ed = editorRef.current;
    if (!monaco || !ed) return;
    const model = ed.getModel();
    if (!model) return;

    const mark = new Map<number, "problem" | "focused" | "both">();
    if (problemLineNumbers) {
      for (const n of problemLineNumbers) {
        if (n >= 1) mark.set(n, "problem");
      }
    }
    if (focusedLine != null && focusedLine >= 1) {
      const prev = mark.get(focusedLine);
      mark.set(focusedLine, prev === "problem" ? "both" : "focused");
    }

    const decorations: editor.IModelDeltaDecoration[] = [];
    for (const [line, kind] of mark) {
      const lastCol = Math.max(1, model.getLineMaxColumn(line));
      let className: string;
      if (kind === "both") className = styles.lineProblemFocused;
      else if (kind === "problem") className = styles.lineProblem;
      else className = styles.lineFocused;
      decorations.push({
        range: new monaco.Range(line, 1, line, lastCol),
        options: { isWholeLine: true, className },
      });
    }

    decoIdsRef.current = ed.deltaDecorations(decoIdsRef.current, decorations);
  }, [problemLineNumbers, focusedLine, value]);

  useEffect(() => {
    if (focusedLine == null || focusedLine < 1) return;
    const ed = editorRef.current;
    if (!ed) return;
    ed.revealLineInCenter(focusedLine);
  }, [focusedLine]);

  useEffect(
    () => () => {
      const ed = editorRef.current;
      if (ed) decoIdsRef.current = ed.deltaDecorations(decoIdsRef.current, []);
    },
    [],
  );

  return (
    <div className={`${styles.wrap}${className ? ` ${className}` : ""}`}>
      <Editor
        height="100%"
        width="100%"
        path={modelPath}
        defaultLanguage={language}
        language={language}
        value={value}
        theme={themeId(appTheme)}
        beforeMount={handleBeforeMount}
        onMount={handleMount}
        onChange={readOnly ? undefined : (v) => onChange?.(v ?? "")}
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 13,
          wordWrap: "on",
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
          folding: true,
          renderLineHighlight: "line",
          padding: { top: 8, bottom: 8 },
          unicodeHighlight: { ambiguousCharacters: false },
        }}
      />
    </div>
  );
}
