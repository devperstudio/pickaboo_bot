from loguru import logger

logger.add("bot.log", rotation="1 MB")

def log_info(msg):
    logger.info(msg)

def log_error(msg):
    logger.error(msg)