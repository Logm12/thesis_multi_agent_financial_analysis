import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

test.describe('File Upload Validation E2E Tests (TIP-001)', () => {
  const assetsDir = path.resolve('tests/assets');
  const txtFile = path.join(assetsDir, 'test_document.txt');
  const validPdf = path.join(assetsDir, 'test_valid.pdf');
  const largePdf = path.join(assetsDir, 'test_large.pdf');

  test.beforeAll(() => {
    if (!fs.existsSync(assetsDir)) {
      fs.mkdirSync(assetsDir, { recursive: true });
    }
    // Create text file
    fs.writeFileSync(txtFile, 'This is a plain text file, not a PDF.');
    // Create valid small pdf (dummy)
    fs.writeFileSync(validPdf, '%PDF-1.4 dummy content');
    // Create >100MB PDF file
    const largeSize = 101 * 1024 * 1024; // 101MB
    const buffer = Buffer.alloc(largeSize);
    fs.writeFileSync(largePdf, buffer);
  });

  test.afterAll(() => {
    // Cleanup temporary files
    try {
      if (fs.existsSync(txtFile)) fs.unlinkSync(txtFile);
      if (fs.existsSync(validPdf)) fs.unlinkSync(validPdf);
      if (fs.existsSync(largePdf)) fs.unlinkSync(largePdf);
      if (fs.existsSync(assetsDir)) fs.rmdirSync(assetsDir);
    } catch (e) {
      console.error('Cleanup error:', e);
    }
  });

  test.beforeEach(async ({ page }) => {
    // Mock authenticated user session
    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'user-123', email: 'test@example.com', full_name: 'Test User', role: 'USER' })
      });
    });
    await page.route('**/health', async (route) => {
      await route.fulfill({ status: 200, body: JSON.stringify({ status: 'ok' }) });
    });
  });

  test('Scenario 1: Should block non-PDF files immediately at Frontend and not call upload API', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Monitor for any POST upload API calls
    let uploadApiCalled = false;
    await page.route('**/upload*', async (route) => {
      uploadApiCalled = true;
      await route.fulfill({ status: 200, body: 'MOCK_UPLOAD_SUCCESS' });
    });

    await page.screenshot({ path: 'screenshot.png' });
    // Handle file input
    await page.locator('#file-upload').evaluate((el: HTMLInputElement) => el.style.display = 'block');
    await page.locator('#file-upload').setInputFiles(txtFile);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'screenshot_after_upload.png' });
    const toast = page.locator('text=Invalid file. Please upload PDF reports only.');
    await expect(toast).toBeVisible({ timeout: 5000 });

    // Assert API was NOT called
    expect(uploadApiCalled).toBe(false);
  });

  test('Scenario 2: Should block files larger than 100MB at Frontend and not call upload API', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Monitor for any POST upload API calls
    let uploadApiCalled = false;
    await page.route('**/upload*', async (route) => {
      uploadApiCalled = true;
      await route.fulfill({ status: 200, body: 'MOCK_UPLOAD_SUCCESS' });
    });

    // Handle file input
    await page.locator('#file-upload').evaluate((el: HTMLInputElement) => el.style.display = 'block');
    await page.locator('#file-upload').setInputFiles(largePdf);

    // Verify size validation toast error is shown
    const toast = page.locator('text=File too large. Please upload a file smaller than 100MB.');
    await expect(toast).toBeVisible({ timeout: 5000 });

    // Assert API was NOT called
    expect(uploadApiCalled).toBe(false);
  });

  test('Scenario 3: Should successfully call upload API for valid PDF under 100MB', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Monitor and intercept POST upload API calls
    let uploadApiCalled = false;
    await page.route('**/upload*', async (route) => {
      uploadApiCalled = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'success', task_id: 'mock-task-123' })
      });
    });

    // Handle file input
    await page.locator('#file-upload').evaluate((el: HTMLInputElement) => el.style.display = 'block');
    await page.locator('#file-upload').setInputFiles(validPdf);

    // Verify success toast or loading toast is shown
    const loadingToast = page.locator('text=Analyzing document:');
    await expect(loadingToast).toBeVisible({ timeout: 5000 });

    // Assert API WAS called
    expect(uploadApiCalled).toBe(true);
  });
});
