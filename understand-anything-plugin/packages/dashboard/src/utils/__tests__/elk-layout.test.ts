import { describe, it, expect } from "vitest";
import { repairElkInput, type ElkInput } from "../elk-layout";

describe("repairElkInput", () => {
  it("ensures node dimensions when missing", () => {
    const input: ElkInput = {
      id: "root",
      children: [{ id: "a" }, { id: "b", width: 100, height: 50 }] as ElkInput["children"],
      edges: [],
    };
    const { input: out, issues } = repairElkInput(input);
    expect(out.children![0].width).toBeGreaterThan(0);
    expect(out.children![0].height).toBeGreaterThan(0);
    expect(out.children![1]).toEqual({ id: "b", width: 100, height: 50 });
    expect(issues.some((i) => i.level === "auto-corrected" && /dimensions/.test(i.message))).toBe(true);
  });

  it("dedupes duplicate child ids and reports auto-corrected", () => {
    const input: ElkInput = {
      id: "root",
      children: [
        { id: "a", width: 1, height: 1 },
        { id: "a", width: 1, height: 1 },
      ],
      edges: [],
    };
    const { input: out, issues } = repairElkInput(input);
    expect(out.children).toHaveLength(1);
    expect(issues.some((i) => i.level === "auto-corrected" && /duplicate/.test(i.message))).toBe(true);
  });

  it("drops orphan edges referencing nonexistent nodes", () => {
    const input: ElkInput = {
      id: "root",
      children: [{ id: "a", width: 1, height: 1 }],
      edges: [
        { id: "e1", sources: ["a"], targets: ["ghost"] },
      ],
    };
    const { input: out, issues } = repairElkInput(input);
    expect(out.edges).toHaveLength(0);
    expect(issues.some((i) => i.level === "dropped" && /edge/.test(i.message))).toBe(true);
  });

  it("drops children referencing nonexistent parents", () => {
    const input: ElkInput = {
      id: "root",
      children: [
        {
          id: "p",
          width: 100,
          height: 100,
          children: [{ id: "c1", width: 1, height: 1 }],
        },
        { id: "orphan", width: 1, height: 1, parentId: "ghost" } as ElkInput["children"][0] & { parentId: string },
      ],
      edges: [],
    };
    const { input: out, issues } = repairElkInput(input);
    expect(out.children!.find((c) => c.id === "orphan")).toBeUndefined();
    expect(issues.some((i) => i.level === "dropped" && /parent/.test(i.message))).toBe(true);
  });

  it("strict mode throws on any issue", () => {
    const input: ElkInput = {
      id: "root",
      children: [{ id: "a" }] as ElkInput["children"],
      edges: [],
    };
    expect(() => repairElkInput(input, { strict: true })).toThrow(/dimensions/);
  });
});
