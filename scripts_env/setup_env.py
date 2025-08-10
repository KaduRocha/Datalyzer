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

VENV_DIR = Path(".venvDatalyzer")


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
    if not VENV_DIR.exists():
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)
        logger.info("[OK] - Ambiente virtual criado")
        if VENV_DIR.exists() and VENV_DIR.is_dir():
            install_requirements()
    else:
        logger.info("[INFO] - Ambiente virtual já existe")


def install_requirements():
    """Instala as dependências usando o pip do ambiente virtual."""
    pip_executable = (
        VENV_DIR / "Scripts" / "pip.exe"  # Windows
        if os.name == "nt"
        else VENV_DIR / "bin" / "pip"    # Linux/Mac
    )

    req_file = Path("requirements.txt")
    if req_file.exists() and req_file.stat().st_size > 0:
        subprocess.check_call([str(pip_executable), "install", "-r", str(req_file)])
        logger.info("[OK] - Dependências instaladas no ambiente virtual")
    else:
        logger.info("[INFO] - Nenhuma dependência")

if __name__ == "__main__":
    logger.info("=== PREPARANDO AMBIENTE DO PROJETO! ===")
    create_folders()
    # create_files()
    create_virtualenv()
    # install_requirements()
    logger.info("=== AMBIENTE PRONTO! ===")
