import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

test.describe('TIP-QA-003 E2E Scenarios', () => {
  const assetsDir = path.resolve('tests/assets');
  const dummyPdf = path.join(assetsDir, 'dummy_10mb.pdf');

  test.beforeAll(() => {
    if (!fs.existsSync(assetsDir)) {
      fs.mkdirSync(assetsDir, { recursive: true });
    }
    fs.writeFileSync(dummyPdf, '%PDF-1.4 dummy content');
  });

  test.afterAll(() => {
    try {
      if (fs.existsSync(dummyPdf)) fs.unlinkSync(dummyPdf);
    } catch (e) {
      console.error(e);
    }
  });

  test('Scenario 1: Upload API should hit /api/v1/upload-pdf and receive 200 OK', async ({ page }) => {
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

    let apiCalledWithV1 = false;

    // Intercept POST to new unified endpoint
    await page.route('**/api/v1/upload-pdf*', async (route) => {
      apiCalledWithV1 = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'success', filename: 'dummy_10mb.pdf', task_id: 'test-task-123' })
      });
    });

    await page.goto('http://localhost:5173');

    // Trigger file upload
    await page.locator('#file-upload').evaluate((el: HTMLInputElement) => el.style.display = 'block');
    await page.locator('#file-upload').setInputFiles(dummyPdf);

    // Wait and assert that v1 API endpoint was called
    await page.waitForTimeout(1000);
    expect(apiCalledWithV1).toBe(true);
  });

  test('Scenario 2: Markdown Bold Rendering (**text** should become bold element)', async ({ page }) => {
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

    // Intercept chat-stream to return bold text
    await page.route('**/chat-stream*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: [
          'event: final_answer\n',
          'data: {"content": "Kết quả tại **Báo cáo Q4 2023** rất khả quan."}\n\n',
          'event: done\n',
          'data: end\n\n'
        ].join('')
      });
    });

    await page.goto('http://localhost:5173');

    // Send a message to trigger chat
    const input = page.locator('input[placeholder*="Ask AI about"]');
    await input.fill('Hi');
    await input.press('Enter');

    // Assert bold text is rendered inside a strong element
    const boldElement = page.locator('strong:has-text("Báo cáo Q4 2023")');
    await expect(boldElement).toBeVisible({ timeout: 5000 });
  });

  test('Scenario 3: Sidebar should display Knowledge and navigate successfully to Knowledge Base dashboard', async ({ page }) => {
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

    await page.goto('http://localhost:5173');

    // Check that "Knowledge" item is in Sidebar
    const knowledgeBtn = page.locator('button:has-text("Knowledge")');
    await expect(knowledgeBtn).toBeVisible();

    // Click on "Knowledge" base navigation item
    await knowledgeBtn.click();

    // Assert we transitioned to Hash route /#/knowledge
    await expect(page).toHaveURL(/.*#\/knowledge/);

    // Assert that the Knowledge Base Dashboard header is visible
    const kbHeader = page.locator('h1:has-text("Knowledge Base")');
    await expect(kbHeader).toBeVisible();
  });
});
