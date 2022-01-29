import boto3
import os
import urllib
import time
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.conditions import Key
import botocore

def fetch_db(event, context):
    time_now = int(time.time())
    userId = event['userID']
    if 'time' in event:
        timestamp = event['timestamp']
    else:
        timestamp = 2592000
    dynamodb = boto3.resource('dynamodb')
    dynamoTable = dynamodb.Table('EmotionsTable')
    response = dynamoTable.scan(
        FilterExpression=Attr('userId').eq(userId) and Attr('time').between(time_now-timestamp, time_now)
    )
    return response['Items']
