import { useEffect, useState } from "react";
import { readUiPreferences, saveUiTheme, UI_PREFERENCES_EVENT, type UiTheme } from "../../pages/home/uiPreferences";
export function useWorkbenchTheme() {
  const [theme, setTheme] = useState<UiTheme>(() => readUiPreferences().theme);
  useEffect(() => {
    const sync = () => setTheme(readUiPreferences().theme);
    window.addEventListener(UI_PREFERENCES_EVENT, sync); window.addEventListener("storage", sync);
    return () => { window.removeEventListener(UI_PREFERENCES_EVENT, sync); window.removeEventListener("storage", sync); };
  }, []);
  return [theme, saveUiTheme] as const;
}
