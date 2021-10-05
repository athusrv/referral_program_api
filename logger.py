import logging

logging.basicConfig(
    format='%(asctime)s # %(levelname)s at %(name)s.%(filename)s:%(lineno)d :: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.DEBUG
)
logger = logging.getLogger()
