import { describe, expect, it } from "vitest";
import { catalogProvisionHref } from "./catalogHref";

describe("catalogProvisionHref", () => {
  it("opens deploy with the selected device", () => {
    expect(catalogProvisionHref(12)).toBe("/services?tab=deploy&device=12");
  });
});
