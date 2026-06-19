import { test, expect } from '@playwright/test';

test.describe('TIP-QA-004 Stepper and Recharts Visual Test Suite', () => {
  test('Scenario 1: Stepper should display reasoning steps and toggle accordion', async ({ page }) => {
    // Mock authenticated user session
    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-123',
          email: 'test@example.com',
          full_name: 'Test User',
          role: 'USER'
        })
      });
    });

    // Mock document lists for dashboard right panel
    await page.route('**/api/v1/documents', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    // Mock chat-stream SSE with steps
    await page.route('**/chat-stream*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: [
          'event: step\n',
          'data: {"node": "retriever", "output": "📚 Retriever: Đang tìm kiếm thông tin doanh thu quý 4 năm 2023"}\n\n',
          'event: step\n',
          'data: {"node": "coder", "output": "🖥️ Coder: Đang lập trình biểu đồ doanh thu bằng pandas"}\n\n',
          'event: final_answer\n',
          'data: {"content": "Doanh thu năm 2023 đạt kết quả tốt."}\n\n',
          'event: done\n',
          'data: end\n\n'
        ].join('')
      });
    });

    await page.goto('http://localhost:5173');

    // Wait and input the message in the main chat dashboard
    const input = page.locator('input[placeholder*="Ask AI about"]');
    await expect(input).toBeVisible({ timeout: 10000 });
    await input.fill('Vẽ biểu đồ doanh thu FPT');
    await input.press('Enter');

    // Wait and assert that the AgentStepper is rendered
    const stepperTitle = page.locator('text=Multi-Agent Thought process');
    await expect(stepperTitle).toBeVisible({ timeout: 10000 });

    // Assert that both steps are visible inside the stepper
    const step1 = page.locator('text=📚 Retriever: Đang tìm kiếm');
    const step2 = page.locator('text=🖥️ Coder: Đang lập trình');
    await expect(step1).toBeVisible();
    await expect(step2).toBeVisible();

    // Toggle the accordion (click to close)
    await stepperTitle.click();
    await expect(step1).not.toBeVisible();

    // Toggle again to open
    await stepperTitle.click();
    await expect(step1).toBeVisible();
  });
});
