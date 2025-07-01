import logging

logging.basicConfig(level=logging.INFO, filename='assistant.log')

def log_event(module, msg):
    logging.info(f"[EVENT][{module}] {msg}")

def log_error(module, msg):
    logging.error(f"[ERROR][{module}] {msg}")