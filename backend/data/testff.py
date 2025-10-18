import fastf1
from fastf1 import plotting

def test_fastf1_data(years=[2022, 2023, 2024]):
    fastf1.Cache.enable_cache("f1_cache")  # Cache results locally (creates folder)

    for year in years:
        print(f"\n=== Checking data for {year} ===")
        schedule = fastf1.get_event_schedule(year)
        
        if schedule.empty:
            print(f"⚠️ No schedule found for {year}")
            continue
        
        for _, event in schedule.iterrows():
            print(f"\n🏁 {event['EventName']} ({event['EventFormat']}) - {event['EventDate'].date()}")
            
            # Try to get session info
            try:
                for session_name in ['FP1', 'FP2', 'FP3', 'Q', 'R']:
                    try:
                        session = fastf1.get_session(year, event['EventName'], session_name)
                        session.load(laps=False, telemetry=False)  # lightweight metadata load
                        print(f"  ✅ {session_name} session loaded (SessionKey={session.session_info['SessionKey']})")
                    except Exception as e:
                        print(f"  ⚠️ {session_name} not available ({str(e)[:60]}...)")
            except Exception as e:
                print(f"⚠️ Error reading {event['EventName']}: {e}")

if __name__ == "__main__":
    test_fastf1_data()
