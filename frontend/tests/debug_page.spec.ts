import { test, expect } from '@playwright/test';

test('DEBUG: capture page HTML and screenshot on load', async ({ page }) => {
  await page.route('**/api/v1/auth/me', (route: any) =>
    route.fulfill({ status: 401, body: JSON.stringify({ detail: 'Not authenticated' }) })
  );

  await page.goto('http://localhost:5174/');

  // Wait a moment for React to render
  await page.waitForTimeout(3000);

  // Take screenshot
  await page.screenshot({ path: 'tests/screenshots/DEBUG_initial_load.png', fullPage: true });

  // Print page title
  const title = await page.title();
  console.log('Page title:', title);

  // Print all headings
  const headings = await page.locator('h1, h2, h3, h4').allTextContents();
  console.log('Headings on page:', headings);

  // Print all button texts
  const buttons = await page.locator('button').allTextContents();
  console.log('Buttons on page:', buttons);

  // Print all input types
  const inputs = await page.locator('input').evaluateAll((els: Element[]) =>
    els.map((el: any) => ({ id: el.id, type: el.type, placeholder: el.placeholder }))
  );
  console.log('Inputs on page:', JSON.stringify(inputs));

  // Save full HTML
  const html = await page.content();
  const fs = require('fs');
  fs.writeFileSync('tests/screenshots/DEBUG_page.html', html);
  console.log('HTML saved');

  // Basic assertion so it doesn't fail
  expect(title).not.toBe('');
});
