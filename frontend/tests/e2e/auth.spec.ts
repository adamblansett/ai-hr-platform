import { test, expect } from '@playwright/test';

test.describe('Authentication & Navigation Flows', () => {
  test('should render login page with branded elements', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('ai-hr-platform');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toContainText('Sign In');
  });

  test('should authenticate demo user and display personalized dashboard', async ({ page }) => {
    await page.goto('/');
    
    // Fill demo employee credentials
    await page.fill('input[type="email"]', 'engineer.alex@acme.corp');
    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button[type="submit"]');

    // Assert dashboard elements
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('nav')).toContainText('Alex Chen');
    await expect(page.locator('h2')).toContainText('Welcome back, Alex!');
  });

  test('should allow user to sign out and clear session', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'engineer.alex@acme.corp');
    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button[type="submit"]');

    await expect(page.locator('button:has-text("Sign Out")')).toBeVisible();
    await page.click('button:has-text("Sign Out")');

    // Should return to login
    await expect(page.locator('h1')).toContainText('ai-hr-platform');
  });
});
