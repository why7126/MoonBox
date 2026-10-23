/** Names are display-only; filter values retain their original stable identity. */
type OwnerFields = { owner: string; ownerKey?: string; owner_key?: string | null; owner_display_name?: string | null };

export function normalizeOwner(issue: OwnerFields): { owner: string; ownerKey: string } {
  const raw = (issue.owner_key ?? issue.ownerKey ?? issue.owner ?? "").trim();
  const key = ["null", "None", "未分配"].includes(raw) ? "" : raw;
  const candidate = (issue.owner_display_name ?? issue.owner ?? "").trim();
  const aliases: Record<string, string> = { product: "产品团队", user: "用户反馈", "": "未分配", null: "未分配", None: "未分配" };
  const owner = !key ? "未分配" : !candidate || candidate.startsWith("user_") ? "未知用户" : aliases[candidate] ?? candidate;
  return { owner, ownerKey: key };
}

export function ownerFilterOptions(issues: OwnerFields[]): { value: string; label: string }[] {
  const byKey = new Map(issues.map(issue => { const value = normalizeOwner(issue); return [value.ownerKey, value.owner] as const; }));
  const counts = new Map<string, number>();
  for (const name of byKey.values()) counts.set(name, (counts.get(name) ?? 0) + 1);
  const positions = new Map<string, number>();
  return [...byKey].sort(([a, an], [b, bn]) => an.localeCompare(bn, "zh-Hans-CN") || a.localeCompare(b)).map(([key, name]) => {
    const index = (positions.get(name) ?? 0) + 1;
    positions.set(name, index);
    return { value: key, label: (counts.get(name) ?? 0) > 1 ? `${name}（${index}）` : name };
  });
}
