from datetime import datetime
from calendar import monthrange
import time
from typing import Any, Dict, List
import json
from authentication import get_token

import boto3

from report.cached_data import emotion_record, monthly_data
def transform_emotions_to_emojis(emotion: str):
    match emotion:
        case "HAPPY":
            return "fas fa-smile"
        case "SAD":
            return "fas fa-frown"
        case "ANGRY":
            return "fas fa-angry"
        case "CONFUSED":
            return "fas fa-flushed"
        case "DISGUSTED":
            return "fas fa-grin-tongue-squint"
        case "SURPRISED":
            return "fas fa-surprise"
        case "CALM":
            return "fas fa-meh-blank"
        case "UNKNOWN":
            return "fas fa-question"
        case "FEAR":
            return "fas fa-grimace"
def get_monthkey(date: datetime):
    return str(date.year) + '-' + str(date.month)

class temporary_record:
    date: float
    emotion: str
    confidence: int
    weather: Dict[str, str]
    def __init__(self) -> None:
        self.emotion = "UNKNOWN"
        self.confidence = 0
        self.weather = {}


def parse_dynamoDB_records(data):
    result_data = {}    
    for record in data:
        id = record["recordID"][0:60]
        if id not in result_data:
            result_data[id] = temporary_record()
            result_data[id].date = record["time"]
        if "emotion" in record:
            if record["confidence"] > result_data[id].confidence:
                result_data[id].emotion = record["emotion"]
        if "weather" in record:
            result_data[id].weather = record["weather"]
    return result_data

def cache_report_data(storage: Dict[str, monthly_data], db_data):
    data = parse_dynamoDB_records(db_data)
    for reading in data:
        record = data[reading]
        date = datetime.fromtimestamp(record.date)
        month = get_monthkey(date)
        if not month in storage:
            storage[month] = monthly_data(monthrange(date.year, date.month)[1])
        storage[month].records[date.day-1].records[date.hour].records[record.date] = emotion_record(record.emotion, record.weather)

def get_monthly_report_data(month: int, year: int, storage: Dict[str, monthly_data]):
    today = datetime.today()
    tokens = get_token()

    lambda_client = boto3.Session(aws_access_key_id=tokens['AccessKeyId'], 
                       aws_secret_access_key=tokens['SecretKey'], 
                       aws_session_token=tokens['SessionToken']).client('lambda', 'eu-central-1')
    
    if not str(year)+'-'+str(month) in storage or (year == today.year and month == today.month):
        dt = datetime(year=year, month=month, day=1)
        response = lambda_client.invoke(
            FunctionName='emotional-app-again-FetchDBFunction-UVptS7ZJCDME',
            Payload=json.dumps({
                'timestamp ': time.mktime(dt.timetuple()),
                'userID': get_token()
            })
        )
        response_data = json.loads(response['Payload'].read().decode())
        cache_report_data(storage, response_data)
    if str(year)+'-'+str(month) in storage: 
        data = storage[str(year)+'-'+str(month)]    
    else:
        data = -1
    return data

def get_daily_report_data(month: int, year: int, day: int, storage: Dict[str, monthly_data]):
    today = datetime.today()
    if not str(year)+'-'+str(month) in storage or (year == today.year and month == today.month):
        dt = datetime(year=year, month=month, day=1)
        
        tokens = get_token()
        lambda_client = boto3.Session(aws_access_key_id=tokens['AccessKeyId'], 
                       aws_secret_access_key=tokens['SecretKey'], 
                       aws_session_token=tokens['SessionToken']).client('lambda', 'eu-central-1')
        
        response = lambda_client.invoke(
            FunctionName='emotional-app-again-FetchDBFunction-UVptS7ZJCDME',
            Payload=json.dumps({
                'timestamp ': time.mktime(dt.timetuple()),
                'userID': get_token()
            })
        )
        response_data = json.loads(response['Payload'].read().decode())
        cache_report_data(storage, response_data)
    data = []
    if str(year)+'-'+str(month) in storage: 
        for record in storage[str(year)+'-'+str(month)].records[day-1].records:
            record.find_top()
            data.append(record.top)
    return data