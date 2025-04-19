import logging
import sys

from constantes import DEBUG

logger = logging.getLogger()
handler = logging.FileHandler('debug.log')
if DEBUG:
    logger.setLevel(logging.INFO)
    handler.setLevel(logging.INFO)
else:
    logger.setLevel(logging.ERROR)
    handler.setLevel(logging.ERROR)

log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(stream_handler)