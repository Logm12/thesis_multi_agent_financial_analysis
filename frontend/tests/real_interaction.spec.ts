import { test, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

test.describe('Real Multi-Agent System Interaction Flow', () => {
  const screenshotsDir = path.resolve('tests/screenshots/real');
  const vnmPdf = path.resolve('../data/VNM_BCTC.pdf');
  const fptPdf = path.resolve('../data/FPT_BCTC.pdf');

  test.beforeAll(() => {
    if (!fs.existsSync(screenshotsDir)) {
      fs.mkdirSync(screenshotsDir, { recursive: true });
    }
  });

  test('Step-by-step Interactive User Flow on Real App', async ({ page, context }) => {
    // Large timeout because we are running real inference with NVIDIA NIM and OpenAI API
    test.setTimeout(480000); 

    // Clear cookies and storage state to start fresh
    await context.clearCookies();
    
    // 1. Navigate to Landing Page
    console.log('[1] Navigating to landing page...');
    await page.goto('http://localhost:5173/');
    await page.evaluate(() => localStorage.clear());
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(screenshotsDir, '01_landing_page.png'), fullPage: true });

    // 2. Go to Register Form
    console.log('[2] Navigating to Login/Register page...');
    await page.goto('http://localhost:5173/#/login');
    
    const switchBtn = page.locator('button:has-text("Create one")');
    await switchBtn.waitFor({ state: 'visible', timeout: 10000 });
    await switchBtn.click();
    await page.waitForTimeout(1000);
    
    const email = `test_jury_${Date.now()}@lumo.ai`;
    console.log(`[3] Registering new user: ${email}...`);
    await page.locator('#fullName').fill('Thesis Reviewer Member');
    await page.locator('#email').fill(email);
    await page.locator('#password').fill('Lumo@2025!');
    await page.screenshot({ path: path.join(screenshotsDir, '02_registration_filled.png'), fullPage: true });
    
    await page.getByRole('button', { name: 'Sign Up' }).click();
    await page.waitForTimeout(3000);

    // If redirect did not auto-login, sign in manually
    if (await page.locator('#email').isVisible()) {
      console.log('[4] Auto-login did not occur, manually signing in...');
      await page.locator('#email').fill(email);
      await page.locator('#password').fill('Lumo@2025!');
      await page.getByRole('button', { name: 'Sign In' }).click();
      await page.waitForTimeout(3000);
    }

    // 5. Verify Dashboard is loaded
    console.log('[5] Verifying main chat interface is loaded...');
    const chatInput = page.locator('input[placeholder*="Ask AI about"]');
    await expect(chatInput).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: path.join(screenshotsDir, '03_main_chat_dashboard.png'), fullPage: true });

    // 6. Upload Vinamilk PDF
    console.log(`[6] Uploading Vinamilk PDF: ${vnmPdf}...`);
    await page.locator('#file-upload').evaluate((el: HTMLInputElement) => el.style.display = 'block');
    await page.locator('#file-upload').setInputFiles(vnmPdf);
    
    console.log('[7] Waiting for Vinamilk ingestion to complete...');
    // The message changes to "successfully processed" or contains indexing success text, or notes it already existed
    const firstUploadMsg = page.locator('text=Successfully processed').or(page.locator('text=existed in system')).first();
    await expect(firstUploadMsg).toBeVisible({ timeout: 90000 });
    await page.screenshot({ path: path.join(screenshotsDir, '04_vnm_upload_done.png'), fullPage: true });

    // 7. Upload FPT PDF
    console.log(`[8] Uploading FPT PDF: ${fptPdf}...`);
    await page.locator('#file-upload').setInputFiles(fptPdf);
    
    console.log('[9] Waiting for FPT ingestion to complete...');
    // We expect another message bubble indicating completion
    const secondUploadMsg = page.locator('text=Successfully processed').or(page.locator('text=existed in system')).nth(1);
    await expect(secondUploadMsg).toBeVisible({ timeout: 90000 });
    await page.screenshot({ path: path.join(screenshotsDir, '05_fpt_upload_done.png'), fullPage: true });

    // Helper function to submit query, wait for streaming to complete, and take screenshot
    const askQuestion = async (qNumber: number, questionText: string) => {
      console.log(`[Q${qNumber}] Submitting: "${questionText}"`);
      await chatInput.fill(questionText);
      await page.waitForTimeout(500);
      await chatInput.press('Enter');

      // Wait for thought process to begin (activeSteps accordion or shimmer active)
      await page.waitForTimeout(2000);
      
      // Wait for the stream loading indicator (spinner SVG) to detach
      console.log(`[Q${qNumber}] Waiting for agent generation stream to complete...`);
      await page.locator('button:has(svg.animate-spin)').waitFor({ state: 'detached', timeout: 180000 });
      await page.waitForTimeout(2000);

      const screenshotName = `q${qNumber}_answer.png`;
      await page.screenshot({ path: path.join(screenshotsDir, screenshotName), fullPage: true });
      console.log(`[Q${qNumber}] Completed, screenshot saved to ${screenshotName}`);
    };

    // 8. Submit 8 Financial Questions sequentially
    const questions = [
      "Doanh thu thuần của Vinamilk năm 2023 là bao nhiêu?",
      "Lợi nhuận sau thuế của Vinamilk năm 2023 là bao nhiêu?",
      "Tỷ suất lợi nhuận gộp của FPT năm 2023 là bao nhiêu phần trăm?",
      "Hãy so sánh doanh thu của FPT năm 2023 với năm 2022.",
      "Chi phí bán hàng và chi phí quản lý doanh nghiệp của Vinamilk năm 2023 thay đổi thế nào?",
      "Tổng vốn chủ sở hữu của FPT cuối năm 2023 là bao nhiêu?",
      "Hãy so sánh biên lợi nhuận ròng giữa FPT và Vinamilk trong năm 2023.",
      "Tổng tài sản của Vinamilk tại ngày 31/12/2023 là bao nhiêu?"
    ];

    for (let i = 0; i < questions.length; i++) {
      await askQuestion(i + 1, questions[i]);
    }

    // 9. Inspect the Real-time Thought Tracing Accordion
    console.log('[10] Checking the Thought Tracing accordion panel...');
    const accordionHeader = page.locator('text=Real-Time Multi-Agent Thought Tracing Stream');
    if (await accordionHeader.isVisible()) {
      await accordionHeader.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(screenshotsDir, '14_accordion_expanded.png'), fullPage: true });
      console.log('[11] Saved expanded thought tracing accordion screenshot');
    } else {
      console.log('[11] Thought tracing stream accordion was not visible at the end of the conversation');
    }
  });
});
