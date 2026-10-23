import { useEffect, useRef, type ReactNode, type RefObject } from "react";
import { X } from "lucide-react";

export function ChatDialog({ title, testId, busy, onClose, children, footer, closeOnOutside = true, inactive = false, returnFocusRef }: { title: string; testId: string; busy?: boolean; onClose: () => void; children: ReactNode; footer?: ReactNode; closeOnOutside?: boolean; inactive?: boolean; returnFocusRef?: RefObject<HTMLElement | null> }) {
  const root = useRef<HTMLElement>(null);
  const close = useRef(onClose); close.current = onClose;
  const pending = useRef(busy); pending.current = busy;
  const suspended = useRef(inactive); suspended.current = inactive;
  useEffect(() => {
    const previous = returnFocusRef?.current || document.activeElement as HTMLElement | null;
    root.current?.focus();
    const outside = (event: PointerEvent) => { if (!suspended.current && closeOnOutside && !pending.current && !root.current?.contains(event.target as Node)) close.current(); };
    const key = (event: KeyboardEvent) => {
      if (suspended.current) return;
      if (event.key === "Escape") {
        event.preventDefault(); event.stopImmediatePropagation();
        if (!pending.current) close.current();
        return;
      }
      if (event.key !== "Tab") return;
      const targets = [...(root.current?.querySelectorAll<HTMLElement>('button:not(:disabled), input:not(:disabled), select:not(:disabled), a[href], textarea:not(:disabled)') || [])];
      const first = targets[0], last = targets[targets.length - 1];
      if (!first) { event.preventDefault(); return; }
      const outsideFocus = !root.current?.contains(document.activeElement);
      if (event.shiftKey && (outsideFocus || document.activeElement === first || document.activeElement === root.current)) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && (outsideFocus || document.activeElement === last || document.activeElement === root.current)) { event.preventDefault(); first.focus(); }
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
