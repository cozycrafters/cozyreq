import { test, expect } from "vitest";
import { render } from "@solidjs/testing-library";
import App from "./App";

test("increments value", async () => {
  const { getByRole } = render(() => <App />);
  const headline = getByRole("heading");
  expect(headline).toHaveTextContent("Welcome to Tauri + Solid");
});
