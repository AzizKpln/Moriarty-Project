import asyncio
from playwright.async_api import async_playwright
from pyvirtualdisplay import Display
import time
def printAll():
    return faceAc
async def run(playwright,phone_number):
    global page
    global faceAc
  
    firefox = playwright.firefox
    browser = await firefox.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://www.facebook.com/login/")
    await page.locator('css=[placeholder="Email address or phone number"]').fill(phone_number[0])
    await page.locator('css=[placeholder="Password"]').fill(phone_number[0])
    await page.click("#loginbutton")
    try:
        try:
            await page.text_content('div:has-text("incorrect.")')
            faceAc="True"
        except:
            try:
                await page.text_content('div:has-text("invalid")')
                faceAc="True"
            except:
                faceAc="False"
    except:
        faceAc="False"
    print(faceAc)
    await browser.close()

async def faceMain(phone_number):
    async with async_playwright() as playwright:
        await run(playwright,phone_number)
        
