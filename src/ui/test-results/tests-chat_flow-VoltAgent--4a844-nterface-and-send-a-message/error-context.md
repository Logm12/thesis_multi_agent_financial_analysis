# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests\chat_flow.spec.ts >> VoltAgent E2E Chat Flow >> should load the chat interface and send a message
- Location: tests\chat_flow.spec.ts:4:3

# Error details

```
Error: expect(locator).not.toBeEmpty() failed

Locator: locator('.prose')
Expected: not empty
Error: strict mode violation: locator('.prose') resolved to 2 elements:
    1) <div class="prose">…</div> aka locator('div').filter({ hasText: /^Lợi nhuận của FPT năm 2023\?$/ })
    2) <div class="prose">…</div> aka locator('div').filter({ hasText: 'Initializing...' }).nth(5)

Call log:
  - Expect "not toBeEmpty" with timeout 30000ms
  - waiting for locator('.prose')

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - complementary [ref=e4]:
    - generic [ref=e5]:
      - img [ref=e6]
      - heading "VoltAgent" [level=1] [ref=e8]
    - button "New Chat" [ref=e9] [cursor=pointer]:
      - img [ref=e10]
      - text: New Chat
    - generic [ref=e11]:
      - heading "History" [level=3] [ref=e12]
      - generic [ref=e13]: No recent chats
    - generic [ref=e14]:
      - img [ref=e16]
      - text: User Account
  - main [ref=e19]:
    - generic [ref=e20]:
      - generic [ref=e21]:
        - img [ref=e23]
        - generic [ref=e26]:
          - generic [ref=e27]: You
          - paragraph [ref=e29]: Lợi nhuận của FPT năm 2023?
      - generic [ref=e30]:
        - img [ref=e32]
        - generic [ref=e35]:
          - generic [ref=e36]: VoltAgent
          - generic [ref=e38]: Initializing...
    - generic [ref=e39]:
      - generic [ref=e40]:
        - textbox "Ask a financial question..." [active] [ref=e41]
        - button [disabled] [ref=e42] [cursor=pointer]:
          - img [ref=e43]
      - generic [ref=e46]: VoltAgent can make mistakes. Check important info.
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('VoltAgent E2E Chat Flow', () => {
  4  |   test('should load the chat interface and send a message', async ({ page }) => {
  5  |     // 1. Mở trang chủ React
  6  |     await page.goto('http://localhost:3001');
  7  | 
  8  |     // 2. Kiểm tra các thành phần UI cơ bản
  9  |     await expect(page.locator('.sidebar')).toBeVisible();
  10 |     await expect(page.locator('.logo-bolt')).toBeVisible();
  11 |     await expect(page.locator('h1')).toHaveText('VoltAgent');
  12 | 
  13 |     // 3. Nhập câu hỏi và gửi
  14 |     const input = page.locator('textarea');
  15 |     await input.fill('Lợi nhuận của FPT năm 2023?');
  16 |     await page.keyboard.press('Enter');
  17 | 
  18 |     // 4. Kiểm tra trạng thái Loading (Thought Process)
  19 |     await expect(page.locator('.message-bubble')).toHaveCount(2); // 1 User, 1 Assistant
  20 |     
  21 |     // 5. Chờ kết quả và kiểm tra Markdown
  22 |     // LangGraph có thể mất vài giây để stream kết quả
> 23 |     await expect(page.locator('.prose')).not.toBeEmpty({ timeout: 30000 });
     |                                              ^ Error: expect(locator).not.toBeEmpty() failed
  24 |     
  25 |     // 6. Kiểm tra xem có icon thumbs up không (xác nhận render assistant actions)
  26 |     await expect(page.locator('.lucide-thumbs-up').first()).toBeVisible();
  27 |   });
  28 | 
  29 |   test('should refresh the chat on New Chat click', async ({ page }) => {
  30 |     await page.goto('http://localhost:3001');
  31 |     const input = page.locator('textarea');
  32 |     await input.fill('Temporary message');
  33 |     await page.keyboard.press('Enter');
  34 |     
  35 |     await expect(page.locator('.message-bubble')).toHaveCount(2);
  36 |     
  37 |     await page.click('.new-chat-btn');
  38 |     // Reload sẽ làm sạch messages (vì chưa có persistence load history tự động trong App.tsx)
  39 |     await expect(page.locator('.message-bubble')).toHaveCount(0);
  40 |   });
  41 | });
  42 | 
```