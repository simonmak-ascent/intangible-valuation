import { describe, it, expect } from "vitest";
import { createElement } from "react";
import { render } from "@testing-library/react";
import { CalculatorForm, fieldKind } from "@/components/valuation/CalculatorForm";
import { CATALOG } from "@/lib/valuation/catalog";
import type { MethodParameter } from "@/lib/valuation/types";

/**
 * A `string` parameter used to fall through to `<input type="number">`, and the browser's
 * number-input sanitisation rejects anything non-numeric — so the standard could never be set to
 * "IAS36" from the site, the value was never sent, and the calculation silently ran as ASC 350
 * with the caller's value-in-use inputs discarded. These assertions make that path fail closed.
 */

const param = (over: Partial<MethodParameter>): MethodParameter => ({
  name: "x",
  type: "number",
  required: true,
  description: "d",
  ...over,
});

describe("fieldKind", () => {
  it("renders a string parameter as text, never as a number input", () => {
    expect(fieldKind(param({ type: "string" }))).toBe("text");
  });

  it("renders a string parameter with options as a select", () => {
    expect(
      fieldKind(param({ type: "string", options: [{ label: "A", value: "a" }] }))
    ).toBe("select");
  });

  it("keeps the numeric types on the number input", () => {
    expect(fieldKind(param({ type: "number" }))).toBe("number");
    expect(fieldKind(param({ type: "integer" }))).toBe("number");
  });

  it("handles the remaining types explicitly", () => {
    expect(fieldKind(param({ type: "boolean" }))).toBe("boolean");
    expect(fieldKind(param({ type: "number[]" }))).toBe("number-array");
    expect(fieldKind(param({ type: "json" }))).toBe("json");
  });

  it("gives every string parameter in the catalogue a non-number control", () => {
    // The defect was not one entry but a class: no string parameter in the catalogue reached a
    // control that could hold its value.
    const strings = CATALOG.flatMap((method) =>
      method.parameters.filter((p) => p.type === "string").map((p) => ({ method: method.slug, p }))
    );

    expect(strings.length).toBeGreaterThan(0);
    for (const { method, p } of strings) {
      const kind = fieldKind(p);
      expect(["text", "select"], `${method}.${p.name}`).toContain(kind);
    }
  });

  it("lets the impairment entries express IAS 36 as a fixed choice", () => {
    const goodwill = CATALOG.find((m) => m.slug === "goodwill-impairment-test");
    const standard = goodwill?.parameters.find((p) => p.name === "standard");

    expect(standard?.type).toBe("string");
    expect(fieldKind(standard as MethodParameter)).toBe("select");
    expect(standard?.options?.map((o) => o.value)).toEqual(["ASC350", "IAS36"]);
    // And the IAS 36 inputs are offered alongside it.
    expect(goodwill?.parameters.map((p) => p.name)).toEqual(
      expect.arrayContaining(["value_in_use", "costs_to_sell"])
    );
  });

  it("renders the control fieldKind chose, not a fallthrough number input", () => {
    // The defect lived in the JSX, so the assertion has to render it. `fieldKind` alone is not
    // enough: deleting the `kind === "text"` branch below would leave that helper untouched and the
    // suite green while a string parameter fell through to `<input type="number">`.
    const { container } = render(
      createElement(CalculatorForm, {
        methodSlug: "probe",
        methodName: "Probe",
        parameters: [
          { name: "label", type: "string", required: true, description: "free text" },
          {
            name: "standard",
            type: "string",
            required: false,
            description: "pick one",
            options: [
              { label: "ASC 350 (US GAAP)", value: "ASC350" },
              { label: "IAS 36 (IFRS)", value: "IAS36" },
            ],
          },
        ],
        onCalculate: async () => ({
          value: 0,
          method: "probe",
          formula_reference: "",
          steps: [],
          assumptions: [],
          inputs: {},
        }),
      })
    );

    expect(container.querySelector('input[placeholder="free text"]')?.getAttribute("type")).toBe("text");
    expect(container.querySelector('select option[value="IAS36"]')).not.toBeNull();
    expect(container.querySelectorAll('input[type="number"]').length).toBe(0);
  });
});
