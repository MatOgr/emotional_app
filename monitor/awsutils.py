import boto3
from botocore.exceptions import ClientError
import logging

from model import GenerateReportRequest, Metadata

BUCKET_NAME = 'pracainzynierska-z3-5-helloworldbucket'
def upload_file(img_path: str, img_name: str, request: GenerateReportRequest):
    s3 = boto3.Session(aws_access_key_id=request.AccessKeyId, 
                       aws_secret_access_key=request.SecretKey, 
                       aws_session_token=request.SessionToken).client('s3')
    logging.info('[OK] S3 Authorized.')
    print("IdentityId: " + request.IdentityId)
    with open(img_path, 'rb') as f:
        try:
            logging.info('Uploading file...')
            s3.upload_fileobj(f, BUCKET_NAME, 'home/' + request.IdentityId + '/' + img_name)

            logging.info('[OK] File uploaded.')
        except ClientError as e:
            logging.error(e)