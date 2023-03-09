import json
# Inputs

# UPDATE ITEM_ENDPOINT

# Input body
input_template_item = json.dumps({
    "machId": "1234",
    "testField": "testValue",
})

# event
event = {
    "path": "/template-engine/path-of-the-api", 
    "httpMethod": "POST", 
    "queryStringParameters": {"machId": "machId1"}, 
    "body": str(input_template_item)
}
