import os, tempfile, unittest, json, base64, asyncio
from pathlib import Path
from io import BytesIO
from unittest.mock import patch, AsyncMock
os.environ['HISTORY_FILE'] = str(Path(tempfile.mkdtemp()) / 'history.json')
os.environ['OPENAI_API_KEY'] = ''
os.environ['PROXY_API_KEY'] = ''
from fastapi.testclient import TestClient
from PIL import Image
from backend.main import app
from backend.config import settings, COMPETITOR_URLS
from backend.models.schemas import CompetitorAnalysis, ImageAnalysis
from backend.services.openai_service import OpenAIService

TEXT = dict(strengths=['Учебный факт'], weaknesses=[], unique_offers=[], recommendations=['Проверить гипотезу'], summary='Тест транспортного контракта',design_score=None,animation_potential='Гипотеза анимации',evidence=['Тестовый источник'],limitations=['Это тестовая заглушка, не вывод LLM'])
VISION = dict(description='Тестовое изображение',marketing_insights=[],visual_style_score=7,design_score=7,visual_style_analysis='Тест',animation_potential='Гипотеза',recommendations=[],evidence=['Тест'],limitations=['Заглушка'])
class AppTests(unittest.TestCase):
    def setUp(self): self.client=TestClient(app)
    def test_01_health_and_fixtures(self):
        self.assertEqual(self.client.get('/health').status_code,200)
        for name in ('flowpilot','doculab','visiondesk'):
            self.assertIn('Учебная вымышленная',self.client.get('/fixtures/'+name+'.html').text)
    def test_02_validation(self):
        self.assertEqual(self.client.post('/analyzetext',json={'text':'short'}).status_code,422)
        self.assertEqual(self.client.post('/analyzetext',json={'text':'x'*20001}).status_code,422)
    def test_03_missing_key(self):
        r=self.client.post('/analyzetext',json={'text':'Описание учебного конкурента'}).json()
        self.assertFalse(r['success']);self.assertIn('API не подключён',r['error'])
    def test_04_invalid_image(self):
        self.assertEqual(self.client.post('/analyzeimage',files={'file':('bad.png',b'bad','image/png')}).status_code,400)
    def test_05_mocked_routes_and_history(self):
        with patch('backend.main.openai_service.analyze_text',new=AsyncMock(return_value=CompetitorAnalysis(**TEXT))):
            for route in ('/analyzetext','/analyze_text'):
                r=self.client.post(route,json={'text':'Описание учебного конкурента'}).json()
                self.assertTrue(r['success']);self.assertIsNone(r['analysis']['design_score'])
        image=BytesIO(); Image.new('RGB',(10,10),'white').save(image,format='PNG')
        with patch('backend.main.openai_service.analyze_image',new=AsyncMock(return_value=ImageAnalysis(**VISION))):
            self.assertEqual(self.client.post('/analyzeimage',files={'file':('a.png',image.getvalue(),'image/png')}).json()['analysis']['design_score'],7)
        history=self.client.get('/history').json();self.assertGreaterEqual(history['total'],3);self.assertEqual(history['items'][0]['analysis']['design_score'],7)
    def test_06_parser_allowlist(self):
        r=self.client.post('/parsedemo',json={'url':'http://169.254.169.254/'}).json()
        self.assertFalse(r['success']);self.assertIn('список',r['error'])
    def test_07_mocked_parser_integration(self):
        with patch('backend.main.parser_service.parse_url',new=AsyncMock(return_value=('Demo','Demo','Описание',b'png',None))), patch('backend.main.openai_service.analyze_website_screenshot',new=AsyncMock(return_value=CompetitorAnalysis(**TEXT))):
            r=self.client.post('/parsedemo',json={'url':COMPETITOR_URLS[0]}).json()
            self.assertTrue(r['success']);self.assertEqual(r['data']['title'],'Demo')
    def test_08_model_response_validation(self):
        settings.openai_api_key='test-placeholder'
        try:
            for data,expected in [(TEXT,True),({**TEXT,'design_score':8},False),({'summary':'missing fields'},False)]:
                response=type('R',(),{'choices':[type('C',(),{'finish_reason':'stop','message':type('M',(),{'content':json.dumps(data)})()})()]})()
                client=AsyncMock();client.chat.completions.create=AsyncMock(return_value=response)
                with patch('backend.services.openai_service.AsyncOpenAI') as factory:
                    factory.return_value.__aenter__=AsyncMock(return_value=client)
                    factory.return_value.__aexit__=AsyncMock(return_value=None)
                    if expected: self.assertIsNone(asyncio.run(OpenAIService().analyze_text('Описание')).design_score)
                    else:
                        with self.assertRaises(RuntimeError):asyncio.run(OpenAIService().analyze_text('Описание'))
        finally:settings.openai_api_key=''
    def test_09_score_bounds(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError): ImageAnalysis(**{**VISION,'design_score':11})
if __name__=='__main__':unittest.main(verbosity=2)
