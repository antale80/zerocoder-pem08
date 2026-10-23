"""Локальное подключение: ключ остаётся в памяти процесса, не записывается в файлы."""
import secrets, os
PORT = int(os.environ.get("PEM08_PORT", "8000"))
from fastapi import Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from openai import AsyncOpenAI
from backend.main import app
from backend.config import settings

TOKEN = secrets.token_urlsafe(32)
STATE = {'connected': False, 'message': 'Введите ключ для подключения.'}

def guard(request):
    if request.headers.get('host') not in (f'127.0.0.1:{PORT}',f'localhost:{PORT}'):
        raise HTTPException(403)
    if request.method == 'POST' and request.headers.get('origin') not in (f'http://127.0.0.1:{PORT}',f'http://localhost:{PORT}'):
        raise HTTPException(403)

@app.get('/connect', response_class=HTMLResponse)
async def form(request: Request):
    guard(request)
    import html
    page='''<!doctype html><html lang="ru"><meta charset="utf-8"><title>PEm08 Подключение API</title>
    <style>body{font:18px Arial;max-width:760px;margin:45px auto;padding:24px;background:#f3f5f8;color:#172b42}main{background:white;padding:32px;border-radius:14px}label{display:block;margin-top:20px}input,select{font:18px Arial;width:95%;padding:12px;margin-top:8px}button{font:18px Arial;background:#145b70;color:white;padding:15px;border:0;border-radius:7px;margin-top:24px}small{line-height:1.5;display:block}a{color:#145b70}</style><main>
    <h1>PEm08 Подключение анализатора</h1><p>KEY_MESSAGE</p>
    <form action="/connect" method="post"><input type="hidden" name="csrf" value="CSRF_TOKEN">
    <label>Провайдер<select name="provider"><option value="openai">OpenAI</option><option value="proxyapi">Proxy API</option></select></label>
    <label>API-ключ<input type="password" name="api_key" required autocomplete="off"></label>
    <label>Модель анализа текста<input name="text_model" value="gpt-4o-mini" required></label>
    <label>Модель анализа изображений<input name="vision_model" value="gpt-4o-mini" required></label>
    <p><small>Ключ используется только сервером для выбранного провайдера и хранится в памяти до остановки процесса. В отчёт и архив он не попадает. После подключения разрешён дополнительный цикл до 9 запросов: проверка исправленной версии на текстах, изображениях и собранной странице. Используется квота вашего API-аккаунта. Новые подписки и пополнение баланса не оформляются.</small></p>
    <button>Подключить и проверить доступ</button></form><p><a href="/">Открыть анализатор</a></p></main></html>'''
    page=page.replace('KEY_MESSAGE',html.escape(STATE['message'])).replace('CSRF_TOKEN',TOKEN)
    return HTMLResponse(page, headers={'Cache-Control':'no-store','X-Frame-Options':'DENY','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'"})

@app.post('/connect')
async def connect(request: Request, csrf: str=Form(...), provider: str=Form(...), api_key: str=Form(...),text_model: str=Form(...),vision_model: str=Form(...)):
    guard(request)
    if not secrets.compare_digest(csrf,TOKEN):raise HTTPException(403)
    if provider not in ('openai','proxyapi') or not 10<=len(api_key)<=1000 or not 1<=len(text_model)<=100 or not 1<=len(vision_model)<=100:
        raise HTTPException(400,'Проверьте поля')
    base='https://api.openai.com/v1' if provider=='openai' else 'https://api.proxyapi.ru/openai/v1'
    try:
        async with AsyncOpenAI(api_key=api_key,base_url=base,timeout=45,max_retries=0) as client:
            response=await client.models.list()
        models={x.id for x in response.data}
        if text_model not in models or vision_model not in models:
            STATE['message']='Ключ принят провайдером, но одна из моделей отсутствует в списке. Уточните названия моделей.'
            return RedirectResponse('/connect',status_code=303)
        settings.openai_api_key=api_key if provider=='openai' else ''
        settings.proxy_api_key=api_key if provider=='proxyapi' else ''
        settings.openai_model=text_model
        settings.openai_vision_model=vision_model
        STATE.update(connected=True,message='Подключение подтверждено. Codex может продолжить проверку задания. Ключ сохранён только в памяти.')
    except Exception:
        STATE['message']='Подключение не подтверждено. Проверьте ключ, выбранный сервис, сеть и доступ к API. Секрет не сохранён.'
    return RedirectResponse('/connect',status_code=303)

@app.get('/connection/status')
async def status(request:Request):
    guard(request)
    return STATE

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=PORT,access_log=False)
