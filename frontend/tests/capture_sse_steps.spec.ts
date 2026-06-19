import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

test('Capture Agent Thought Steps SSE Screenshot', async ({ page }) => {
  const screenshotsDir = path.resolve('tests/screenshots/audit');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }

  // Mock authenticated user session
  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'user-audit-sse',
        email: 'sse_audit@lumo.ai',
        full_name: 'Visual Auditor',
        role: 'USER'
      })
    });
  });

  // Mock documents list so we have an active document
  await page.route('**/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'vnm-doc-id',
          name: 'VNM_BCTC_2023.pdf',
          size: '1.2 MB',
          uploadedAt: '2026-06-18 10:00',
          status: 'indexed',
          user_id: 'user-audit-sse'
        }
      ])
    });
  });

  // Mock active PDF info
  await page.route('**/api/v1/documents/vnm-doc-id/info', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'vnm-doc-id',
        name: 'VNM_BCTC_2023.pdf',
        totalPages: 2,
        pages: [
          { page: 1, width: 600, height: 800 },
          { page: 2, width: 600, height: 800 }
        ]
      })
    });
  });

  // Mock chat-stream SSE with steps requested by the user
  await page.route('**/chat-stream*', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'text/event-stream',
      body: [
        'event: step\n',
        'data: {"node": "retriever", "output": "📚 Retriever: Retriever searching ChromaDB for financial blocks..."}\n\n',
        'event: step\n',
        'data: {"node": "coder", "output": "🖥️ Coder: Code Execution sandbox starting to generate data comparison..."}\n\n',
        'event: final_answer\n',
        'data: {"content": "Based on the database blocks retrieved, the comparison of financial metrics is shown below. Coder Sandbox processed the Python script and visualized it successfully."}\n\n',
        'event: done\n',
        'data: end\n\n'
      ].join('')
    });
  });

  await page.goto('http://localhost:5173');
  await page.waitForTimeout(2000);

  // Enter a message
  const chatInput = page.locator('#chat-input-field');
  await expect(chatInput).toBeVisible();
  await chatInput.fill('Compare Vinamilk performance in 2023');
  await chatInput.press('Enter');

  // Wait for the thought process stepper and final answer to show up
  await page.locator('text=Multi-Agent Thought process').waitFor({ state: 'visible', timeout: 10000 });
  await page.locator('text=Based on the database blocks').waitFor({ state: 'visible', timeout: 10000 });
  await page.waitForTimeout(1000);

  // Take the screenshot
  await page.screenshot({ path: path.join(screenshotsDir, 'agent_thought_steps.png'), fullPage: true });
  console.log('[Capture] Screenshot saved to agent_thought_steps.png');
});
