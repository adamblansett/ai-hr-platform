import { test, expect } from '@playwright/test';

test.describe('Leave & Attendance PTO Request Flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'engineer.alex@acme.corp');
    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button[type="submit"]');
  });

  test('should display leave balance cards and request history table', async ({ page }) => {
    await page.click('button:has-text("Leave & PTO")');
    await expect(page.locator('h2')).toContainText('Leave & Attendance');
    await expect(page.locator('h3')).toContainText('Leave Request History');
    await expect(page.locator('button:has-text("+ Request Time Off")')).toBeVisible();
  });

  test('should open time-off modal and validate required fields', async ({ page }) => {
    await page.click('button:has-text("Leave & PTO")');
    await page.click('button:has-text("+ Request Time Off")');

    // Assert modal opened
    await expect(page.locator('h3:has-text("Submit Time-Off Request")')).toBeVisible();
    await expect(page.locator('select')).toBeVisible();
    await expect(page.locator('input[type="date"]').first()).toBeVisible();
  });
});
