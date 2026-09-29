import type { ReactNode } from "react";

type HighlightCandidate = { text: string; start: number; end: number; priority: number };
type HighlightPlan = { remaining: string[] };

const MAX_IMPORTANT_HIGHLIGHTS = 2;

const IMPORTANT_FRAGMENT_RULES = [
  { priority: 1, pattern: /(根因未确认|根因不明确|无法[^，。！？!?；;\n]{0,18}|不能[^，。！？!?；;\n]{0,18}|不可用|阻塞[^，。！？!?；;\n]{0,18}|缺少[^，。！？!?；;\n]{0,18})/g },
  { priority: 1, pattern: /(未修改代码或创建 Issue|未(?:修改代码|创建 Issue|定位[^，。！？!?；;\n]{0,18}|发现[^，。！？!?；;\n]{0,18}|完成[^，。！？!?；;\n]{0,18}|执行[^，。！？!?；;\n]{0,18}|通过[^，。！？!?；;\n]{0,18}))/g },
  { priority: 2, pattern: /(已(?:完成|修复|创建|归档|通过)[^，。！？!?；;\n]{0,16})/g },
  { priority: 3, pattern: /(需要(?:补充|确认|处理|修复|创建|检查|复验)[^，。！？!?；;\n]{0,16}|请补充[^，。！？!?；;\n]{0,16})/g },
];

function collectHighlightCandidates(content: string): HighlightCandidate[] {
  const candidates: HighlightCandidate[] = [];
  IMPORTANT_FRAGMENT_RULES.forEach((rule) => {
    rule.pattern.lastIndex = 0;
    let match: RegExpExecArray | null;
    while ((match = rule.pattern.exec(content))) {
      const text = match[0].trim();
      if (text) candidates.push({ text, start: match.index, end: match.index + match[0].length, priority: rule.priority });
      if (match[0].length === 0) rule.pattern.lastIndex++;
    }
  });
  return candidates;
}

function buildHighlightPlan(content: string): HighlightPlan {
  const selected: HighlightCandidate[] = [];
  const candidates = collectHighlightCandidates(content)
    .sort((a, b) => a.priority - b.priority || a.start - b.start || a.text.length - b.text.length);
  for (const candidate of candidates) {
    if (selected.length >= MAX_IMPORTANT_HIGHLIGHTS) break;
    if (selected.some((item) => candidate.start < item.end && item.start < candidate.end)) continue;
    selected.push(candidate);
  }
  return { remaining: selected.sort((a, b) => a.start - b.start).map((item) => item.text) };
}

function highlightText(text: string, keyPrefix: string, plan: HighlightPlan): ReactNode[] {
  const nodes: ReactNode[] = [];
  let rest = text, index = 0;
  while (rest) {
    const matches = plan.remaining
      .map((fragment, remainingIndex) => ({ fragment, remainingIndex, at: rest.indexOf(fragment) }))
      .filter((match) => match.at >= 0)
      .sort((a, b) => a.at - b.at || b.fragment.length - a.fragment.length);
    const match = matches[0];
    if (!match) { nodes.push(rest); break; }
    if (match.at > 0) nodes.push(rest.slice(0, match.at));
    nodes.push(<mark className="chat-important-highlight" key={`${keyPrefix}-${index++}`}>{match.fragment}</mark>);
    rest = rest.slice(match.at + match.fragment.length);
    plan.remaining.splice(match.remainingIndex, 1);
  }
  return nodes;
}
function inline(text: string, plan: HighlightPlan): ReactNode[] {
  return text.split(/(`[^`\n]+`|\*\*[^*\n]+\*\*|(?<!!)\[[^\]\n]+\]\([^\s)]+\))/g).map((part, index) => {
    if (part.startsWith("`")) return <code key={index}>{part.slice(1, -1)}</code>;
    if (part.startsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    const link = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(part);
    if (link) {
      try { const url = new URL(link[2]); if (["https:", "http:"].includes(url.protocol)) return <a key={index} href={url.href} target="_blank" rel="noopener noreferrer">{link[1]}</a>; } catch { /* Unsupported links remain inert text. */ }
    }
    return <span key={index}>{highlightText(part, `text-${index}`, plan)}</span>;
  });
}
function tableCells(line: string): string[] {
  // Protect escaped pipes and pipes inside inline code from column splitting.
  const cells: string[] = []; let cell = "", code = 0;
  const input = line.trim().replace(/^\|/, "").replace(/(?<!\\)\|$/, "");
  for (let i = 0; i < input.length; i++) {
    if (input[i] === "\\" && input[i + 1] === "|") { cell += "|"; i++; continue; }
    if (input[i] === "`") {
      let count = 1; while (input[i + count] === "`") count++;
      code = code === count ? 0 : code || count;
      cell += "`".repeat(count); i += count - 1; continue;
    }
    if (input[i] === "|" && !code) { cells.push(cell.trim()); cell = ""; } else cell += input[i];
  }
  cells.push(cell.trim()); return cells;
}
/** A bounded Markdown subset. HTML and image syntax are always inert text. */
export function SafeMarkdown({ content }: { content: string }) {
  const lines = content.split("\n"), blocks: ReactNode[] = [];
  const highlightPlan = buildHighlightPlan(content);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("```")) {
      const code: string[] = []; const key = i;
      while (++i < lines.length && !lines[i].startsWith("```")) code.push(lines[i]);
      blocks.push(<pre key={key}><code>{code.join("\n")}</code></pre>); continue;
    }
    if (!line.trim()) continue;
    const header = tableCells(line), separator = i + 1 < lines.length ? tableCells(lines[i + 1]) : [];
    if (line.includes("|") && header.length > 1 && separator.length === header.length && separator.every(cell => /^:?-{3,}:?$/.test(cell))) {
      const key = i, rows: string[][] = []; i += 2;
      while (i < lines.length && lines[i].trim() && lines[i].includes("|")) { rows.push(tableCells(lines[i])); i++; }
      i--;
      const align = separator.map(cell => cell.startsWith(":") && cell.endsWith(":") ? "center" as const : cell.endsWith(":") ? "right" as const : "left" as const);
      blocks.push(<div className="chat-table-scroll" role="region" aria-label="消息表格" tabIndex={0} key={key}><table>
        <thead><tr>{header.map((cell, column) => <th scope="col" style={{ textAlign: align[column] }} key={column}>{inline(cell, highlightPlan)}</th>)}</tr></thead>
        <tbody>{rows.map((row, index) => <tr key={index}>{header.map((_, column) => <td style={{ textAlign: align[column] }} key={column}>{inline(row[column] || "", highlightPlan)}</td>)}</tr>)}</tbody>
      </table></div>); continue;
    }
    const heading = /^(#{1,6})\s+(.+)$/.exec(line);
    if (heading) { blocks.push(<h4 key={i}>{inline(heading[2], highlightPlan)}</h4>); continue; }
    if (/^[-*]\s+/.test(line)) {
      const key = i, items: ReactNode[] = [];
      do { items.push(<li key={i}>{inline(lines[i].replace(/^[-*]\s+/, ""), highlightPlan)}</li>); i++; } while (i < lines.length && /^[-*]\s+/.test(lines[i]));
      i--; blocks.push(<ul key={key}>{items}</ul>); continue;
    }
    if (line.startsWith("> ")) blocks.push(<blockquote key={i}>{inline(line.slice(2), highlightPlan)}</blockquote>);
    else blocks.push(<p key={i}>{inline(line, highlightPlan)}</p>);
  }
  return <div className="chat-markdown">{blocks}</div>;
}
