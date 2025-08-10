# ------------------------------------------------------------
# Script para preparar toda a estrutura de ambiente do projeto Datalyzer
# ------------------------------------------------------------

import os
import sys
import venv
import subprocess
from pathlib import Path

# Garante que a pasta raiz do projeto esteja no PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.py_processor.utils.logger import logger


# Estrutura de pastas que será criada
FOLDERS = [
      "data"
    , "data/input"
    , "data/output"
    , "src"
    , "src/config"
    , "src/logs"
]

# Arquivos básicos do projeto
FILES = {}

def create_folders():
    for folder in FOLDERS:
        Path(folder).mkdir(parents=True, exist_ok=True)
    logger.info("[OK] - Pastas criadas")

def create_files():
    for file_path, content in FILES.items():
        path = Path(file_path)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    logger.info("[OK] - Arquivos base criados")

def create_virtualenv():
    venv_dir = Path("venv")
    if not venv_dir.exists():
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        logger.info("[OK] - Ambiente virtual criado")
    else:
        logger.info("[INFO] - Ambiente virtual já existe")

def install_requirements():
    req_file = Path("requirements.txt")
    if req_file.exists() and req_file.stat().st_size > 0:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("[OK] - Dependências instaladas")
    else:
        logger.info("[INFO] - Nenhuma dependência para instalar")

if __name__ == "__main__":
    logger.info("=== PREPARANDO AMBIENTE DO PROJETO! ===")
    create_folders()
    # create_files()
    # create_virtualenv()
    install_requirements()
    logger.info("=== AMBIENTE PRONTO! ===")
