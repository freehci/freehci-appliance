import { describe, expect, it } from "vitest";
import {
  mibCompileErrorHintKeys,
  mibCompileErrorNeedsToggle,
  mibCompileErrorPreview,
} from "./compileErrorHints";

describe("mibCompileErrorHintKeys", () => {
  it("detects Integer64 unknown parents", () => {
    const keys = mibCompileErrorHintKeys("Unknown parents for symbols: Integer64 at MIB X");
    expect(keys).toContain("snmp.compileHint.integer64Imports");
  });

  it("detects OBJECT-TYPE grammar issues", () => {
    const keys = mibCompileErrorHintKeys(
      "Bad grammar near token type OBJECT_TYPE, value OBJECT-TYPE at MIB hpnr, line 887",
    );
    expect(keys).toContain("snmp.compileHint.badGrammarObjectType");
  });

  it("detects no symbol in module", () => {
    const keys = mibCompileErrorHintKeys('no symbol "jnxJsSMS" in module "JUNIPER-JS-SMI" at MIB Y');
    expect(keys).toContain("snmp.compileHint.noSymbolInModule");
  });
});

describe("mibCompileErrorNeedsToggle", () => {
  it("is false for short message without specific hints", () => {
    expect(mibCompileErrorNeedsToggle("failed")).toBe(false);
  });

  it("is true when specific hint matches", () => {
    expect(mibCompileErrorNeedsToggle("Unknown parents for symbols: Integer64")).toBe(true);
  });

  it("is true for long first line", () => {
    const long = "x".repeat(200);
    expect(mibCompileErrorNeedsToggle(long)).toBe(true);
    expect(mibCompileErrorPreview(long).endsWith("…")).toBe(true);
  });
});
