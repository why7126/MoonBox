import "../../styles/globals.css";
import "../../styles/tokens.generated.css";
import { Activity, Filter, KanbanSquare, RefreshCw, ShieldCheck } from "lucide-react";
import { moonboxBrandAssets } from "../../shared/brand/moonboxAssets";
import { Button } from "../../shared/ui";

const tokens = [
  ["Background", "#0A0D14", "#F4F6FA"],
  ["Panel", "#131826", "#FFFFFF"],
  ["Raised", "#1A1F2C", "#EEF2F7"],
  ["Accent", "#D8AC55", "#B9832E"],
  ["Text", "#ECEAE4", "#202636"],
];

export function DesignSystemPage() {
  return (
    <main className="ds-preview">
      <header className="ds-preview-header">
        <div>
          <p>MoonBox Ops</p>
          <h1>MoonBox Design System</h1>
        </div>
        <Button>
          <RefreshCw size={15} aria-hidden="true" />
          Sync Tokens
        </Button>
      </header>

      <section className="ds-preview-brand" aria-label="MoonBox 品牌资产">
        <img src={moonboxBrandAssets.logoDarkWide.compact} alt="MoonBox 深色横版 Logo" />
        <img src={moonboxBrandAssets.logoLight.compact} alt="MoonBox 浅色横版 Logo" />
        <img src={moonboxBrandAssets.appIcon.compact} alt="MoonBox 应用图标" />
      </section>

      <section className="ds-preview-grid" aria-label="现代 Ops Token">
        {tokens.map(([name, dark, light]) => (
          <article className="ds-token-card" key={name}>
            <strong>{name}</strong>
            <span>{dark}</span>
            <span>{light}</span>
          </article>
        ))}
      </section>

      <section className="ds-component-demo" aria-label="组件样式样本">
        <article>
          <span><KanbanSquare size={16} aria-hidden="true" /> Requirement Board</span>
          <strong>8</strong>
          <small>active lanes</small>
        </article>
        <article>
          <span><Activity size={16} aria-hidden="true" /> Delivery Pulse</span>
          <strong>96%</strong>
          <small>healthy flow</small>
        </article>
        <article>
          <span><ShieldCheck size={16} aria-hidden="true" /> Risk Control</span>
          <strong>2</strong>
          <small>blocked items</small>
        </article>
        <button className="ds-filter-demo" type="button">
          <Filter size={15} aria-hidden="true" />
          Filters
          <i>3</i>
        </button>
      </section>
    </main>
  );
}
