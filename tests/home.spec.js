const { test, expect } = require("@playwright/test");

test.describe("Role-Playing Video Game guide", () => {
  test("desktop homepage renders SEO metadata and starter path interactions", async ({ page }) => {
    await page.goto("/");

    await expect(page).toHaveTitle(/Role-Playing Video Game Guide/i);
    await expect(page.locator("h1")).toHaveText("Role-Playing Video Game");
    await expect(page.locator('meta[name="description"]')).toHaveAttribute(
      "content",
      /character progression, choice, exploration/i
    );
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", "https://role-playingvideogame.lol/");
    await expect(page.locator('link[rel="manifest"]')).toHaveAttribute("href", "site.webmanifest");
    await expect(page.locator('link[rel="icon"]').first()).toHaveAttribute("href", "assets/brand/favicon.png");
    await expect(page.locator('meta[property="og:site_name"]')).toHaveAttribute("content", "Quest Atlas");
    await expect(page.locator('meta[name="twitter:image:alt"]')).toHaveAttribute(
      "content",
      /Quest Atlas editorial cover/i
    );

    await page.getByRole("link", { name: "Explore the Guide" }).click();
    await expect(page.locator("#what-is")).toBeInViewport();

    await page.getByRole("tab", { name: "Tactics and consequences" }).click();
    await expect(page.locator("[data-path-output-kicker]")).toHaveText("Systems-first entry");
    await expect(page.locator("[data-path-output-title]")).toContainText("planning");

    await page.getByRole("tab", { name: "Shared world and routine" }).click();
    await expect(page.locator("[data-path-output-kicker]")).toHaveText("Routine-first entry");
    await expect(page.locator("[data-path-output-body]")).toContainText("guilds");

    const imagesLoaded = await page.evaluate(() =>
      Array.from(document.images).every((image) => image.complete && image.naturalWidth > 0)
    );
    expect(imagesLoaded).toBe(true);

    await expect(page.locator("details")).toHaveCount(4);
  });

  test("mobile layout remains within viewport and keeps sections reachable", async ({ browser }) => {
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 },
      isMobile: true
    });
    const page = await context.newPage();

    await page.goto("/");

    await expect(page.locator("h1")).toBeVisible();
    await page.getByRole("link", { name: "Read the FAQ" }).click();
    await expect(page.locator("#faq")).toBeInViewport();

    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(1);

    await expect(page.locator(".hero-facts div")).toHaveCount(4);
    await context.close();
  });
});
