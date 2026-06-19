import { test, expect } from '@playwright/test';

test.describe('Chat Streaming and Citation E2E Tests (TIP-002)', () => {
  test('Scenario 1 & 2: Streaming steps should display correctly and citation tooltip should show on hover', async ({ page }) => {
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

    // Intercept and mock the SSE endpoint /chat-stream
    await page.route('**/chat-stream*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        headers: {
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
        body: [
          'event: step\n',
          'data: {"node": "retriever", "output": "Đang tìm kiếm thông tin..."}\n\n',
          'event: step\n',
          'data: {"node": "coder", "output": "Đang thực thi mã tính toán..."}\n\n',
          'event: final_answer\n',
          'data: {"content": "Theo báo cáo tài chính của công ty [1], lợi nhuận ròng năm 2024 đạt tăng trưởng ấn tượng."}\n\n',
          'event: done\n',
          'data: end\n\n'
        ].join('')
      });
    });

    page.on('console', msg => {
      console.log(`[BROWSER CONSOLE ${msg.type()}]:`, msg.text());
    });

    await page.goto('http://localhost:5173');

    // Send a message
    const input = page.locator('input[placeholder*="Ask AI about"]');
    await input.fill('So sánh kết quả kinh doanh năm 2024');
    await input.press('Enter');

    // Assert intermediate steps are shown
    const reasoningSteps = page.locator('#reasoning-steps');
    await expect(reasoningSteps).toBeVisible({ timeout: 5000 });
    await expect(reasoningSteps).toContainText('Thought process');
    await expect(reasoningSteps).toContainText('Đang tìm kiếm thông tin...');
    await expect(reasoningSteps).toContainText('Đang thực thi mã tính toán...');

    // Assert final message content is rendered
    const finalMsg = page.locator('text=lợi nhuận ròng năm 2024 đạt tăng trưởng ấn tượng');
    await expect(finalMsg).toBeVisible({ timeout: 5000 });

    // Assert citation hook [1] is rendered
    const citationHook = page.locator('#citation-hook-1');
    await expect(citationHook).toBeVisible();

    // Hover over the citation hook
    await citationHook.hover();

    // Verify tooltip is shown
    const tooltip = page.locator('#citation-tooltip-1');
    await expect(tooltip).toBeVisible();
    await expect(tooltip).toContainText('View citation directly on PDF document');
  });
});
