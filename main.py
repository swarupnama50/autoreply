import asyncio
import threading
import os
from flask import Flask
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

app = Flask(__name__)

AUTO_REPLY_TEXT = ("🔥 Play Shillong Teer Online from Anywhere, Anytime – No More Counter Queues, Just Big Wins! 🔥\n\n"
                   "✅ Instant & Secure Gameplay\n"
                   "✅ Trusted Platform\n"
                   "✅ Easy Withdrawals\n\n"
                   "🔹 Play Now: teerkhelo.web.app\n\n")

# Dictionary to hold processed conversations
processed_chats = {}

async def run(playwright):
    global processed_chats
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    await page.goto("https://www.messenger.com/")

    email = os.getenv("MESSENGER_EMAIL")
    password = os.getenv("MESSENGER_PASSWORD")

    await page.fill('input[name="email"]', email)
    await page.fill('input[name="pass"]', password)
    await page.click('button[name="login"]')

    await page.wait_for_load_state('load', timeout=60000)
    print("Logged in successfully!")

    try:
        await page.wait_for_selector('div[aria-label="Chats"]', timeout=15000)
        await asyncio.sleep(3)
    except Exception as e:
        print("Chat list not found:", e)

    print("Monitoring for unread messages...")

    while True:
        now = datetime.now()
        processed_chats = {cid: ts for cid, ts in processed_chats.items() if now - ts < timedelta(minutes=10)}

        unread_elements = await page.query_selector_all(
            "xpath=//*[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'unread')]"
        )
        if unread_elements:
            print(f"Found {len(unread_elements)} unread messages.")
            for unread in unread_elements:
                try:
                    await unread.click(force=True)
                    await page.wait_for_timeout(3000)  # Wait for chat to load

                    current_url = page.url
                    conversation_id = current_url.split("/t/")[1].split("/")[0] if "/t/" in current_url else None

                    if conversation_id and conversation_id not in processed_chats:
                        message_box = await page.wait_for_selector('div[aria-label="Message"]', timeout=5000)
                        await message_box.fill(AUTO_REPLY_TEXT)
                        await message_box.press("Enter")
                        print("Auto-reply sent to:", conversation_id)
                        processed_chats[conversation_id] = datetime.now()
                except Exception as e:
                    print("Error processing unread message:", e)
        else:
            print("No unread messages.")

        await asyncio.sleep(10)

    await browser.close()

# Start Playwright bot in a background thread
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
