import datetime
from pickle import TRUE
from xmlrpc.client import boolean
from report.cached_data import monthly_data

def group_emotions(data: monthly_data, get_key, include_emotion_in_key: boolean):
    emotions = {}
    if data != -1:
        for day in data.records:
                for hour in day.records:
                    for id in hour.records:
                        record = hour.records[id].emotion
                        if include_emotion_in_key:
                            key = (record, get_key(id, hour.records))
                        else:
                            key = get_key(id, hour.records)
                        if record != "UNKNOWN":
                            if key in emotions:
                                emotions[key] += 1
                            else:
                                emotions[key] = 1
    return emotions

def get_key_flat(record, list):
    return 0

def get_key_daypart(record, list):    
    hour = datetime.datetime.fromtimestamp(record).hour
    if hour < 7 or hour > 23:
        daypart = "Night(23:00-07:00)"
    elif hour < 13:
        daypart = "Morning(07:00-13:00)"
    elif hour < 18:
        daypart = "Afternoon(13:00-18:00)"
    else:
        daypart = "Evening(18:00-23:00)"
    return daypart

def get_key_dayofweek(record, list):    
    return datetime.datetime.fromtimestamp(record).strftime('%A')

def get_key_location(record, list):
    if "location" not in list[record].weather:
        return "Unknown"
    return list[record].weather["location"]

def get_key_temperature(record, list):
    if "temperature" not in list[record].weather:
        return "Unknown"
    value = round(list[record].weather["temperature"]/5, 0)*5
    return str(value) + "-" + str(value + 5)

def get_key_humidity(record, list):
    if "humidity" not in list[record].weather:
        return "Unknown"
    value = round(list[record].weather["humidity"]/10, 0)*10
    return str(value) + "-" + str(value + 10)

def get_key_pressure(record, list):
    if "pressure" not in list[record].weather:
        return "Unknown"
    value = round((list[record].weather["pressure"] - 900)/20, 0)*20+900
    return str(value) + "-" + str(value + 20)

def detect_trends(data: monthly_data, selector, strictness: int):
    emotions = group_emotions(data, selector, True)     
    reference_data = group_emotions(data, selector, False)
    expected = sum(emotions.values()) / float(len(emotions))
    trends = {k: v for k, v in emotions.items() if v > strictness * expected}    
    return [(k[0], k[1], round(v*100 / reference_data[k[1]], 2)) for k, v in sorted(trends.items(), key=lambda item: item[1], reverse = True)]


def detect_hour_series(data: monthly_data, strictness: int):
    current_emotion = "UNKNOWN"
    current_series = 0
    series = []
    for day in data.records:
            for hour in day:
                hour.find_top()
                if current_emotion == hour.top:
                    current_series+=1
                elif current_series > strictness:
                    series.append((current_emotion, current_series))                
    return [(k[0], k[1], v) for k, v in sorted(series.items(), key=lambda item: item[1], reverse=TRUE)]

def detect_day_series(data: monthly_data, strictness: int, month: int):
    current_emotion = "UNKNOWN"
    current_series = 1
    series = []
    start = 0
    end = 0
    for i in range(0, len(data.records)):
        day = data.records[i]
        day.find_top()
        if current_emotion == day.top:
            current_series+=1
        else:                       
            end = i
            if current_series > strictness and current_emotion != "UNKNOWN":
                month = str(month).zfill(2)
                period = str(start+1).zfill(2) + "." + month + "-" + str(end).zfill(2) + "." + month
                series.append((current_emotion, period, current_series))                
            start = i
            current_series = 1
            current_emotion = day.top 
    return sorted(series, key=lambda tup: tup[1], reverse=TRUE)
