import os
from test.utils import log_structure

# Calls
# API GATEEWAY
# Body format
response_income_update_item = ''

# Endpoint success response
update_item = {
    "statusCode": "200",
    "body": log_structure({'machId': '', 'engine_response': response_income_update_item}),
    "headers": {"Content-Type": "application/json"},
}


# DYNAMO
# Dynamo data after endpoint success execution
# ONLY FOR ENDPOINTS THAT DO PUT, UPDATE OR DELETE IN DYNAMO
'''
dynamo_result = {
    "machId": '123',
    "testField": 'testValue'
}       

# input and output for tables
dynamo_data_list_to_search = [
    {
        "input": {
            "table_name": 'table_name',
            "key": 'machId',
            "value": '123'
        },
        "output": dynamo_result
    }
]
'''
