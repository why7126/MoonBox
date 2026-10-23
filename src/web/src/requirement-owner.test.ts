import { describe, expect, it } from "vitest";
import { normalizeOwner, ownerFilterOptions } from "./pages/catalog/requirementOwner";

describe("负责人安全显示与身份筛选", () => {
  it.each([["user_missing", "未知用户"], ["", "未分配"], ["null", "未分配"], ["product", "产品团队"], ["user", "用户反馈"], ["历史团队", "历史团队"]])("兼容旧响应 %s", (owner, expected) => {
    expect(normalizeOwner({ owner }).owner).toBe(expected);
  });
  it("显式展示字段优先且不会回退展示内部身份", () => {
    expect(normalizeOwner({ owner: "user_one", owner_key: "user_one", owner_display_name: "昵称" })).toEqual({ owner: "昵称", ownerKey: "user_one" });
    expect(normalizeOwner({ owner: "user_one", owner_display_name: " " }).owner).toBe("未知用户");
  });
  it("同名不同键保持独立，刷新排序稳定且标签不泄漏键", () => {
    const issues = [{ owner: "同名", owner_key: "user_b" }, { owner: "同名", owner_key: "user_a" }, { owner: "同名", owner_key: "user_b" }];
    const options=ownerFilterOptions(issues);
    expect(options).toEqual([{ value: "user_a", label: "同名（1）" }, { value: "user_b", label: "同名（2）" }]);
    expect(ownerFilterOptions([...issues].reverse())).toEqual(options);
    expect(ownerFilterOptions([{owner:"user_a"},{owner:"user_b"}]).map(o=>o.label)).toEqual(["未知用户（1）","未知用户（2）"]);
  });
});
