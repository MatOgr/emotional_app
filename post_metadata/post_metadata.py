import json
import boto3
import logging
from botocore.exceptions import ClientError
import jwt
import json

def put_in_database(req_body):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('EmotionsTable')
    table.put_item(Item=req_body)
    

def lambda_handler(event, context):
    cognito_username = ''
    try:
        authorization_token = event['headers']['Authorization']
        decoded_token = jwt.decode(authorization_token, options={"verify_signature": False})
        cognito_username = ''
    
        cognito_username = decoded_token['cognito:username']
    except KeyError as e:
        return {
            "statusCode": 403,
            "body": json.dumps({
                "message": "Authorization error",
                "details": e
            })
        }

    body_json_str = event['body']
    req_body = json.loads(body_json_str)
    id = req_body['recordID']
    if id.split('_')[0] != cognito_username:
        return {
            "statusCode": 403,
            "body": json.dumps({
                "message": "You are not authorized to act on behalf of other user!"
            })
        }
    
    put_in_database(req_body)
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Metadata has been posted."
        })
    }
    
