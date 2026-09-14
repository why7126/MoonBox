// Dev-only entry; browser harness supplies explicitly synthetic HTTP responses.
import React from "react";
import { createRoot } from "react-dom/client";
import { RequirementCenterPage } from "../src/pages/catalog/RequirementCenterPage";
import "../src/styles/globals.css";
import "../src/styles/tokens.generated.css";
createRoot(document.getElementById("root")!).render(<RequirementCenterPage />);
