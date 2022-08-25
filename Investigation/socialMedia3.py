import asyncio
from playwright.async_api import async_playwright
from pyvirtualdisplay import Display
import time

def printAll():
    return twAc
async def run(playwright,phone_number):
    global page
    global twAc
    display = Display(visible=0, size=(1600, 1200))
    display.start()
    firefox = playwright.firefox
    browser = await firefox.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://twitter.com/i/flow/login")

    await page.locator('.r-30o5oe').fill(phone_number[0])
    await page.click('div.css-18t94o4:nth-child(6)')
    try:
        await page.click('span.css-18t94o4:nth-child(1) > span:nth-child(1) > span:nth-child(1)',timeout=5000)
        twAc="True"
    except:
        twAc="False"
    await browser.close()
async def twMain(phone_number):
    async with async_playwright() as playwright:
        await run(playwright,phone_number)




