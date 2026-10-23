from pathlib import Path
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
ROOT = Path(__file__).resolve().parents[1]
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')
    openai_api_key: str = ''
    proxy_api_key: str = ''
    proxy_api_base_url: str = 'https://api.proxyapi.ru/openai/v1'
    openai_model: str = 'gpt-4o-mini'
    openai_vision_model: str = 'gpt-4o-mini'
    api_host: str = '127.0.0.1'
    api_port: int = 8000
    history_file: str = str(Path(os.environ['LOCALAPPDATA']) / 'PEm08' / 'history.json') if 'LOCALAPPDATA' in os.environ else str(ROOT / 'runtime' / 'history.json')
    max_history_items: int = 30
    parser_timeout: int = 20
    parser_user_agent: str = 'PEm08 educational competitor monitor'
settings = Settings()
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('competitor_monitor')
FIXTURE_URLS = [f'http://127.0.0.1:8000/fixtures/{name}.html' for name in ('flowpilot','doculab','visiondesk')]

MARKET_URLS = ['https://tilda.cc/ru/', 'https://www.framer.com/', 'https://readymag.com/']
COMPETITOR_URLS = MARKET_URLS + FIXTURE_URLS
