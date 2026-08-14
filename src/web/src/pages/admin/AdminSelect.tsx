import { ChevronDown } from "lucide-react";
import { KeyboardEvent, useEffect, useId, useRef, useState, type CSSProperties } from "react";
import { createPortal } from "react-dom";

export type AdminSelectOption<T extends string | number = string> = {
  value: T;
  label: string;
};

type AdminSelectProps<T extends string | number = string> = {
  id?: string;
  ariaLabel: string;
  value: T;
  options: AdminSelectOption<T>[];
  onChange: (value: T) => void;
  className?: string;
  portal?: boolean;
};

export function AdminSelect<T extends string | number = string>({ id, ariaLabel, value, options, onChange, className, portal = false }: AdminSelectProps<T>) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(() => Math.max(0, options.findIndex((option) => option.value === value)));
  const [portalStyle, setPortalStyle] = useState<CSSProperties | null>(null);
  const rootRef = useRef<HTMLDivElement | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);
  const listboxId = useId();
  const selected = options.find((option) => option.value === value) ?? options[0];

  useEffect(() => {
    const close = (event: MouseEvent) => {
      const target = event.target as Node;
      if (!rootRef.current?.contains(target) && !menuRef.current?.contains(target)) setIsOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  useEffect(() => {
    if (!isOpen || !portal) {
      setPortalStyle(null);
      return;
    }

    const updatePlacement = () => {
      const trigger = rootRef.current?.querySelector(".admin-select-trigger");
      if (!trigger) return;
      const rect = trigger.getBoundingClientRect();
      const rootStyle = rootRef.current ? window.getComputedStyle(rootRef.current) : null;
      const menuHeight = menuRef.current?.getBoundingClientRect().height ?? Math.min(220, Math.max(38, options.length * 38 + 10));
      const gap = 4;
      const belowTop = rect.bottom + gap;
      const aboveTop = Math.max(gap, rect.top - menuHeight - gap);
      const hasBelowSpace = window.innerHeight - belowTop >= menuHeight;
      const nextStyle = {
        position: "fixed",
        top: Math.round(hasBelowSpace ? belowTop : aboveTop),
        left: Math.round(rect.left),
        width: Math.round(rect.width),
        zIndex: 120,
        "--admin-panel-bg": rootStyle?.getPropertyValue("--admin-panel-bg"),
        "--admin-panel-strong-bg": rootStyle?.getPropertyValue("--admin-panel-strong-bg"),
        "--admin-border-strong": rootStyle?.getPropertyValue("--admin-border-strong"),
        "--admin-text": rootStyle?.getPropertyValue("--admin-text"),
        "--admin-hover-bg": rootStyle?.getPropertyValue("--admin-hover-bg"),
      } as CSSProperties;
      setPortalStyle(nextStyle);
    };

    updatePlacement();
    window.addEventListener("resize", updatePlacement);
    window.addEventListener("scroll", updatePlacement, true);
    return () => {
      window.removeEventListener("resize", updatePlacement);
      window.removeEventListener("scroll", updatePlacement, true);
    };
  }, [isOpen, options.length, portal]);

  useEffect(() => {
    if (!isOpen) return;
    setActiveIndex(Math.max(0, options.findIndex((option) => option.value === value)));
  }, [isOpen, options, value]);

  const commit = (index: number) => {
    const option = options[index];
    if (!option) return;
    onChange(option.value);
    setIsOpen(false);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    if (event.key === "Escape") {
      setIsOpen(false);
      return;
    }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if (!isOpen) {
        setIsOpen(true);
        return;
      }
      setActiveIndex((index) => {
        const delta = event.key === "ArrowDown" ? 1 : -1;
        return (index + delta + options.length) % options.length;
      });
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (isOpen) commit(activeIndex);
      else setIsOpen(true);
    }
  };

  const menu = (
    <div
      className={`admin-select-menu${portal ? " admin-select-menu-portal" : ""}`}
      id={listboxId}
      role="listbox"
      aria-label={ariaLabel}
      ref={menuRef}
      style={portalStyle ?? undefined}
    >
      {options.map((option, index) => (
        <button
          type="button"
          role="option"
          aria-selected={option.value === value}
          className={index === activeIndex ? "active" : ""}
          key={String(option.value)}
          onMouseEnter={() => setActiveIndex(index)}
          onClick={() => commit(index)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );

  return (
    <div className={`admin-select${className ? ` ${className}` : ""}`} ref={rootRef}>
      <button
        id={id}
        type="button"
        className="admin-select-trigger"
        aria-label={ariaLabel}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-controls={listboxId}
        onClick={() => setIsOpen((value) => !value)}
        onKeyDown={onKeyDown}
      >
        <span>{selected?.label ?? ""}</span>
        <ChevronDown size={14} aria-hidden="true" />
      </button>
      {isOpen && (portal ? createPortal(menu, document.body) : menu)}
    </div>
  );
}
