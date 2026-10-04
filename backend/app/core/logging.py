import logging


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("chainnetra")
    logger.setLevel(logging.INFO)
