import logging

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """Configura o logger para o aplicativo."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Configuração do logger padrão
logger = setup_logger('trading_bot', 'trading_bot.log')