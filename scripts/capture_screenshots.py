import asyncio
import os
import sys
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:5000"
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

async def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--no-sandbox", "--disable-gpu"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2
        )
        page = await context.new_page()

        # 1. Landing Page
        print("[1] Capturing Landing Page...", flush=True)
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "LandingPage.png"))
        print("    [OK] Saved LandingPage.png", flush=True)

        # 2. About Page
        print("[2] Capturing About & Architecture Page...", flush=True)
        await page.goto(f"{BASE_URL}/about", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "ArchitectureAbout.png"))
        print("    [OK] Saved ArchitectureAbout.png", flush=True)

        # 3. Load Demo Portfolio from Landing Page and go to Dashboard
        print("[3] Loading Mutual Fund Demo Audit...", flush=True)
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.wait_for_timeout(500)
        
        # Click Explore with Demo Portfolio
        await page.locator("button:has-text('Explore with Demo Portfolio')").first.click()
        print("    Waiting for dashboard navigation...", flush=True)
        await page.wait_for_url("**/dashboard", timeout=15000)
        await page.wait_for_timeout(2000)
        
        # Ensure section-mf-overview is active and rendered
        await page.screenshot(path=os.path.join(ASSETS_DIR, "MFPortfolioAudit.png"))
        print("    [OK] Saved MFPortfolioAudit.png", flush=True)

        # 4. Stock Overlap Section
        print("[4] Capturing Stock Overlap Matrix...", flush=True)
        await page.click(".nav-item[data-section='mf-overlap']")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "StockOverlap.png"))
        print("    [OK] Saved StockOverlap.png", flush=True)

        # 5. Holdings & 4-Tier Form
        print("[5] Capturing Holdings & Rolling Form...", flush=True)
        await page.click(".nav-item[data-section='mf-holdings']")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "HoldingsRollingForm.png"))
        print("    [OK] Saved HoldingsRollingForm.png", flush=True)

        # 6. AI Chatbot Section
        print("[6] Capturing FinWise AI Chatbot...", flush=True)
        await page.click(".nav-item[data-section='mf-chatbot']")
        await page.wait_for_timeout(1500)
        
        # Trigger first prompt chip
        chips = page.locator(".chat-chip, .prompt-chip, button.quick-prompt-btn")
        if await chips.count() > 0:
            await chips.first.click()
            print("    Triggered prompt chip, waiting for response...", flush=True)
            await page.wait_for_timeout(4000)
            
        await page.screenshot(path=os.path.join(ASSETS_DIR, "AIChatbotAdvisor.png"))
        print("    [OK] Saved AIChatbotAdvisor.png", flush=True)

        # 7. Spending Overview
        print("[7] Capturing Spending Overview...", flush=True)
        await page.click(".nav-item[data-section='spending-overview']")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "Dashboard.png"))
        print("    [OK] Saved Dashboard.png", flush=True)

        # 8. Spending Anomalies & Health Score
        print("[8] Capturing Spending Anomalies & Health Score...", flush=True)
        await page.click(".nav-item[data-section='spending-anomalies']")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "SpendingAnomalies.png"))
        await page.screenshot(path=os.path.join(ASSETS_DIR, "HealthScore.png"))
        print("    [OK] Saved SpendingAnomalies.png and HealthScore.png", flush=True)

        await browser.close()
        print("\nALL SCREENSHOTS CAPTURED AND SAVED TO ASSETS!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
