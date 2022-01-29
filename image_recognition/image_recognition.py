import boto3
import os
import urllib
from boto3.dynamodb.conditions import Attr
import botocore
import time

def run_recognition(event, context):
    photo = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    user = event['Records'][0]['userIdentity']['principalId']
    key = os.path.splitext(photo)[0].split('_')[1]
    bucket = event['Records'][0]['s3']['bucket']['name']
    client = boto3.client("rekognition")
    response = client.detect_faces(
        Image={"S3Object": {"Bucket": bucket, "Name": photo}}, Attributes=["ALL"]
    )
    emotion = response["FaceDetails"][0]["Emotions"][0]["Type"]
    dynamodb = boto3.resource('dynamodb')
    dynamoTable = dynamodb.Table('EmotionsTable')
    item = {
        'userId': user,
        'recordID': f'{key}_img',
        'emotion': emotion,
        'time': int(time.time())
    }
    s3 = boto3.resource('s3')
    s3.Object(bucket, photo).delete()
    try:
        dynamoTable.put_item(
            Item = item
        )
    except botocore.exceptions.ClientError as e:
        print('Error occured!')
        raise
