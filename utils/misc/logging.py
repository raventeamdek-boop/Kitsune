import logging

logging.basicConfig(
    filename='logs.log',
    level=logging.INFO,
    format='%(asctime)s : %(filename)s line - %(lineno)d : %(funcName)s : %(name)s : %(levelname)s : %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')