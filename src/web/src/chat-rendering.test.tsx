import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it } from "vitest";
import { SafeMarkdown } from "./components/chat/SafeMarkdown";
import { DiffView } from "./components/chat/DiffView";
afterEach(cleanup);
it("renders supported Markdown without active HTML, images or unsafe protocols", () => {
  render(<SafeMarkdown content={'# 标题\n**粗体** `代码`\n[安全](https://example.com) [危险](javascript:alert)\n<img src=x onerror=alert(1)>\n![图片](https://example.com/image.png)\n```html\n<script>alert(1)</script>\n```'} />);
  expect(document.querySelector('img,script')).toBeNull();
  expect(document.querySelector('strong')?.textContent).toBe('粗体');
  expect(screen.getByRole('link',{name:'安全'}).getAttribute('rel')).toBe('noopener noreferrer');
  expect(document.querySelector('a[href^="javascript"]')).toBeNull();
});
it("distinguishes turn/cumulative changes and metadata-only files", () => {
  render(<DiffView diff={{available:true,files:[{path:'image.bin',status:'added',reason:'二进制文件',after_size:12,workspace_status:'untracked'},{path:'stale.txt',status:'modified',patch:'-old\n+new',workspace_status:'mismatch'}],cumulative_files:[{path:'new.txt',previous_path:'old.txt',status:'renamed',patch:''}]}} />);
  expect(screen.getByText('本轮执行快照')).toBeTruthy();
  expect(screen.getByText('新增（未跟踪）')).toBeTruthy();
  expect(screen.getByText('当前工作区：未跟踪')).toBeTruthy();
  expect(screen.getByText('快照内容与当前磁盘内容不一致，页面展示的是执行快照。')).toBeTruthy();
  expect(screen.getByText(/二进制文件；仅展示文件元数据/)).toBeTruthy();
  fireEvent.change(screen.getByLabelText('Diff 比较范围'),{target:{value:'cumulative'}});
  expect(screen.getByText('原路径：old.txt')).toBeTruthy();
  expect(screen.queryByText('image.bin')).toBeNull();
});
it("renders safe tables with alignment, escaped pipes, inline code and missing cells", () => {
  render(<SafeMarkdown content={'| 名称 | 状态 |\n| :--- | ---: |\n| **任务** | `a|b` |\n| a\\|b | [危险](javascript:alert) |\n| 缺失 |\n\n后续正文'} />);
  expect(screen.getByRole('table')).toBeTruthy();
  expect(screen.getAllByRole('columnheader')).toHaveLength(2);
  expect(screen.getAllByRole('cell')).toHaveLength(6);
  expect(screen.getByText('a|b', {selector:'code'})).toBeTruthy();
  expect(screen.getAllByRole('columnheader')[1].style.textAlign).toBe('right');
  expect(document.querySelector('a[href^="javascript"]')).toBeNull();
  expect(screen.getByText('后续正文')).toBeTruthy();
});
it("keeps pipe text and fenced tables as text and HTML in cells inert", () => {
  render(<SafeMarkdown content={'普通 | 文字\n不是表头\n```\n| a | b |\n| --- | --- |\n```\n| a | b |\n| --- | --- |\n| <img src=x onerror=alert(1)> | <script>bad</script> |'} />);
  expect(screen.getAllByRole('table')).toHaveLength(1);
  expect(document.querySelector('img,script')).toBeNull();
});
