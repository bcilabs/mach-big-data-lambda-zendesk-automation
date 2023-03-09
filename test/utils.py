import json
import boto3
from index import handler
from handlers.dynamo_hook import DynamoHook

def get_table(table_name):
        return DynamoHook(table_name)

def log_structure(res):
    name_of_lambda = ''
    if 'error' in res:
        msg = f'{name_of_lambda}_failed'
    else:
        msg = f'{name_of_lambda}_successful'
    return {
        'msg': msg,
        'info': res
    }

def delete_time_from_body(test_return):
    # Remove time from return of handler for make the tests
    test_return['body'] = json.loads(test_return['body'])
    del test_return['body']['time']
    return test_return

# Dynamo create table for mocks function
def create_dynamo_mock_tables(dynamodb, table_name, attribute_dict, data_list):
    KeySchemaList = []
    AttributeDefinitionsList = []
    gsiList = []
    dynamo_index_list = []

    for attribute in attribute_dict:
        if attribute_dict[attribute][1] == 'primary':
            key_type = 'HASH'
        else:
            if attribute_dict[attribute][1] == 'gsi':
                gsiList.append(attribute)
            key_type = 'RANGE'
        KeySchemaList.append({'AttributeName': attribute, 'KeyType': key_type})
        AttributeDefinitionsList.append({'AttributeName': attribute, 'AttributeType': attribute_dict[attribute][0]})

    if not gsiList:
        table = dynamodb.create_table(
            TableName=table_name,
            BillingMode='PAY_PER_REQUEST',
            KeySchema=KeySchemaList,
            AttributeDefinitions=AttributeDefinitionsList
        )
    else:
        for gsi in gsiList:
            dynamo_index_list.append({
                'IndexName': gsi + '-index',
                'KeySchema': [
                    {
                        'AttributeName': gsi,
                        'KeyType': 'HASH'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL',
                },
            })
        table = dynamodb.create_table(
            TableName=table_name,
            BillingMode='PAY_PER_REQUEST',
            KeySchema=KeySchemaList,
            AttributeDefinitions=AttributeDefinitionsList,
            GlobalSecondaryIndexes=dynamo_index_list
        )
    for item in data_list:
        table.put_item(Item=item)
    return table

def test_endpoint_response(tables, event, dynamo_data_list_to_search=None):
    dynamodb = boto3.resource('dynamodb')
    for table in tables:
        create_dynamo_mock_tables(
            dynamodb=dynamodb,
            table_name=table['table_name'],
            attribute_dict=table['attribute_dict'],
            data_list=table['data'],
        )

    test_return = delete_time_from_body(handler(event, None))
    if not dynamo_data_list_to_search:
        return test_return, ""
    else:
        dynamo_data_list = []
        for item in dynamo_data_list_to_search:
            table = get_table(item['input']['table_name'])
            key = item['input']['key']
            value = item['input']['value']
            sort_key = item['input']['sort_key'] if 'sort_key' in item else ''
            sort_value = item['input']['sort_value'] if 'sort_value' in item else ''
            index = item['input']['index'] if 'index' in item else ''

            if 'sort_key' in item: 
                result = table.query(key=key, value=value, sort_key=sort_key, sort_value=sort_value)
            if 'index' in item:
                result = table.query(key=key, value=value, index=index)
            else:
                result = table.get_item(key=key, value=value)

            item.update({'dynamo_response': result})

        return test_return, dynamo_data_list_to_search
