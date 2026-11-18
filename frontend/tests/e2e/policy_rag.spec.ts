import { test, expect } from '@playwright/test';

test.describe('Policy AI Assistant & RAG Q&A Flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'engineer.alex@acme.corp');
    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button[type="submit"]');
  });

  test('should render Policy AI Assistant view with input form', async ({ page }) => {
    await page.click('button:has-text("Policy AI Assistant")');
    await expect(page.locator('h2')).toContainText('HR Policy & Compliance AI Assistant');
    await expect(page.locator('input[placeholder*="PTO request"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toContainText('Ask AI');
  });

  test('should submit query and render grounded answer with citations', async ({ page }) => {
    await page.click('button:has-text("Policy AI Assistant")');
    const input = page.locator('input[placeholder*="PTO request"]');
    await input.fill('What is the core working hours policy?');
    await page.click('button:has-text("Ask AI")');

    // Wait for response card
    await expect(page.locator('h3:has-text("Answer")')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('h4:has-text("Cited Policy Sources")')).toBeVisible();
  });
});
