import { test, expect } from '@playwright/test';

test.describe('VoltAgent E2E Chat Flow', () => {
  test('should load the chat interface and send a message', async ({ page }) => {
    // 1. Mở trang chủ React
    await page.goto('http://localhost:3001');

    // 2. Kiểm tra các thành phần UI cơ bản
    await expect(page.locator('.sidebar')).toBeVisible();
    await expect(page.locator('.logo-bolt')).toBeVisible();
    await expect(page.locator('h1')).toHaveText('VoltAgent');

    // 3. Nhập câu hỏi và gửi
    const input = page.locator('textarea');
    await input.fill('Lợi nhuận của FPT năm 2023?');
    await page.keyboard.press('Enter');

    // 4. Kiểm tra trạng thái Loading (Thought Process)
    await expect(page.locator('.message-bubble')).toHaveCount(2); // 1 User, 1 Assistant
    
    // 5. Chờ kết quả và kiểm tra Markdown
    // LangGraph có thể mất vài giây để stream kết quả
    await expect(page.locator('.prose')).not.toBeEmpty({ timeout: 30000 });
    
    // 6. Kiểm tra xem có icon thumbs up không (xác nhận render assistant actions)
    await expect(page.locator('.lucide-thumbs-up').first()).toBeVisible();
  });

  test('should refresh the chat on New Chat click', async ({ page }) => {
    await page.goto('http://localhost:3001');
    const input = page.locator('textarea');
    await input.fill('Temporary message');
    await page.keyboard.press('Enter');
    
    await expect(page.locator('.message-bubble')).toHaveCount(2);
    
    await page.click('.new-chat-btn');
    // Reload sẽ làm sạch messages (vì chưa có persistence load history tự động trong App.tsx)
    await expect(page.locator('.message-bubble')).toHaveCount(0);
  });
});
