import os, sys, threading, time, urllib.request
from pathlib import Path
if getattr(sys, 'frozen', False):
    os.chdir(Path(sys.executable).parent)
from backend.config import settings
from dotenv import load_dotenv
load_dotenv(Path.cwd() / '.env')
settings.openai_api_key = os.getenv('OPENAI_API_KEY', settings.openai_api_key)
settings.proxy_api_key = os.getenv('PROXY_API_KEY', settings.proxy_api_key)
settings.openai_model = os.getenv('OPENAI_MODEL', settings.openai_model)
settings.openai_vision_model = os.getenv('OPENAI_VISION_MODEL', settings.openai_vision_model)
import uvicorn
from backend.main import app
server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=8000, log_config=None))
threading.Thread(target=server.run, daemon=True).start()
for _ in range(100):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=.2): break
    except OSError: time.sleep(.1)
else: raise SystemExit('Локальный сервер не запустился. Проверьте порт 8000.')
sys.path.insert(0, str(Path(__file__).resolve().parent / 'desktop'))
if '--smoke-test' in sys.argv:
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from desktop.main import MainWindow
    gui = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    QTimer.singleShot(1500, gui.quit)
    try: code = gui.exec()
    finally: server.should_exit = True
    raise SystemExit(code)
else:
    from desktop.main import main
    try: main()
    finally: server.should_exit = True
