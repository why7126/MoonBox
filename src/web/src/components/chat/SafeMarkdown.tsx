import type { ReactNode } from "react";
function inline(text: string): ReactNode[] {
  return text.split(/(`[^`\n]+`|\*\*[^*\n]+\*\*|(?<!!)\[[^\]\n]+\]\([^\s)]+\))/g).map((part, index) => {
    if (part.startsWith("`")) return <code key={index}>{part.slice(1, -1)}</code>;
    if (part.startsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    const link = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(part);
    if (link) {
      try { const url = new URL(link[2]); if (["https:", "http:"].includes(url.protocol)) return <a key={index} href={url.href} target="_blank" rel="noopener noreferrer">{link[1]}</a>; } catch { /* Unsupported links remain inert text. */ }
    }
    return part;
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
        <thead><tr>{header.map((cell, column) => <th scope="col" style={{ textAlign: align[column] }} key={column}>{inline(cell)}</th>)}</tr></thead>
        <tbody>{rows.map((row, index) => <tr key={index}>{header.map((_, column) => <td style={{ textAlign: align[column] }} key={column}>{inline(row[column] || "")}</td>)}</tr>)}</tbody>
      </table></div>); continue;
    }
    const heading = /^(#{1,6})\s+(.+)$/.exec(line);
    if (heading) { blocks.push(<h4 key={i}>{inline(heading[2])}</h4>); continue; }
    if (/^[-*]\s+/.test(line)) {
      const key = i, items: ReactNode[] = [];
      do { items.push(<li key={i}>{inline(lines[i].replace(/^[-*]\s+/, ""))}</li>); i++; } while (i < lines.length && /^[-*]\s+/.test(lines[i]));
      i--; blocks.push(<ul key={key}>{items}</ul>); continue;
    }
    if (line.startsWith("> ")) blocks.push(<blockquote key={i}>{inline(line.slice(2))}</blockquote>);
    else blocks.push(<p key={i}>{inline(line)}</p>);
  }
  return <div className="chat-markdown">{blocks}</div>;
}
