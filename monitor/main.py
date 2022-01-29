import threading
import logging
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from starlette.responses import Response
import datetime
import pytz
from audio import record_voice
from facerecognition import process_face
from model import GenerateReportRequest, Metadata
import random
from audio import process_voice
from weather import process_weather
import requests
import json

app = FastAPI()
logging.basicConfig(level=logging.INFO)
def generate_metadata(request: GenerateReportRequest) -> Metadata:
    dtime = datetime.datetime.now()
    timezone_name = get_user_timezone(request.IdToken)
    timezone = pytz.timezone(timezone_name)
    dtz = timezone.localize(dtime)
    timestamp = str(int(dtz.timestamp()))
    
    id = request.UserId + '_' + timestamp + '_' + str(random.randint(10000000, 1000000000000))
    logging.info('[OK] Metadata generated.')
    return Metadata(time=timestamp, location=request.location, recordID=id, userId=request.UserId)

def post_metadata(metadata: Metadata, idtoken: str):
    logging.info("Putting item in the database...")
    URL = "https://xotfdzx3ue.execute-api.eu-central-1.amazonaws.com/Prod/metadata"
    headers = {
        "Authorization": idtoken,
        "Content-Type": "application/json"
    }
    response = requests.post(URL, json=jsonable_encoder(metadata), headers=headers)
    print(response)
    logging.info('[OK] Data posted in the database.')

def get_user_timezone(id_token: str):
    # TODO
    return "Europe/Warsaw"

def generate_report(request: GenerateReportRequest):
    logging.basicConfig(level=logging.INFO)
    metadata = generate_metadata(request)
    logging.info("timestamp" + str(metadata.time))
    process_face(metadata, request)
    process_voice(metadata, request)
    process_weather(metadata, request)
    post_metadata(metadata, idtoken=request.IdToken)

@app.post("/report-generation-requests")
def generate_report_endpoint(request: GenerateReportRequest):
    
    th = threading.Thread(target=generate_report, args=(request, ))
    th.start()
    logging.info("Started scanning...")
    
    return Response(status_code=201)