import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(headless=True)
        page = await br.new_page()
        await page.goto("https://axa-hml-faturamento.nsseg.com.br/citnet/", wait_until="networkidle", timeout=20000)
        print("URL final:", page.url)
        print("Titulo:", await page.title())

        inputs = await page.evaluate("""
            () => Array.from(document.querySelectorAll('input, button, select'))
                .map(el => ({tag: el.tagName, id: el.id, name: el.name, type: el.type, placeholder: el.placeholder}))
        """)
        for inp in inputs:
            print(" ", inp)

        txt = await page.inner_text("body")
        print("Body (300):", txt[:300])
        await br.close()

asyncio.run(check())
