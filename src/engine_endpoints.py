from typing import final
import boto3
import json
from datetime import datetime
from logger.engine_logger import get_logger
from handlers.dynamo_hook import DynamoHook


class EngineEndpoints:

    def __init__(self):
        self.dynamo = boto3.resource("dynamodb")
        self.log = get_logger()

    @staticmethod
    def _get_table(table_name):
        '''Return an instance from Dynamo table from boto3. The functions are in hablers/dynamo_hook'''
        return DynamoHook(table_name)

    def endpoint_error(self, error, mach_id=None, document_number=None):
        '''If the endpoint function has and error, this function parse the error and add mach_id or document_number'''
        response = {"error": "Error: " + error}
        if mach_id:
            response["machId"] = mach_id
        if document_number:
            response["documentNumber"] = document_number
        return response

    #This is an example of the endpoint function logic format. A possbile name for this functions are
    # {put/get}_{name_of_the_function}_data for example
    def template_endpoint_function(self, tables, event):

        self.log.info("template_endpoint_function_started", {"table": '', "item": event}) #-> fill with table that endpoint consults

        # Logic of the endpoint function
        try:
            mach_id = ''
            engine_response = ''
            result = {'machId': mach_id, 'engine_response': engine_response}
            self.log.info("template_endpoint_function_started_finish", result)
            return result
        except Exception as e:
            error = "Error try to put data in identity verification table: " + str(e)
            return self.endpoint_error(error, mach_id)
