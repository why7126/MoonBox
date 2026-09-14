export const captureLevels = {
  requirement: [
    ["P0", "P0", "最高优先级：阻塞当前核心目标，需立即安排"],
    ["P1", "P1", "高优先级：对核心目标有明显价值，优先纳入近期迭代"],
    ["P2", "P2", "常规优先级：按计划推进，可结合容量安排"],
    ["P3", "P3", "低优先级：体验优化或探索项，资源允许时安排"],
  ],
  bug: [
    ["blocker", "致命", "系统或核心流程完全不可用，无可行绕行方案"],
    ["critical", "严重", "核心功能严重受损，或存在重大数据、安全影响"],
    ["high", "高", "重要功能异常，明显影响使用，但存在绕行方案"],
    ["medium", "中", "局部功能异常，核心流程仍可完成"],
    ["low", "低", "轻微视觉、文案或体验问题，基本不影响功能"],
  ],
} as const;

export function CaptureGrading({ type, value, disabled, onChange }: {
  type: "requirement" | "bug"; value: string; disabled: boolean; onChange: (value: string) => void;
}) {
  const levels = captureLevels[type];
  const selected = levels.find(level => level[0] === value);
  return <fieldset className="rc-capture-fieldset">
    <legend>{type === "bug" ? "严重性" : "优先级"} <b aria-hidden="true">*</b></legend>
    <div className={`rc-capture-segmented priority${type === "bug" ? " severity" : ""}`} role="group" aria-label={type === "bug" ? "Capture 严重性" : "Capture 优先级"} aria-required="true">
      {levels.map(([id, label]) => <div className="rc-level-option" key={id}>
        <button type="button" disabled={disabled} data-priority={id} aria-pressed={value === id}
          className={value === id ? "selected" : ""} aria-describedby={value === id ? "capture-level-description" : undefined}
          onClick={() => onChange(id)}>{label}</button>
      </div>)}
    </div>
    <p id="capture-level-description" className="rc-level-description" aria-live="polite">{selected?.[1]}：{selected?.[2]}</p>
  </fieldset>;
}
