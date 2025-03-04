import asyncio
import threading
import os
from flask import Flask
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

app = Flask(__name__)

AUTO_REPLY_TEXT = "🔥 Play Shillong Teer Online from Anywhere, Anytime – No More Counter Queues, Just Big Wins! 🔥\n\n✅ Instant & Secure Gameplay\n✅ Trusted Platform\n✅ Easy Withdrawals\n\n🔹 Play Now: teerkhelo.web.app\n\n"

processed_chats = {}

async def run(playwright):
    global processed_chats
    print("🚀 Launching Playwright...")

    try:
        browser = await playwright.chromium.launch(headless=True)
        print("✅ Browser launched successfully")
    except Exception as e:
        print(f"❌ Failed to launch browser: {e}")
        return

    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto("https://www.messenger.com/")
        print("✅ Opened Messenger")
    except Exception as e:
        print(f"❌ Error opening Messenger: {e}")
        return

    email = os.getenv("MESSENGER_EMAIL")
    password = os.getenv("MESSENGER_PASSWORD")

    if not email or not password:
        print("❌ Missing login credentials!")
        return

    try:
        await page.fill('input[name="email"]', email)
        await page.fill('input[name="pass"]', password)
        await page.click('button[name="login"]')
        await page.wait_for_load_state('load', timeout=60000)
        print("✅ Logged in successfully!")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    print("🎯 Watching for unread messages...")

    while True:
        now = datetime.now()
        processed_chats = {cid: ts for cid, ts in processed_chats.items() if now - ts < timedelta(minutes=10)}

        unread_elements = await page.query_selector_all(
            "xpath=//*[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'unread')]"
        )
        print(f"🔍 Found {len(unread_elements)} unread messages.")

        for unread in unread_elements:
            try:
                await unread.click(force=True)
                await page.wait_for_timeout(3000)

                current_url = page.url
                conversation_id = current_url.split("/t/")[1].split("/")[0] if "/t/" in current_url else None

                if conversation_id and conversation_id not in processed_chats:
                    message_box = await page.wait_for_selector('div[aria-label="Message"]', timeout=5000)
                    await message_box.fill(AUTO_REPLY_TEXT)
                    await message_box.press("Enter")
                    print(f"✅ Auto-reply sent to {conversation_id}")
                    processed_chats[conversation_id] = datetime.now()
            except Exception as e:
                print(f"❌ Error processing unread message: {e}")

        await asyncio.sleep(10)

    await browser.close()

def start_playwright_bot():
    asyncio.run(run_playwright())

async def run_playwright():
    async with async_playwright() as playwright:
        await run(playwright)

threading.Thread(target=start_playwright_bot, daemon=True).start()

@app.route('/')
def home():
    return "Messenger Auto-reply Bot is running!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
