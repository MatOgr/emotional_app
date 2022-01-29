from typing import Optional
from pydantic import BaseModel

class Weather(BaseModel):
    temperature: str
    location: str
    description: str
    pressure: int
    humidity: int

class GenerateReportRequest(BaseModel):
    IdToken: str
    AccessToken: str
    AccessKeyId: str
    SecretKey: str
    SessionToken: str
    UserId: str
    IdentityId: str
    location: str
    
class Metadata(BaseModel):
    time: int
    recordID: str
    userId: str
    weather: Optional[Weather]
    