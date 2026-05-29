import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("PURPLEAIR_READ_KEY")

SENSOR_IDS = [289280, 161159, 276512, 161015]

def get_sensor_history(sensor_id, days=180):
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    
    url = "https://api.purpleair.com/v1/sensors/{}/history".format(sensor_id)
    headers = {"X-API-Key": API_KEY}
    params = {
        "start_timestamp": int(start.timestamp()),
        "end_timestamp": int(end.timestamp()),
        "average": 1440,
        "fields": "pm2.5_atm"
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    if "data" not in data:
        print(f"Sensor {sensor_id} error: {data}")
        return pd.DataFrame()
    
    df = pd.DataFrame(data["data"], columns=["timestamp", "pm25"])
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
    df["sensor_id"] = sensor_id
    return df

def get_all_data(days=180):
    dfs = []
    for sid in SENSOR_IDS:
        try:
            df = get_sensor_history(sid, days)
            if not df.empty:
                dfs.append(df)
        except Exception as e:
            print(f"Error fetching sensor {sid}: {e}")
    
    if not dfs:
        return pd.DataFrame()
    
    combined = pd.concat(dfs)
    daily = combined.groupby("datetime")["pm25"].mean().reset_index()
    daily.columns = ["date", "pm25"]
    daily["pm25"] = daily["pm25"].round(1)
    return daily

def get_aqi_category(pm25):
    if pm25 <= 12: return "Good"
    elif pm25 <= 35.4: return "Moderate"
    elif pm25 <= 55.4: return "Unhealthy for Sensitive Groups"
    elif pm25 <= 150.4: return "Unhealthy"
    else: return "Very Unhealthy"

def get_aqi_color(pm25):
    if pm25 <= 12: return "#639922"
    elif pm25 <= 35.4: return "#EF9F27"
    elif pm25 <= 55.4: return "#D85A30"
    elif pm25 <= 150.4: return "#A32D2D"
    else: return "#791F1F"