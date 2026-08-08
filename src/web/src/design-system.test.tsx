import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DesignSystemPage } from "./pages/dev/DesignSystemPage";

describe("DesignSystemPage", () => {
  it("renders MoonBox design system preview", () => {
    render(<DesignSystemPage />);

    expect(screen.getByText("MoonBox Design System")).toBeTruthy();
  });
});
