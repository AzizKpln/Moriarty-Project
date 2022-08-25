import asyncio
from playwright.async_api import async_playwright
from pyvirtualdisplay import Display
import time
async def GoogleMail(email,password):
    await page2.fill("#identifierId",email)
    await page2.click("#identifierNext > div > button > span",timeout=3000)
    await page2.locator("#password > div.aCsJod.oJeWuf > div > div.Xb9hP > input").fill(password)
    await page2.locator("#passwordNext > div > button > span").click()
    await page2.locator("#submit_approve_access > div > button > div.VfPpkd-RLmnJb").click()
async def getName():
    global name
    try:
        name = await page.text_content("#__next > section.SearchDataSection_searchData___2rxeV > div.NumberDetailsCard_card___2vSQO.SearchDataSection_searchData__card___2yyUr.NumberDetailsCard_card__info___SGTrb > div > div > div.NumberDetailsCard_card__head___3dM4Q > div.NumberDetailsCard_card__name____58-0",timeout=3000)
    except:
        try:
            await page.text_content("#__next > section.SearchDataSection_searchData___2rxeV > div.NumberDetailsCard_card___2vSQO.SearchDataSection_searchData__card___2yyUr.NumberDetailsCard_card__overLimit___1aZPG > div > div > div.NumberDetailsCard_card__head___3dM4Q > div.NumberDetailsCard_card__name____58-0 > div",timeout=3000)
            name="exceeded"
        except:
            try:
                await page.text_content("#__next > section.SearchDataSection_searchData___2rxeV > div.NumberDetailsCard_card___2vSQO.SearchDataSection_searchData__card___2yyUr.NumberDetailsCard_card__noInfo___wOyaL > div > div > div.NumberDetailsCard_card__head___3dM4Q > div.NumberDetailsCard_card__name____58-0",timeout=3000)
                name="UnKnown"
            except:
                name="Update Required. Please contact with developer."
def printName():
    return name
async def run(playwright,phone_number,email,password):
    global page,page2
    display = Display(visible=0, size=(1600, 1200))
    display.start()
    firefox = playwright.firefox
    browser = await firefox.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://sync.me/")
    await page.locator('css=[placeholder="Search any phone number"]').fill(phone_number)
    await page.keyboard.press("Enter")
    time.sleep(1)
    async with context.expect_page() as new_page_info:
        await page.click("p.NumberDetailsCard_button___3FEkC:nth-child(1)")
    page2 = await new_page_info.value
    await page2.wait_for_load_state()
    time.sleep(2)
    await GoogleMail(email,password)
    await getName()
    await browser.close()
async def main1(phone_number,email,password):
    async with async_playwright() as playwright:
        await run(playwright,phone_number,email,password)
