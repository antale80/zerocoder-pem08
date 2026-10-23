"""Запускать на Windows после pip install -r requirements-desktop.txt."""
import platform, subprocess, sys, os
from pathlib import Path
if platform.system() != 'Windows':
    raise SystemExit('Windows exe собирается на Windows. На текущей ОС сборка не выполнена.')
root = Path(__file__).resolve().parent
subprocess.run([sys.executable, '-m', 'PyInstaller', '--onefile', '--windowed',
 '--name', 'competitionmonitor', '--paths', str(root / 'desktop'),
 '--add-data', f'frontend{os.pathsep}frontend', '--add-data', f'data{os.pathsep}data',
 '--hidden-import', 'uvicorn.logging', '--hidden-import', 'uvicorn.loops.auto',
 '--hidden-import', 'uvicorn.protocols.http.auto', '--hidden-import', 'uvicorn.lifespan.on',
 '--collect-submodules', 'selenium', 'desktop_launcher.py'], cwd=root, check=True)
