import boto3
from boto3.dynamodb.conditions import Key, Attr
import asyncio, concurrent


class DynamoHook:
    def __init__(self, dynamo_table=None):
        """Init for class

        Args:
            dynamo_table (str): Optional - name of the dynamo table.

        """
        if dynamo_table:
            dynamo_db = boto3.resource('dynamodb')
            self.table = dynamo_db.Table(dynamo_table)

    def get_item(self, key, value):
        """Get a single item from dynamo.

        Args:
            key (str): name of the primary key
            value (str): value of the primary key

        Returns:
            dict: row of given primary key
        """
        try:
            response = self.table.get_item(Key={key: value})
            return response["Item"] if 'Item' in response else None
        except Exception as e:
            print("Error try to get item from dynamo: " + str(e))
            return ''

    def query(self, key, value, sort_key=None, sort_value=None, filter_key=None, filter_value=None, index=None):
        """Get one or more rows from dynamo with query operation. 

        Args:
            key (str): name of the primary key
            value (str): value of the primary key
            sort_key (str): Optional - name of the sort key
            sort_value (str): Optional - value of the sort key
            filter_key (str): Optional - name of the attribute if you want a filter search
            filter_value (str): Optional - value of the attribute if you want a filter search
            index (str): Optional - name of the global secondary index (ex. {name_of_the_gsi_attribute}-index).

        Returns:
            dict: row of given primary key
        """
        try:
            if sort_key and sort_value:
                response = self.table.query(KeyConditionExpression=Key(key).eq(value) & Key(sort_key).eq(sort_value))
            elif filter_key and filter_value:
                response = self.table.query(KeyConditionExpression=Key(key).eq(value), FilterExpression=Attr(filter_key).eq(filter_value))
            elif index:
                response = self.table.query(IndexName=index, KeyConditionExpression=Key(key).eq(value))
            else:
                response = self.table.query(KeyConditionExpression=Key(key).eq(value))
            return response["Items"] if any(response["Items"]) else None
        except Exception as e:
            print("Error try to query from dynamo: " + str(e))
            return ''

    def put_item(self, item):
        """Put an item in dynamo table.

        Args:
            item (dict): row that will be put in table. Must have Primary Key.
                         Sort key will also be mandatory if the configuration of the
                         table say so.

        """
        try:
            self.table.put_item(Item=item)
        except Exception as e:
            print("Error try to put item into dynamo: " + str(e))

    def update_item(self, item, key, sort_key=None, index=None):
        """Update an item in dynamo table.

        Args:
            item (dict): row that will be updated in table. Must have Primary Key.
                         Sort key will also be mandatory if the configuration of the
                         table say so.
            sort_key (str): Optional - name of the sort key
            index (str): Optional - name of the global secondary index (ex. {name_of_the_gsi_attribute}-index).

        """
        try:
            primary_value = item.pop(key)
            keys = {key: primary_value}
            if sort_key:
                sort_value = item.pop(sort_key)
                keys[sort_key] = sort_value
            if index:
                index_value = item.pop(index)
                keys[index] = index_value
            update_expression = 'SET {}'.format(','.join(f'#{k}=:{k}' for k, v in item.items() if v is not None))
            expression_attribute_values = {f':{k}': v for k, v in item.items() if v is not None}
            expression_attribute_names = {f'#{k}': k for k, v in item.items() if v is not None}

            self.table.update_item(
                Key=keys,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues="NONE")

        except Exception as e:
            print("Error try to update item into dynamo: " + str(e))

    def delete_item(self, key, value, sort_key=None, sort_value=None):
        """Delete an item in dynamo table.

        Args:
            key (str): name of the primary key
            value (str): value of the primary key
            sort_key (str): Optional - name of the sort key
            sort_value (str): Optional - value of the sort key

        """
        item_to_delete = {key: value}
        try:
            if sort_key and sort_value:
                item_to_delete.update({sort_key: sort_value})
            self.table.delete_item(
                Key=item_to_delete
            )
        except Exception as e:
            print("Error try to delete item into dynamo: " + str(e))

        # ASYNC VERSION FOR QUERY OR GET ITEM IN MULTIPLE TABLES

    def get_data_from_dynamo_for_async_extraction(self, table_name, parameters):
        """get_item and query dynamo operations for async function. 
        Args:
            table_name (str): name of the table in dynamo
            parameters (str): dictionary with key, value and the operation. For example: 
                           tables = {
                               key: 'mach_id' (str),
                               value: '123' (str),
                               operation: 'query' (str)
                           } 
                           operation parameter can be get_item, query or gsi (global secondary index)

        Returns:
            dict: row with the attributes of the search.

        """
        table = DynamoHook(table_name)
        key = parameters.get('key')
        value = parameters.get('value')
        sort_key = parameters.get('sort_key')
        sort_value = parameters.get('sort_value')
        filter_key = parameters.get('filter_key')
        filter_value = parameters.get('filter_value')
        index = parameters.get('index')
        operation = parameters.get('operation')

        if key and value:
            if operation == 'get_item':
                response = table.get_item(key, value)
            
            elif operation == 'query':
                response = table.query(key, value, sort_key, sort_value, filter_key, filter_value, index)
        else:
            response = None

        return {'table_name': table_name, 'response': response}

    async def parallel_query(self, tables):
        """Do a parallel querys (or get item) operation into different tables
        Args:
            tables (dict): The key must be the name of the table, and the element must be a dict
                           with key, value and the operation. For example:
                           config_tables = {
                                table_name = {
                                    key: 'mach_id' (str),
                                    value: '123' (str),
                                    operation: 'query' (str)
                                }
                            } 
                           operation parameter can be get_item or query

        Returns:
            list: list of lists with the results of the dynamo operation (this results are dicts)

        """
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=len(tables),
        )
        loop = asyncio.get_event_loop()
        boto3_tasks = [loop.run_in_executor(executor, self.get_data_from_dynamo_for_async_extraction, *(item, tables[item])) for item in tables]
        completed, pending = await asyncio.wait(boto3_tasks)
        recommendations = [t.result() for t in completed]
        recommendations = list(filter(None, recommendations))

        response = {}
        for item in recommendations:
            response[item['table_name']] = item['response']

        return response

    def get_data_from_many_tables_async(self, tables):
        """Get the data from different tables concurrently
        Args:
            tables (dict): The key must be the name of the table, and the element must be a dict
                           with key, value and the operation. For example:
                           config_tables = {
                                table_name = {
                                    key: 'mach_id' (str),
                                    value: '123' (str),
                                    operation: 'query' (str)
                                }
                            } 
                           operation parameter can be get_item or query

        Returns:
            list: list of lists with the results of the dynamo operation (this results are dicts)

        """
        return asyncio.run(DynamoHook().parallel_query(tables))