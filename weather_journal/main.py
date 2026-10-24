
import requests

geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
weather_url = "https://api.open-meteo.com/v1/forecast"
air_quality_url = "https://air-quality-api.open-meteo.com/v1/air-quality"


class WeatherAPI:
    def get_weather(self, city):
        try:
            search = {"name": city, "count": 1}
            response = requests.get(
                geocoding_url, params=search, timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("results"):
                return None, "City not found", None

            latitude = data["results"][0]["latitude"]
            longitude = data["results"][0]["longitude"]

            coordinates = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,weather_code"
            }

            response = requests.get(
                weather_url, params=coordinates, timeout=10
            )
            response.raise_for_status()
            weather_data = response.json()

            temperature = weather_data["current"]["temperature_2m"]
            weather_code = weather_data["current"]["weather_code"]

            if weather_code == 0:
                condition = "Clear Sky"
            elif weather_code == 1:
                condition = "Mainly clear"
            elif weather_code == 2:
                condition = "Partly cloudy"
            elif weather_code == 3:
                condition = "Overcast"
            elif weather_code in (45, 48):
                condition = "Fog"
            elif weather_code in (51, 53, 55, 56, 57):
                condition = "Drizzle"
            elif weather_code in (61, 63, 65, 66, 67):
                condition = "Rain"
            elif weather_code in (71, 73, 75, 77):
                condition = "Snow"
            elif weather_code in (80, 81, 82):
                condition = "Rain showers"
            elif weather_code in (95, 96, 99):
                condition = "Thunderstorm"
            else:
                condition = "Unknown condition"

            # Fetch AQI
            aqi = None
            try:
                aqi_params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "us_aqi"
                }

                response = requests.get(
                    air_quality_url, params=aqi_params, timeout=10
                )
                response.raise_for_status()
                aqi_data = response.json()
                aqi = aqi_data["current"]["us_aqi"]

            except (requests.exceptions.RequestException, KeyError, TypeError):
                pass

            return temperature, condition, aqi

        except requests.exceptions.Timeout:
            return None, "Request timed out", None

        except requests.exceptions.ConnectionError:
            return None, "Internet connection error", None

        except requests.exceptions.RequestException:
            return None, "Weather service error", None

        except (KeyError, IndexError, TypeError, ValueError):
            return None, "Unexpected API response", None


def main():
    print("=== Weather App ===")
    weather = WeatherAPI()

    while True:
        city = input("\nEnter city (or 'exit' to quit): ").strip()

        if city.lower() == "exit":
            print("Weather App closed.")
            break

        if not city:
            print("Please enter a city name.")
            continue

        temperature, condition, aqi = weather.get_weather(city)

        if temperature is None:
            print("Error:", condition)
            continue

        print("\nCity:", city.title())
        print("Temperature:", temperature, "°C")
        print("Condition:", condition)

        if aqi is not None:
            if aqi <= 50:
                category = "Good"
            elif aqi <= 100:
                category = "Moderate"
            elif aqi <= 150:
                category = "Unhealthy for Sensitive Groups"
            elif aqi <= 200:
                category = "Unhealthy"
            elif aqi <= 300:
                category = "Very Unhealthy"
            else:
                category = "Hazardous"

            print("AQI:", aqi)
            print("Air Quality:", category)
        else:
            print("AQI is currently unavailable.")


if __name__ == "__main__":
    main()
