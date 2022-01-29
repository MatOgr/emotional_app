import datetime
from email.policy import default
import pickle
from dateutil.relativedelta import relativedelta
import logging
from typing import Dict, Optional
from fastapi import FastAPI, Request, Form
from fastapi.routing import APIRouter
from fastapi.templating import Jinja2Templates
import requests
from starlette.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from model.Settings import Settings
from authentication import ActivateAccountError, AuthenticationRoute, SignUpError, UsernamePasswordError, authenticate, get_token, get_user_info, signup, activate_account
from model.report_model import report_model
from model.trends_model import trends_model
from report.cached_data import daily_data, emotion_record, monthly_data
from report.report_statistics import detect_day_series, detect_trends, get_key_dayofweek, get_key_daypart, get_key_flat, get_key_humidity, get_key_location, get_key_pressure, get_key_temperature, group_emotions
from report.cached_data import monthly_data
import json
from report.report_utils import get_daily_report_data, get_monthly_report_data
import os.path

logging.basicConfig(level=logging.INFO)
MONITOR_ENDPOINT_URL = 'http://monitor:8000'
app = FastAPI()
authentication_router = APIRouter(route_class=AuthenticationRoute)
userSettings = Settings()
cached_data: Dict[str, monthly_data] = {}

settings_path = "settings.pkl"
if os.path.isfile(settings_path):
    with open(settings_path, 'rb') as input:
        userSettings = pickle.load(input)

templates = Jinja2Templates(directory="templates/")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(HTTPException)
async def render_error(request, exc):
    return templates.TemplateResponse('error.html', context={'request': request, 'code': exc.status_code, 'message': str(exc.detail)})

@app.get('/login')
def login(request: Request, authenticationError: Optional[bool] = None):
    return templates.TemplateResponse('login.html', 
                                      context={'request': request, 
                                               'authenticationError': authenticationError})

@app.post('/login')
async def login(response: Response, username: str = Form(...), password: str = Form(...), redirectPath: str = '/'):
    try:
        authenticate(username, password)
    except UsernamePasswordError:
        return RedirectResponse('/login?authenticationError=true', status_code=302)
    
    return RedirectResponse(redirectPath, status_code=302)

@app.get('/register')
async def register(request: Request):
    message = request.headers.get('errorMessage', '')
    return templates.TemplateResponse('register.html', context={'request': request, 'message': message})

@app.get('/activate-account')
async def activate_account_page(request: Request, email: str = '', activationError: bool = False):
    return templates.TemplateResponse('accounts/confirm-account.html', context={'request': request, 'email': email, 'activationError': activationError})

@app.post('/activate-account')
async def activate_account_page(request: Request, email: str = Form(...), code: str = Form(...), redirectPath: str = '/login'):
    try:
        activate_account(email, code)
    except ActivateAccountError:
        return RedirectResponse('/activate-account?activationError=true&email=' + email, status_code=302)
    return RedirectResponse(redirectPath, status_code=302)
@app.post('/register')
async def register(request: Request, name: str = Form(...),
                   family_name: str = Form(...), 
                   preferred_username: str = Form(...), 
                   email: str = Form(...), 
                   birthdate: str = Form(...), 
                   zoneinfo: str = Form(...), 
                   password: str = Form(...)):
    try:
        signup(name=name,
                    family_name=family_name,
                    preferred_username=preferred_username,
                    email=email,
                    birthdate=birthdate,
                    zoneinfo=zoneinfo,
                    password=password)
        
        return RedirectResponse('/activate-account?email=' + email, status_code=302)
    except SignUpError as e:
        print(e)
        #return RedirectResponse('/register', status_code=302)
        return templates.TemplateResponse('register.html', context={'request': request, 'message': str(e)})

@authentication_router.get("/")
async def root(request: Request):
    user = get_user_info(get_token()['AccessToken'])
    return templates.TemplateResponse('index.html', context={'request': request, 'current_user': user})


@authentication_router.get("/settings")
async def Settings(request: Request):
    user = get_user_info(get_token()['AccessToken'])
    return templates.TemplateResponse('page-profile.html', context={'request': request, 'settings': userSettings, 'current_user': user})

@authentication_router.get("/report")
async def report(request: Request):
    user = get_user_info(get_token()['AccessToken'])
    return templates.TemplateResponse('report.html', context={'request': request, 'current_user': user})

@authentication_router.get("/monthly_report/{year}/{month}")
async def monthly_report(request: Request, year: int, month: int):
    period = datetime.datetime(year, month, 1)
    last = period + relativedelta(months=-1)
    next = period + relativedelta(months=1)
    user = get_user_info(get_token()['AccessToken'])
    emotions = get_monthly_report_data(month, year, cached_data)
    if emotions == -1:
        emotions_processed = []
    else:
        emotions_processed = report_model.parse_month_data(emotions, month, year)
    data = report_model(emotions = emotions_processed,
    month = month,
    year = year,
    last = str(last.year) + "/" + str(last.month),
    next = str(next.year) + "/" + str(next.month))
    return templates.TemplateResponse('monthly_report.html', context={'request': request, 'current_user': user, 'data': data})    

@authentication_router.get("/monthly_report")
async def monthly_report(request: Request):
    today = datetime.datetime.today()
    redirect_path = "/monthly_report/" + str(today.year) +"/"+ str(today.month)
    return RedirectResponse(redirect_path, status_code=302)

@authentication_router.get("/trends_report")
async def trends_report(request: Request):
    user = get_user_info(get_token()['AccessToken'])
    return templates.TemplateResponse('trends_options.html', context = { 'request': request, 'current_user': user })

@authentication_router.get("/monthly_trends/{type}")
async def monthly_report(request: Request, type: str):
    today = datetime.datetime.today()
    redirect_path = "/monthly_trends/" + str(today.year) +"/"+ str(today.month) + "/" + type
    return RedirectResponse(redirect_path, status_code=302)

@authentication_router.get("/monthly_trends/{year}/{month}/{type}")
async def monthly_report(request: Request, year: int, month: int, type:str):
    period = datetime.datetime(year, month, 1)
    last = period + relativedelta(months=-1)
    next = period + relativedelta(months=1)
    user = get_user_info(get_token()['AccessToken'])
            
    emotions = get_monthly_report_data(month, year, cached_data)
    data_counter = group_emotions(emotions, get_key_flat, False)
    if len(data_counter) == 0  or data_counter[0] < 32:
        data = trends_model(trends = [],
        month = month,
        year = year,
        last = str(last.year) + "/" + str(last.month),
        next = str(next.year) + "/" + str(next.month),
        type = type)
        return templates.TemplateResponse('trends_not_available.html', context={'request': request, 'current_user': user, 'data': data})        
    type_array = type.split("-")
    data = []
    match type_array[0]:
        case "daypart":
            data = detect_trends(emotions, get_key_daypart, 2)
        case "dayofweek":
            data = detect_trends(emotions, get_key_dayofweek, 2)
        case "location":
            data = detect_trends(emotions, get_key_location, 2)
        case "weather":
            if len(type_array) == 1:
                type_array.append("temperature")
            match type_array[1]:
                case "temperature":
                    data = detect_trends(emotions, get_key_temperature, 2)
                case "pressure":
                    data = detect_trends(emotions, get_key_pressure, 2)
                case "humidity":
                    data = detect_trends(emotions, get_key_humidity, 2)
        case "series":
            data = detect_day_series(emotions, 2, month)            
    
    model = trends_model(trends = data,
    month = month,
    year = year,
    last = str(last.year) + "/" + str(last.month),
    next = str(next.year) + "/" + str(next.month),
    type = type_array[0])

    return templates.TemplateResponse('monthly_trends.html', context={'request': request, 'current_user': user, 'data': model})    

@authentication_router.get("/daily_report/{year}/{month}/{day}")
async def monthly_report(request: Request, year: int, month: int, day: int):
    period = datetime.datetime(year, month, day)
    last = period + datetime.timedelta(days=-1)
    next = period + datetime.timedelta(days=1)
    user = get_user_info(get_token()['AccessToken'])
    emotions = get_daily_report_data(month, year, day, cached_data)
    data = report_model(emotions = report_model.parse_day_data(emotions),
    month = month,
    year = year,
    last = str(last.year) + "/" + str(last.month),
    next = str(next.year) + "/" + str(next.month))
    return templates.TemplateResponse('daily_report.html', context={'request': request, 'current_user': user, 'data': data})    

@authentication_router.get("/daily_report")
async def monthly_report(request: Request):
    today = datetime.datetime.today()
    redirect_path = "/daily_report/" + str(today.year) +"/"+ str(today.month) + "/" + str(today.day)
    return RedirectResponse(redirect_path, status_code=302)

@authentication_router.get("/change-user")
async def change_user(request: Request):
    user = get_user_info(get_token()['AccessToken'])
    return templates.TemplateResponse('login.html', context={'request': request, 'current_user': user})

@authentication_router.post("/save_settings")
async def save_settings(send_pictures: bool = Form(...), send_voice: bool = Form(...), location: str = Form(...), redirectPath: str = '/'):
    userSettings.send_pictures = send_pictures
    userSettings.send_voice = send_voice
    userSettings.location = location.split(" ", 2)   
    with open(settings_path, 'wb') as output:
        pickle.dump(userSettings, output, pickle.HIGHEST_PROTOCOL) 
    return RedirectResponse(redirectPath, status_code=302)

@authentication_router.post('/monitor-user')
async def monitor_user():
    logging.info("Data collection started...")
    tokens = get_token()
    user = get_user_info(tokens['AccessToken'])
    logging.info('[OK] User authenticated.')
    body = {
        'IdToken': tokens['IdToken'],
        'AccessToken': tokens['AccessToken'],
        'AccessKeyId': tokens['AccessKeyId'],
        'SecretKey': tokens['SecretKey'],
        'SessionToken': tokens['SessionToken'],
        'IdentityId': tokens['IdentityId'],
        'UserId': user.user_id,
        'location': userSettings.location
    }
    URL = MONITOR_ENDPOINT_URL + '/report-generation-requests'
    headers = {'Content-Type': 'application/json'}
    requests.post(url=URL, headers=headers, data=json.dumps(body))
    logging.info('[OK] Data sent to monitor app')
app.include_router(authentication_router)
