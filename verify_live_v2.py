"""Повторная серия после подключения. 6 вызовов, без автоматических повторов."""
from pathlib import Path
import json,httpx,os,time
root=Path(__file__).resolve().parent
out=root/'runtime/live-v2';out.mkdir(parents=True,exist_ok=True)
base=os.environ.get('PEM08_BASE','http://127.0.0.1:8001')
with httpx.Client(base_url=base,timeout=120) as client:
 for slug in ('tilda','framer','readymag'):
  for kind in ('text','image'):
   start=time.monotonic()
   if kind=='text':response=client.post('/analyzetext',json={'text':(root/f'data/{slug}-analysis-input.txt').read_text()})
   else:
    with (root/f'data/{slug}.png').open('rb') as file:response=client.post('/analyzeimage',files={'file':(slug+'.png',file,'image/png')})
   response.raise_for_status();result=response.json()
   record={'competitor':slug,'kind':kind,'duration_seconds':round(time.monotonic()-start,3),'result':result}
   (out/f'{slug}-{kind}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
   print(slug,kind,'success='+str(result.get('success')),flush=True)
 (out/'history.json').write_text(json.dumps(client.get('/history').json(),ensure_ascii=False,indent=2))
