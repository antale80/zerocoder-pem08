"""Запуск вручную после локального подключения API. 6 LLM-запросов, без Selenium."""
from pathlib import Path
import json, httpx
root=Path(__file__).resolve().parent
out=root/'runtime'/'live';out.mkdir(parents=True,exist_ok=True)
with httpx.Client(base_url='http://127.0.0.1:8000',timeout=90) as client:
    for competitor in json.loads((root/'data/manifest.json').read_text()):
        slug=competitor['id']
        jobs=[('text',dict(json={'text':(root/'data'/competitor['text']).read_text()}))]
        for kind,kwargs in jobs:
            response=client.post('/analyzetext',**kwargs);response.raise_for_status();result=response.json()
            (out/f'{slug}-{kind}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
            if not result.get('success'):raise SystemExit('Анализ не выполнен. См. runtime/live; ключ, модель или квота требуют проверки.')
        with (root/'data'/competitor['image']).open('rb') as file:
            response=client.post('/analyzeimage',files={'file':(competitor['image'],file,'image/png')})
        response.raise_for_status();result=response.json()
        (out/f'{slug}-image.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
        if not result.get('success'):raise SystemExit('Анализ изображения не выполнен. См. runtime/live.')
    (out/'history.json').write_text(json.dumps(client.get('/history').json(),ensure_ascii=False,indent=2))
print('Шесть реальных ответов сохранены в runtime/live. Проверьте их по исходникам.')
