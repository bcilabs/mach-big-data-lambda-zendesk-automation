import json
import os

from logger.engine_logger import get_logger
# Have to import the class from src
from src.engine_template_class import TemplateClassLogic

logger = get_logger()


def handler(event, context):
    logger.info("request_received", event)

    # Tables
    tables = {
        #Here is the tables from dynamo that you uses. For example:
        # 'template_table': os.environ["TEMPLATE_TABLE"]
    }

    path = event["path"].split('/')[2]
    engine = TemplateClassLogic(tables, path)
    return engine.handle_request(event, context)
