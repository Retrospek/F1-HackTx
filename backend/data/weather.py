import requests

SESSION_URL = "https://api.openf1.org/v1/sessions"
WEATHER_URL = "https://api.openf1.org/v1/weather"

def get_cota_weather_data(years=[2022, 2023, 2024], circuit_short_name="Austin"):
    for year in years:
        print(f"\n================ YEAR {year} ================\n")

        # Step 1: Fetch sessions for the given year in the US
        session_params = {
            "country_name": "United States",
            "year": year
        }
        sessions = requests.get(SESSION_URL, params=session_params).json()

        # Filter for Circuit of the Americas (Austin)
        cota_sessions = [s for s in sessions if circuit_short_name.lower() in (s.get("circuit_short_name") or "").lower()]

        if not cota_sessions:
            print(f"No sessions found for {circuit_short_name} in {year}.")
            continue

        print(f"Found {len(cota_sessions)} sessions at {circuit_short_name}:")

        # Step 2: Loop through all sessions
        for i, session in enumerate(cota_sessions, start=1):
            print(f"\n--- Session {i}: {session.get('session_name')} ---")
            print(f"circuit_key: {session.get('circuit_key')}")
            print(f"circuit_short_name: {session.get('circuit_short_name')}")
            print(f"country_code: {session.get('country_code')}")
            print(f"country_key: {session.get('country_key')}")
            print(f"country_name: {session.get('country_name')}")
            print(f"date_start: {session.get('date_start')}")
            print(f"date_end: {session.get('date_end')}")
            print(f"gmt_offset: {session.get('gmt_offset')}")
            print(f"location: {session.get('location')}")
            print(f"meeting_key: {session.get('meeting_key')}")
            print(f"session_key: {session.get('session_key')}")
            print(f"session_name: {session.get('session_name')}")
            print(f"session_type: {session.get('session_type')}")
            print(f"year: {session.get('year')}")

            # Step 3: Fetch weather data for this session
            weather_params = {"session_key": session.get("session_key")}
            weather_data = requests.get(WEATHER_URL, params=weather_params).json()

            if not weather_data:
                print("No weather data available for this session.\n")
                continue

            print("\nWeather Data Sample:")
            for w in weather_data[:5]:  # Show just a few samples
                print(w)

get_cota_weather_data()
