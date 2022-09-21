import asyncio
from playwright.async_api import async_playwright
from pyvirtualdisplay import Display
import time
def printAll():
    return instAc
async def run(playwright,phone_number):
    global page
    global instAc
    firefox = playwright.firefox
    browser = await firefox.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://www.instagram.com/accounts/login/")
    await page.locator('[name="username"]').fill(phone_number[0])
    await page.locator('[name="password"]').fill(phone_number[0])
    await page.click('button:has-text("Log In")')
    try:
        try:
            await page.text_content('p:has-text("Sorry, your password was incorrect. Please double-check your password.")',timeout=3000)
            instAc="True"
        except:
            try:
                await page.text_content('p:has-text("a problem")',timeout=3000)
                instAc="_False_"
            except:
                instAc="False"
    except:
        instAc="False"
    await browser.close()
async def instaMain(phone_number):
    async with async_playwright() as playwright:
        await run(playwright,phone_number)
