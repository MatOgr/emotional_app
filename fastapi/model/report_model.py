from pydantic import BaseModel
from typing import Any, List
import datetime
from report.cached_data import monthly_data

from report.report_utils import transform_emotions_to_emojis

class day_data(BaseModel):
    emotion: str
    day: str
    text: str

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)

class report_model(BaseModel):
    month: str
    year: str
    emotions: List
    last: str
    next: str
    class Config:        
        arbitrary_types_allowed = True

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)

    @staticmethod
    def parse_month_data(emotions: monthly_data, month: int, year: int):
        day_of_month = datetime.datetime(year, month, 1)
        week: List[day_data] = []
        month: List[List[day_data]] = []
        for _ in range(0, day_of_month.weekday()):
            week.append(day_data(emotion = "", day = "", text = ""))
        for day in emotions.records:
            day.find_top()
            week.append(day_data(emotion = transform_emotions_to_emojis(day.top),
                                day = day_of_month.day,
                                text = day.top))
            day_of_month =  day_of_month + datetime.timedelta(days=1)
            if len(week) == 7:
                month.append(week)
                del week
                week: List[day_data] = []
        while len(week) < 7:
            week.append(day_data(emotion = "", day = "", text = ""))
        month.append(week)
        return month

    @staticmethod
    def parse_day_data(emotions: List[str]):
        data = []
        i = 0
        for emotion in emotions:
            data.append(day_data(emotion = transform_emotions_to_emojis(emotion),
                                day = str(i).zfill(2)+":00",
                                text = emotion))
            i+=1
        return data