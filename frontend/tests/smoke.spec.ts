import { test, expect } from "@playwright/test";
test("homepage navigation renders", async ({ page }) => { await page.goto("/"); await expect(page.getByText("Build your future")).toBeVisible(); await page.getByRole("link", { name: "Courses" }).click(); await expect(page.getByRole("heading", { name: "Learn by building" })).toBeVisible(); });
