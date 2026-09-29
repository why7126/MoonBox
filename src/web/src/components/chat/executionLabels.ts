import type { ExecutionConfig, ExecutionOption } from "./chatApi";

const AGENT_LABELS: Record<string, string> = {
  codex: "Codex",
};

const MODEL_LABELS: Record<string, string> = {
  "gpt-6-astra": "GPT-6 Astra",
  "gpt-5.6-luna": "GPT-5.6 Luna",
  "gpt-5.6-terra": "GPT-5.6 Terra",
  "gpt-5.6-sol": "GPT-5.6 Sol",
  "gpt-5.5": "GPT-5.5",
};

const REASONING_LABELS: Record<string, string> = {
  xhigh: "XHigh",
  high: "High",
  medium: "Medium",
  low: "Low",
};

function optionDisplayName(options: ExecutionOption[] | undefined, value: string) {
  return options?.find((item) => item.value === value)?.display_name;
}

export function agentDisplayName(value: string, options?: ExecutionOption[]) {
  return optionDisplayName(options, value) || AGENT_LABELS[value] || value;
}

export function modelDisplayName(value: string, options?: ExecutionOption[]) {
  return optionDisplayName(options, value) || MODEL_LABELS[value] || value;
}

export function reasoningDisplayName(value: string, options?: ExecutionOption[]) {
  return optionDisplayName(options, value) || REASONING_LABELS[value] || value;
}

export function executionConfigLabel(config?: ExecutionConfig | null) {
  if (!config) return "";
  return [
    agentDisplayName(config.agent),
    modelDisplayName(config.model),
    reasoningDisplayName(config.reasoning),
  ].filter(Boolean).join(" · ");
}

