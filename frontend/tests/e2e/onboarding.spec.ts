import { test, expect } from '@playwright/test';

test.describe('Employee Onboarding Checklist Flows', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'newhire.elena@acme.corp');
    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button[type="submit"]');
    await expect(page.locator('nav')).toBeVisible();
  });

  test('should display onboarding checklist and progress percentage', async ({ page }) => {
    await page.click('button:has-text("Onboarding")');
    await expect(page.locator('h2')).toContainText('Onboarding Progress');
    await expect(page.locator('h3')).toContainText('Required Tasks');
    
    // Checkboxes should exist
    const checkboxes = page.locator('input[type="checkbox"]');
    await expect(checkboxes.first()).toBeVisible();
  });

  test('should toggle task completion state', async ({ page }) => {
    await page.click('button:has-text("Onboarding")');
    const firstCheckbox = page.locator('input[type="checkbox"]').first();
    const wasChecked = await firstCheckbox.isChecked();

    await firstCheckbox.click();
    // Verification: state changes
    if (wasChecked) {
      await expect(firstCheckbox).not.toBeChecked();
    } else {
      await expect(firstCheckbox).toBeChecked();
    }
  });
});
