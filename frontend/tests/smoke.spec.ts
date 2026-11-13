import { test, expect } from "@playwright/test";
test("homepage navigation renders the real course catalog", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Build your future")).toBeVisible();
  await page.getByRole("link", { name: "Courses" }).click();
  await expect(page.getByRole("heading", { name: "Learn programming from first principles" })).toBeVisible();
  await expect(page.getByText("Python").first()).toBeVisible();
  await page.getByLabel("Search courses").fill("C Programming");
  await expect(page.getByText("C Programming")).toBeVisible();
  await page.getByText("C Programming").click();
  await expect(page).toHaveURL(/\/courses\/c-programming$/);
});
