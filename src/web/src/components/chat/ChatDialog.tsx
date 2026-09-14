import { useEffect, useRef, type ReactNode } from "react";
import { X } from "lucide-react";

export function ChatDialog({ title, testId, busy, onClose, children, footer }: { title: string; testId: string; busy?: boolean; onClose: () => void; children: ReactNode; footer?: ReactNode }) {
  const root = useRef<HTMLElement>(null);
  const close = useRef(onClose); close.current = onClose;
  const pending = useRef(busy); pending.current = busy;
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    root.current?.focus();
    const outside = (event: PointerEvent) => { if (!pending.current && !root.current?.contains(event.target as Node)) close.current(); };
    const key = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !pending.current) { event.preventDefault(); close.current(); }
      if (event.key !== "Tab") return;
      const targets = [...(root.current?.querySelectorAll<HTMLElement>('button:not(:disabled), input:not(:disabled), select:not(:disabled), a[href], textarea:not(:disabled)') || [])];
      const first = targets[0], last = targets[targets.length - 1];
      if (!first) { event.preventDefault(); return; }
      if (event.shiftKey && (document.activeElement === first || document.activeElement === root.current)) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && (document.activeElement === last || document.activeElement === root.current)) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener("pointerdown", outside, true); document.addEventListener("keydown", key, true);
    return () => { document.removeEventListener("pointerdown", outside, true); document.removeEventListener("keydown", key, true); if (previous?.isConnected) previous.focus(); };
  }, []);
  return <div className="chat-dialog-backdrop"><section ref={root} role="dialog" aria-modal="true" aria-label={title} tabIndex={-1} className="chat-dialog" data-testid={testId}>
    <header><h2>{title}</h2><button type="button" data-testid="chat-modal-close" aria-label={`关闭${title}`} disabled={busy} onClick={onClose}><X size={16} /></button></header>
    <div className="chat-dialog-body">{children}</div>
    {footer && <footer>{footer}</footer>}
  </section></div>;
}
