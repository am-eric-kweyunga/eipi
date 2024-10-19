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
    "data": {
        "location": {
            "name": "Dar es Salaam",
            "region": "Dar es Salaam",
            "country": "Tanzania",
            "lat": -6.82,
            "lon": 39.28,
            "tz_id": "Africa/Dar_es_Salaam",
            "localtime": "2024-10-19 11:00"
        },
        "current": {
            "temp_c": 30.0,
            "condition": {
                "text": "Sunny",
                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png"
            },
            "wind_kph": 13.0,
            "humidity": 62,
            "feelslike_c": 32.5
        }
    }
}

```




