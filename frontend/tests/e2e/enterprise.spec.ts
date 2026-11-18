import { test, expect } from '@playwright/test';

test.describe('Enterprise Suite (v1.1 & v1.2) E2E Flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'engineer.alex@acme.corp');
    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button[type="submit"]');
    await expect(page.locator('nav')).toBeVisible();
  });

  test('should navigate to Compensation & Equity view and render vesting metrics', async ({ page }) => {
    await page.click('button:has-text("Compensation & Equity")');
    await expect(page.locator('text=Annual Base Salary')).toBeVisible();
    await expect(page.locator('text=Total Vested Equity')).toBeVisible();
    await expect(page.locator('text=Equity Grants & Vesting Schedule')).toBeVisible();
  });

  test('should navigate to Global & Holidays view and toggle country calendars', async ({ page }) => {
    await page.click('button:has-text("Global & Holidays")');
    await expect(page.locator('text=Global Statutory Public Holidays')).toBeVisible();
    await expect(page.locator('button:has-text("United Kingdom")')).toBeVisible();
    await page.click('button:has-text("United Kingdom")');
    await expect(page.locator('text=Multilingual Policy RAG Assistant')).toBeVisible();
  });

  test('should navigate to Compliance & Audit view and display SOC 2 criteria', async ({ page }) => {
    await page.click('button:has-text("Compliance & Audit")');
    await expect(page.locator('text=SOC 2 Type II Trust Services Criteria Status')).toBeVisible();
    await expect(page.locator('text=Audit Ready (100% Passing)')).toBeVisible();
    await expect(page.locator('text=AI Flight-Risk & Retention Calibration')).toBeVisible();
    await expect(page.locator('text=GDPR & CCPA Data Subject Access Request (DSAR)')).toBeVisible();
  });
});
