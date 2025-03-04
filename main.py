import asyncio
from getpass import getpass
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import os


AUTO_REPLY_TEXT = ("🔥 Play Shillong Teer Online from Anywhere, Anytime – No More Counter Queues, Just Big Wins! 🔥\n\n"
                   "✅ Instant & Secure Gameplay\n"
                   "✅ Trusted Platform\n"
                   "✅ Easy Withdrawals\n\n"
                   "🔹 Play Now: teerkhelo.web.app\n\n"
                   "🔹 WhatsApp wa.link/79fmfa")

# Dictionary to hold conversation IDs and the time when a reply was sent.
processed_chats = {}

async def run(playwright):
    global processed_chats
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    
    await page.goto("https://www.messenger.com/")

    # Prompt for credentials (password input is hidden)
    email = os.getenv("MESSENGER_EMAIL")
    password = os.getenv("MESSENGER_PASSWORD")

    # Login
    await page.fill('input[name="email"]', email)
    await page.fill('input[name="pass"]', password)
    await page.click('button[name="login"]')
    # Wait for page load (using 'load' event)
    await page.wait_for_load_state('load', timeout=60000)
    print("Logged in successfully!")
    
    # Wait for an element that indicates the Messenger home page is ready
    try:
        await page.wait_for_selector('div[aria-label="Chats"]', timeout=15000)
        await asyncio.sleep(3)
    except Exception as e:
        print("Chat list not found; proceeding anyway:", e)
    
    print("Monitoring for unread messages...")

    while True:
        # Clean up processed_chats older than 10 minutes
        now = datetime.now()
        processed_chats = {cid: ts for cid, ts in processed_chats.items() if now - ts < timedelta(minutes=10)}
        
        # Look for unread message indicators (adjust XPath if necessary)
        unread_elements = await page.query_selector_all(
            "xpath=//*[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'unread')]"
        )
        if unread_elements:
            print(f"Found {len(unread_elements)} unread indicator(s).")
            for unread in unread_elements:
                try:
                    # Force click the unread element (to bypass overlays)
                    await unread.click(force=True)
                    print("Forced click on unread element succeeded.")
                    await page.wait_for_timeout(3000)  # Wait for the chat to load
                    
                    # Extract conversation ID from the current URL
                    current_url = page.url
                    conversation_id = None
                    if "/t/" in current_url:
                        conversation_id = current_url.split("/t/")[1].split("/")[0]
                    
                    if conversation_id:
                        if conversation_id in processed_chats:
                            print(f"Conversation {conversation_id} already processed. Skipping auto-reply.")
                        else:
                            message_box = await page.wait_for_selector('div[aria-label="Message"]', timeout=5000)
                            await message_box.fill(AUTO_REPLY_TEXT)
                            await message_box.press("Enter")
                            print("Auto-reply sent to conversation", conversation_id)
                            processed_chats[conversation_id] = datetime.now()
                    else:
                        print("Could not determine conversation ID. Sending auto-reply anyway.")
                        message_box = await page.wait_for_selector('div[aria-label="Message"]', timeout=5000)
                        await message_box.fill(AUTO_REPLY_TEXT)
                        await message_box.press("Enter")
                        print("Auto-reply sent.")
                except Exception as e:
                    print("Error processing unread message:", e)
        else:
            print("No unread messages found.")
        await asyncio.sleep(10)

    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == '__main__':
    asyncio.run(main())
