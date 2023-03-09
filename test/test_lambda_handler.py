from http.client import responses
from sys import api_version
from test.utils import test_endpoint_response
from moto import mock_dynamodb
from test.resources import inputs, responses, dynamo_tables

class TestLambdaHandler:

    @mock_dynamodb
    def test_template_item_response(self):
        test_return, dynamo_data = test_endpoint_response(
            dynamo_tables.tables, 
            inputs.event 
            # , responses.dynamo_data_list_to_search -> only if endpoint modify a dynamo
        )

        assert test_return == responses.update_item
        # only if endpoint modify a dynamo
        '''
        if dynamo_data:
            for item in dynamo_data:
                print("A: ", item['dynamo_response'])
                print("B: ", item['output'])
                assert item['dynamo_response'] == item['output']
        '''
