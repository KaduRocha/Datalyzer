# ------------------------------------------------------------
# Sistema de logging para o Datalyzer
# ------------------------------------------------------------

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Caminho padrão para salvar logs
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "datalyzer.log"

# Formato padrão
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

def setup_logger(name: str = "datalyzer") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:  # Garante que não adiciona múltiplos handlers

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)

        # File handler com rotação (5 arquivos de até 5MB)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)

    return logger

# Instância padrão para reutilização fácil
logger = setup_logger()


