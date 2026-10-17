import { useEffect } from "react";
import type { UiTheme } from "../../pages/home/uiPreferences";

const WORKBENCH_ROOT_BACKGROUND: Record<UiTheme, string> = {
  dark: "#0A0D14",
  light: "#F4F6FA",
};

export function useWorkbenchRootBackground(theme: UiTheme) {
  useEffect(() => {
    const targets = [document.documentElement, document.body, document.getElementById("root")].filter(
      (target): target is HTMLElement => Boolean(target),
    );
    const previous = targets.map(target => ({
      target,
      backgroundColor: target.style.backgroundColor,
    }));
    const backgroundColor = WORKBENCH_ROOT_BACKGROUND[theme];
    targets.forEach(target => {
      target.style.backgroundColor = backgroundColor;
    });
    return () => {
      previous.forEach(({ target, backgroundColor }) => {
        target.style.backgroundColor = backgroundColor;
      });
    };
  }, [theme]);
}
