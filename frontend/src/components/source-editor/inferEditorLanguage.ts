/**
 * Monaco language-id fra filnavn. Ukjente endelser → plaintext (trygt for MIB m.m.).
 * HCL brukes for Terraform / OpenTofu (.tf, .tofu, .hcl).
 */
export function inferEditorLanguageFromFilename(filename: string): string {
  const lower = filename.toLowerCase();
  const dot = lower.lastIndexOf(".");
  const ext = dot >= 0 ? lower.slice(dot) : "";

  switch (ext) {
    case ".json":
      return "json";
    case ".yaml":
    case ".yml":
      return "yaml";
    case ".tf":
    case ".tofu":
    case ".hcl":
      return "hcl";
    case ".xml":
      return "xml";
    case ".md":
    case ".markdown":
      return "markdown";
    case ".sh":
      return "shell";
    case ".py":
      return "python";
    case ".mib":
    case ".my":
      return "mib";
    default:
      return "plaintext";
  }
}
