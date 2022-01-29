from typing import Dict, List

class emotion_record:
    emotion: str
    weather: Dict[str, str]
    def __init__(self, emotion: str, weather: Dict[str, str]):
        self.emotion = emotion
        self.weather = weather

class hourly_data:
    records: Dict[float, emotion_record]
    top: str    

    def find_top(self):
        emotions = {}
        for id in self.records:
            record = self.records[id].emotion
            if record != "UNKNOWN":
                if record in emotions:
                    emotions[record] += 1
                else:
                    emotions[record] = 1
        if len(emotions) > 0:
            self.top = max(emotions, key=emotions.get)
        else:
            self.top = "UNKNOWN"
    def __init__(self):
        self.records = {0: emotion_record("UNKNOWN", {})}


class daily_data:
    records: List[hourly_data]
    top: str
    def find_top(self):
        emotions = {}
        for hour in self.records:
            for id in hour.records:
                record = hour.records[id].emotion
                if record != "UNKNOWN":
                    if record in emotions:
                        emotions[record] += 1
                    else:
                        emotions[record] = 1
        if len(emotions) > 0:
            self.top = max(emotions, key=emotions.get)
        else:
            self.top = "UNKNOWN"
    
    def __init__(self):
        self.records = []
        for _ in range(0, 24):            
            self.records.append(hourly_data())

class monthly_data:
    records: List[daily_data]
    top: str

    def __init__(self, size: int):
        self.records = []
        for _ in range(0, size):            
            self.records.append(daily_data())

    def find_top(self):
        emotions = {}
        for day in self.records:
            for hour in day:
                for id in hour.records:
                    record = hour.records[id].emotion
                    if record != "UNKNOWN":
                        if record in emotions:
                            emotions[record] += 1
                        else:
                            emotions[record] = 1
        self.top = max(self.records, key=self.records.get)
