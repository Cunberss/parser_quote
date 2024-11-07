import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
from typing import List, Dict


class QuoteScraper:
    """Класс парсера"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.quote_id_counter = 1

    async def fetch_page(self, session: aiohttp.ClientSession, page_number: int) -> str:
        """Асинхронная функция для запроса одной страницы"""
        self.base_url = self.base_url + '/' if not self.base_url.endswith('/') else self.base_url
        url = f"{self.base_url}page/{page_number}/"
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()

    def parse_quotes(self, html: str, page_number: int) -> List[Dict[str, str]]:
        """Парсинг страницы"""
        soup = BeautifulSoup(html, 'html.parser')
        quotes = []
        for quote in soup.find_all('div', class_='quote'):
            text = quote.find('span', class_='text').text
            author = quote.find('small', class_='author').text
            tags = [tag.text for tag in quote.find_all('a', class_='tag')]
            quotes.append({
                'id': self.quote_id_counter,
                'text': text,
                'author': author,
                'tags': tags,
                'page_number': page_number
            })
            self.quote_id_counter += 1
        return quotes

    async def scrape_all_quotes(self, max_page_number: int = 10) -> List[Dict[str, str]]:
        """Асинхронная функция для запроса всех страниц, парсинг и сохранение объектов в список"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_page(session, page_number) for page_number in range(1, max_page_number + 1)]
            pages = await asyncio.gather(*tasks)

            all_quotes = []
            for page_number, html in enumerate(pages, start=1):
                quotes = self.parse_quotes(html, page_number)
                all_quotes.extend(quotes)

            return all_quotes


class DataExporter:
    """Класс для экспорта результатов"""
    @staticmethod
    def export_to_json(data: List[Dict[str, str]], filename: str):
        """Экспортируем данные в json"""

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


async def main():
    base_url = "https://quotes.toscrape.com/"
    scraper = QuoteScraper(base_url)
    quotes = await scraper.scrape_all_quotes(max_page_number=100)

    exporter = DataExporter()
    exporter.export_to_json(quotes, 'quotes.json')


if __name__ == "__main__":
    asyncio.run(main())
