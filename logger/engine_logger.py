import logging
import time
import json
import sys
import os


class JSONFormatter(logging.Formatter):
    def format(self, record):
        string_formatted_time = time.strftime(
            "%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)
        )
        obj = {
            "message": record.msg,
            "level": record.levelname,
            "module": record.name,
            "time": f"{string_formatted_time}.{record.msecs:3.0f}Z",
        }
        if record.args:
            obj["info"] = record.args
        return json.dumps(obj)


def get_logger():
    logger = logging.getLogger(__name__)
    logger.propagate = False
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    formatter = JSONFormatter()
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    if "DEBUG" in os.environ and os.environ["DEBUG"] == "true":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        logging.getLogger("boto3").setLevel(logging.INFO)
        logging.getLogger("botocore").setLevel(logging.INFO)

    return logger
