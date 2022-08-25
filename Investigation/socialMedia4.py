import asyncio
from playwright.async_api import async_playwright
from pyvirtualdisplay import Display
import time

def printAll():
    return goAc
async def run(playwright,phone_number):
    global page
    global goAc
    display = Display(visible=0, size=(1600, 1200))
    display.start()
    firefox = playwright.firefox
    browser = await firefox.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://accounts.google.com/signin/v2/identifier?hl=en-GB&flowName=GlifWebSignIn&flowEntry=ServiceLogin")
    await page.locator('css=[autocomplete="username"]').fill(phone_number[0])
    await page.click('button:has-text("Next")')
    try:
        
        await page.click("css=[type='checkbox']")
        goAc="True"
    except:
        goAc="False"
    await browser.close()
async def goMain(phone_number):
    async with async_playwright() as playwright:
        await run(playwright,phone_number)




