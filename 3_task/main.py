import asyncio
import csv
from playwright.async_api import async_playwright


async def parse_wiki_articles_with_details():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        all_articles_data = []
        target_url = "https://en.wikipedia.org/wiki/Wikipedia:Featured_articles"

        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_selector("#mw-content-text", timeout=10000)

        # Собираем ссылки
        article_links = await page.query_selector_all(
            "div#mw-content-text a[href^='/wiki/']:not([href*=':'])"
        )

        articles_to_parse = []
        for link in article_links:
            try:
                href = await link.get_attribute("href")
                title = await link.get_attribute("title")
                if href and title and ":" not in href and "index.php" not in href:
                    articles_to_parse.append((title, href))
            except:
                continue

        # парсим только 5 статей
        articles_to_parse = articles_to_parse[:5]

        for title, href in articles_to_parse:

            try:
                full_article_url = "https://en.wikipedia.org" + href

                # переход на статью
                await page.goto(
                    full_article_url, wait_until="domcontentloaded", timeout=30000
                )
                await page.wait_for_selector("#mw-content-text", timeout=10000)

                # считываем длину статьи
                content = await page.text_content("#mw-content-text")
                article_length = len(content.strip()) if content else 0

                # первый автор (из истории)
                article_title = href.replace("/wiki/", "")
                history_url = f"https://en.wikipedia.org/w/index.php?title={article_title}&action=history"

                await page.goto(
                    history_url, wait_until="domcontentloaded", timeout=30000
                )
                await page.wait_for_selector("#pagehistory", timeout=10000)

                history_entries = await page.query_selector_all("li[data-mw-revid]")

                # елси автор анонимен, то получаем его ip (<span> - mw-anonuserlink)
                first_author = "—"
                if history_entries:
                    first_entry = history_entries[-1]  # самая первая правка

                    author_link = await first_entry.query_selector("a.mw-userlink")
                    if author_link:
                        first_author = await author_link.inner_text()
                    else:
                        ip_span = await first_entry.query_selector(
                            "span.mw-anonuserlink"
                        )
                        if ip_span:
                            first_author = await ip_span.inner_text()

                all_articles_data.append(
                    [title, full_article_url, article_length, first_author]
                )

            except Exception as e:
                print(f"Ошибка при обработке {title}: {e}")
                continue

        await browser.close()

        with open("wiki_parse2.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Link", "Article Length (chars)", "First Author"])
            writer.writerows(all_articles_data)

        print(f"\nDone")


asyncio.run(parse_wiki_articles_with_details())