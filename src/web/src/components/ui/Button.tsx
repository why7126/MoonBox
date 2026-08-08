import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
}

export function Button({ children, variant = "primary", ...props }: ButtonProps) {
  return (
    <button className={`mb-button mb-button-${variant}`} {...props}>
      {children}
    </button>
  );
}
