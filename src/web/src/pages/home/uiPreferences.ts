export type UiTheme = "dark" | "light";

type UiPreferences = {
  theme: UiTheme;
};

const STORAGE_KEY = "moonbox.ui.preferences";
export const UI_PREFERENCES_EVENT = "moonbox.ui.preferences.changed";

const defaultPreferences: UiPreferences = {
  theme: "dark",
};

export function readUiPreferences(): UiPreferences {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultPreferences;
    const parsed = JSON.parse(raw) as Partial<UiPreferences>;
    return {
      theme: parsed.theme === "light" ? "light" : "dark",
    };
  } catch {
    return defaultPreferences;
  }
}

export function saveUiTheme(theme: UiTheme) {
  const preferences = { ...readUiPreferences(), theme };
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
  window.dispatchEvent(new CustomEvent(UI_PREFERENCES_EVENT, { detail: preferences }));
}
