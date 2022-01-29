from typing import Callable
import boto3
from botocore.exceptions import ClientError, ParamValidationError
from pydantic import ValidationError
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response 
from os import access, environ
from model.User import User
import logging

'''
Module used for authentication with AWS Cognito Identity Provider
'''

DEFAULT_TOKEN_PATH='~/.emotional_credentials'
CLIENT_ID = '4md6155dt95s952l8ccuen8v4g'
IDENTITY_POOL_ID = 'eu-central-1:7e19dd0d-ebdc-40fb-a8cb-975d7587ad76'
REGION = 'eu-central-1'
USER_POOL_ID = 'eu-central-1_QRVSvaseq'

class Error(Exception):
    """Base exception class"""
    pass

class UserNotAuthenticatedError(Error):
    """Raised when user token was not found in the home directory"""
    def __init__(self):
        self.message = 'User is not authenticated.'
        
class UsernamePasswordError(Error):
    """Raised when credentials are incorrect."""
    
    def __init__(self):
        self.message = 'Username or password is incorrect.'
        
class UserNotAuthorizedError(Error):
    """Raised when current token could not be authorized against Cognito"""
    
    def __init__(self):
        self.message = "Invalid token!"
        
class ActivateAccountError(Error):
    """Raised when account activation fails."""
    
    def __init__(self):
        self.message = "Account activation failed!"
        
class SignUpError(Error):
    """Raised when user registration fails"""
    
    def __init__(self, error):
        self.message = error
        
class AuthenticationRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        
        async def authentication_route_handler(request: Request) -> Response:
            try:
                tokens = get_token()
                if not validate_credentials(tokens):
                    raise UserNotAuthenticatedError
            except (UserNotAuthenticatedError, UserNotAuthorizedError) as e:
                return RedirectResponse('/login?redirectPath=' + str(request.url.path), status_code=302)
            response: Response = await original_route_handler(request)
            return response
        
        return authentication_route_handler
            
def get_token_path():
    token_path = environ.get('TOKEN_PATH')
    if not token_path.strip():
        token_path = DEFAULT_TOKEN_PATH
        
    return token_path

def validate_credentials(tokens: dict) -> bool:
    return True #TODO

def get_token():
    token_path = get_token_path()
    tokens_str = ''
    tokens = dict()
    logging.info('Reading existing credentials...')
    try:
        with open(token_path, 'r') as f:
            for line in f:
                tokens_str += line
        for token in tokens_str.split('\n'):
            if len(token.split(' ')) > 1:
                key, value = token.split(' ')
                tokens[key] = value
            
    except FileNotFoundError as e:
        logging.error(e)
        raise UserNotAuthenticatedError
    
    return tokens

def authenticate(username: str, password: str) -> bool:
    logging.info("Started authentication process...")
    cgn_idp = boto3.client('cognito-idp', 'eu-central-1')
    cgn_identity = boto3.client('cognito-identity', 'eu-central-1')
    
    try:
        response = cgn_idp.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password}
        )
        logging.info('[OK] Username and passwords correct.')
        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        tokens = 'IdToken ' + id_token + '\n' + 'AccessToken ' + access_token + '\n'
        
        identity_id = cgn_identity.get_id(IdentityPoolId=IDENTITY_POOL_ID, Logins={
            'cognito-idp.' + REGION + '.amazonaws.com/' + USER_POOL_ID: id_token
        })['IdentityId']
        aws_credentials = cgn_identity.get_credentials_for_identity(IdentityId=identity_id, Logins={
            'cognito-idp.' + REGION + '.amazonaws.com/' + USER_POOL_ID: id_token
        })['Credentials']
        logging.info('[OK] Received AWS Credentials from Identity Pools')
        tokens += 'AccessKeyId ' + aws_credentials['AccessKeyId'] + '\n'
        tokens += 'SecretKey ' + aws_credentials['SecretKey'] + '\n'
        tokens += 'SessionToken ' + aws_credentials['SessionToken'] + '\n'
        tokens += 'IdentityId ' + identity_id
        token_path = get_token_path()
        with open(token_path, 'w') as f:
            f.seek(0)
            f.truncate()
            f.write(tokens)
            f.close()
            logging.info('[OK] Credentials saved.')
            return True
    except ClientError as e:
        logging.error(e)
        raise UsernamePasswordError

def activate_account(email: str, code: str):
    cgn = boto3.client('cognito-idp', 'eu-central-1')
    try:
        cgn.confirm_sign_up(Username=email, ConfirmationCode=code, ClientId=CLIENT_ID)
    except ClientError as e:
        logging.error(e)
        raise ActivateAccountError
    

def get_user_info(token: str) -> User:
    logging.info('Getting user info...')
    cgn = boto3.client('cognito-idp', 'eu-central-1')
    try:
        response = cgn.get_user(AccessToken=token)
        logging.info('[OK] Received user info from Cognito.')
        userAttr = dict()
        for attr in response['UserAttributes']:
            name = attr['Name']
            value = attr['Value']
            
            userAttr[name] = value
        print(userAttr)
        user = User(name=userAttr['name'], 
                    family_name=userAttr['family_name'], 
                    preferred_username=userAttr['preferred_username'], 
                    email=userAttr['email'], 
                    birthdate=userAttr['birthdate'], 
                    zoneinfo=userAttr['zoneinfo'],
                    user_id=userAttr['sub'])
        return user
    except (ClientError, ValidationError) as e:
        logging.error(e)
        raise UserNotAuthorizedError
    
def signup(name: str, family_name: str, preferred_username: str, 
             email: str, birthdate: str, zoneinfo: str, password: str):
    cgn = boto3.client('cognito-idp', 'eu-central-1')
    try:
        response = cgn.sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'name',
                    'Value': name
                },
                {
                    'Name': 'family_name',
                    'Value': family_name
                },
                {
                    'Name': 'preferred_username',
                    'Value': preferred_username
                },
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'birthdate',
                    'Value': birthdate
                },
                {
                    'Name': 'zoneinfo',
                    'Value': zoneinfo
                }
            ]
        )
    except (ClientError, ParamValidationError) as e:
        raise SignUpError(str(e))