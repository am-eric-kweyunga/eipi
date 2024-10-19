# Weather API using " Eipi DSP "
## Overview
The **Weather API** allows you to fetch current weather information for Tanzania using data from an external weather service. This API uses the WeatherAPI service to provide up-to-date weather conditions.

## Endpoint
- Route: ``/eipi/weather``
- Method: ``GET``

## Description
This API returns the current weather data for Tanzania by making a GET request to the WeatherAPI service.

## Response
### Successful Response (Status 200)
When the request is successful, the API will return the following:
```
{
    "status": 200,
    "location": {
        "name": "Dodoma",
        "region": "Dodoma",
        "country": "Tanzania",
        "lat": -6.183,
        "lon": 35.75,
        "tz_id": "Africa/Dar_es_Salaam",
        "localtime_epoch": 1729307687,
        "localtime": "2024-10-19 06:14"
    },
    "current": {
        "last_updated_epoch": 1729306800,
        "last_updated": "2024-10-19 06:00",
        "temp_c": 18.9,
        "temp_f": 66.1,
        "is_day": 0,
        "condition": {
            "text": "Clear",
            "icon": "//cdn.weatherapi.com/weather/64x64/night/113.png",
            "code": 1000
        },
        "wind_mph": 6.0,
        "wind_kph": 9.7,
        "wind_degree": 75,
        "wind_dir": "ENE",
        "pressure_mb": 1013.0,
        "pressure_in": 29.92,
        "precip_mm": 0.0,
        "precip_in": 0.0,
        "humidity": 86,
        "cloud": 11,
        "feelslike_c": 18.9,
        "feelslike_f": 66.1,
        "windchill_c": 18.9,
        "windchill_f": 66.1,
        "heatindex_c": 18.9,
        "heatindex_f": 66.1,
        "dewpoint_c": 16.5,
        "dewpoint_f": 61.7,
        "vis_km": 10.0,
        "vis_miles": 6.0,
        "uv": 0.0,
        "gust_mph": 9.8,
        "gust_kph": 15.8
    }
}

```




