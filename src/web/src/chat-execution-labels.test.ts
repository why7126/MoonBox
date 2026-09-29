import { expect, it } from "vitest";
import { agentDisplayName, executionConfigLabel, modelDisplayName, reasoningDisplayName } from "./components/chat/executionLabels";

it("normalizes chat execution display names while preserving raw values elsewhere", () => {
  expect(agentDisplayName("codex")).toBe("Codex");
  expect(modelDisplayName("gpt-6-astra")).toBe("GPT-6 Astra");
  expect(modelDisplayName("gpt-5.6-luna")).toBe("GPT-5.6 Luna");
  expect(modelDisplayName("gpt-5.6-terra")).toBe("GPT-5.6 Terra");
  expect(modelDisplayName("gpt-5.6-sol")).toBe("GPT-5.6 Sol");
  expect(modelDisplayName("gpt-5.5")).toBe("GPT-5.5");
  expect(reasoningDisplayName("xhigh")).toBe("XHigh");
  expect(reasoningDisplayName("high")).toBe("High");
  expect(reasoningDisplayName("medium")).toBe("Medium");
  expect(reasoningDisplayName("low")).toBe("Low");
  expect(executionConfigLabel({ agent: "codex", model: "gpt-6-astra", reasoning: "xhigh" })).toBe("Codex · GPT-6 Astra · XHigh");
});

