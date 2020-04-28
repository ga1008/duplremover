import logging


def set_logger(log_level=logging.INFO, pure_mode=False):
    logger = logging.getLogger("logger")

    handler1 = logging.StreamHandler()

    logger.setLevel(log_level)
    handler1.setLevel(log_level)

    # formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    if not pure_mode:
        formatter = logging.Formatter("%(asctime)s >>> %(message)s", "%Y-%m-%d %H:%M:%S")
    else:
        formatter = logging.Formatter("%(message)s")
    handler1.setFormatter(formatter)

    logger.addHandler(handler1)
    return logger
