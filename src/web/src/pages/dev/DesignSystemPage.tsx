import "../../styles/globals.css";
import "../../styles/tokens.generated.css";
import { moonboxBrandAssets } from "../../shared/brand/moonboxAssets";
import { Button } from "../../shared/ui";

const tokens = [
  ["背景", "#0A0C1B", "#F6F7FB"],
  ["面板", "#12142B", "#FFFFFF"],
  ["强调", "#CBA35C", "#B8863E"],
  ["文字", "#E7E8F3", "#232A42"],
];

export function DesignSystemPage() {
  return (
    <main style={{ padding: 32 }}>
      <h1 style={{ color: "var(--mb-heading)", fontFamily: "Noto Serif SC, serif" }}>
        MoonBox Design System
      </h1>
      <section>
        {tokens.map(([name, dark, light]) => (
          <div key={name}>
            <strong>{name}</strong> <span>{dark}</span> <span>{light}</span>
          </div>
        ))}
      </section>
      <section style={{ display: "grid", gap: 16, marginBlock: 32, maxWidth: 720 }}>
        <img src={moonboxBrandAssets.logoLight.compact} alt="MoonBox 白底横版 Logo" />
        <img src={moonboxBrandAssets.logoDarkWide.compact} alt="MoonBox 黑底横版 Logo" />
        <img src={moonboxBrandAssets.logoTransparent.compact} alt="MoonBox 透明背景 Logo" />
        <img src={moonboxBrandAssets.appIcon.compact} alt="MoonBox 应用图标" width={128} height={128} />
      </section>
      <Button>Primary</Button>
    </main>
  );
}
