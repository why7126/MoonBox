import { defineConfig } from "orval";

export default defineConfig({
  capture: {
    input: { target: "./openapi.json", filters: { tags: ["Capture"] } },
    output: { target: "./src/api/generated/capture.ts", client: "fetch", mode: "single" },
  },
  governance: {
    input: { target: "./openapi.json", filters: { tags: ["Governance", "Requirement Center", "requirement-center"] } },
    output: { target: "./src/api/generated/governance.ts", client: "fetch", mode: "single" },
  },
  chat: {
    input: { target: "./openapi.json", filters: { tags: ["Chat"] } },
    output: { target: "./src/api/generated/chat.ts", client: "fetch", mode: "single" },
  },
});
