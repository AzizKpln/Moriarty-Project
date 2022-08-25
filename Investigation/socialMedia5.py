import asyncio
from playwright.async_api import async_playwright
from pyvirtualdisplay import Display
import time

def printAll():
    return micAc
async def run(playwright,phone_number):
    global page
    global micAc
    display = Display(visible=0, size=(1600, 1200))
    display.start()
    firefox = playwright.firefox
    browser = await firefox.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://shorturl.at/drxz5")
    await page.locator('css=[data-report-event="Signin_Email_Phone_Skype"]').fill(phone_number[0])
    await page.click('css=[data-report-event="Signin_Submit"]',timeout=2000)
    try:
        await page.text_content('#usernameError',timeout=4000)
        micAc="False"
    except:
        micAc="True"
    await browser.close()
async def micMain(phone_number):
    async with async_playwright() as playwright:
        await run(playwright,phone_number)



