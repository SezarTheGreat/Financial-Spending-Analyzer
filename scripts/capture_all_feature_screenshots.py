import asyncio
import os
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

        # 2. About & Architecture Page
        print("[2] Capturing About & Architecture Page...", flush=True)
        await page.goto(f"{BASE_URL}/about", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "ArchitectureAbout.png"))
        print("    [OK] Saved ArchitectureAbout.png", flush=True)

        # 3. Load Mutual Fund Demo Audit -> Dashboard
        print("[3] Loading Mutual Fund Demo Audit...", flush=True)
        await page.goto(f"{BASE_URL}/", wait_until="networkidle")
        await page.wait_for_timeout(500)
        await page.locator("button:has-text('Explore with Demo Portfolio')").first.click()
        await page.wait_for_url("**/dashboard", timeout=15000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "MFPortfolioAudit.png"))
        print("    [OK] Saved MFPortfolioAudit.png", flush=True)

        # 4. Holdings & 4-Tier Rolling Form
        print("[4] Capturing Holdings & Form...", flush=True)
        await page.evaluate("switchSection('mf-holdings')")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "HoldingsRollingForm.png"))
        print("    [OK] Saved HoldingsRollingForm.png", flush=True)

        # 5. Stock Overlap Matrix & Spatial Flower Venn
        print("[5] Capturing Stock Overlap Matrix...", flush=True)
        await page.evaluate("switchSection('mf-overlap')")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "StockOverlap.png"))
        print("    [OK] Saved StockOverlap.png", flush=True)

        # 6. AI Advisory & Step-by-Step Rebalance Action Plan
        print("[6] Capturing MF Advisory & Action Plan...", flush=True)
        await page.evaluate("switchSection('mf-advisory')")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "MFAdvisoryActions.png"))
        print("    [OK] Saved MFAdvisoryActions.png", flush=True)

        # 7. AI Chatbot Advisor Modal
        print("[7] Capturing FinWise AI Chatbot...", flush=True)
        await page.evaluate("switchSection('mf-chatbot')")
        await page.wait_for_timeout(1500)
        chips = page.locator(".chat-chip, .prompt-chip, button.quick-prompt-btn")
        if await chips.count() > 0:
            await chips.first.click()
            await page.wait_for_timeout(4000)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "AIChatbotAdvisor.png"))
        print("    [OK] Saved AIChatbotAdvisor.png", flush=True)

        # 8. Spending Overview Dashboard
        print("[8] Capturing Spending Overview...", flush=True)
        await page.evaluate("switchSection('spending-overview')")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "Dashboard.png"))
        print("    [OK] Saved Dashboard.png", flush=True)

        # 9. Expenses by Category
        print("[9] Capturing Expenses by Category...", flush=True)
        await page.evaluate("switchSection('spending-categories')")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "SpendingCategories.png"))
        print("    [OK] Saved SpendingCategories.png", flush=True)

        # 10. Daily Spending Trends & Heatmap
        print("[10] Capturing Spending Trends...", flush=True)
        await page.evaluate("switchSection('spending-trends')")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "SpendingTrends.png"))
        print("    [OK] Saved SpendingTrends.png", flush=True)

        # 11. Unusual Transactions & Anomalies / Health Score
        print("[11] Capturing Spending Anomalies & Health Score...", flush=True)
        await page.evaluate("switchSection('spending-anomalies')")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(ASSETS_DIR, "SpendingAnomalies.png"))
        await page.screenshot(path=os.path.join(ASSETS_DIR, "HealthScore.png"))
        print("    [OK] Saved SpendingAnomalies.png & HealthScore.png", flush=True)

        await browser.close()
        print("\nALL FEATURE SCREENSHOTS CAPTURED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
