import json
import datetime

def respond(res):
    log = log_structure(res)
    return {
        "statusCode": "400" if 'error' in res else "200",
        "body": json.dumps(log),
        "headers": {
            "Content-Type": "application/json",
        },
    }

def log_structure(res):
    name_of_lambda = ''
    if 'error' in res:
        msg = f'{name_of_lambda}_failed'
    else:
        msg = f'{name_of_lambda}_successful'
    return {
        'msg': msg,
        'info': res,
        'time': str(datetime.datetime.now())
    }