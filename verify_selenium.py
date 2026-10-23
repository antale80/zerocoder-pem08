"""Запуск вручную. Открывает три публичные страницы через Selenium, без LLM."""
import asyncio, json
from pathlib import Path
from backend.config import MARKET_URLS
from backend.services.parser_service import ParserService

async def main():
    parser = ParserService()
    out = Path('runtime/selenium')
    out.mkdir(parents=True, exist_ok=True)
    try:
        for i, url in enumerate(MARKET_URLS, 1):
            title, h1, paragraph, png, error = await parser.parse_url(url)
            record = dict(url=url, title=title, h1=h1, first_paragraph=paragraph, error=error)
            (out / f'{i}.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
            if png:
                (out / f'{i}.png').write_bytes(png)
            if error:
                raise SystemExit('Сбор не выполнен: ' + error)
    finally:
        await parser.close()
asyncio.run(main())
