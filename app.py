import datetime
import schedule
import time
import os
import requests

from dotenv import load_dotenv

load_dotenv()
SKIP_DATES = ["2025-04-07", "2025-04-08", "2025-04-09", "2025-04-10", "2025-04-11", "2025-04-14", "2025-04-15", "2025-04-16", "2025-04-17", "2025-04-18", "2025-04-21", "2025-05-01", "2025-05-02", "2025-05-29", "2025-05-30", "2025-06-05", "2025-06-06"]  # Add your skippable dates here
NTFY_SERVER = os.getenv("NTFY_SERVER")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

def is_weekend(date):
    # Returns True if the given date falls on a weekend (Saturday or Sunday)
    return date.weekday() in [5, 6]

def is_skippable_date(date):
    # Returns True if the given date should be skipped based on the settings
    return date.strftime("%Y-%m-%d") in SKIP_DATES

def notify(remain):
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.time()
    today_date = current_datetime.date()

    # Check if it's between 08:00 and 08:30 and it hasn't been run today (fuck codespaces running in UTC/CET-1)
    if datetime.time(12, 0) <= current_time <= datetime.time(14, 30):
        last_run_date = None

        # Read the last run date from the file
        try:
            with open('lastrun.txt', 'r') as file:
                last_run_date_str = file.readline().strip()
                last_run_date = datetime.datetime.strptime(last_run_date_str, "%Y-%m-%d").date()
        except FileNotFoundError:
            pass

        # If the last run date is not today, run it?
        if last_run_date != today_date:
            print("Notification sent at", current_datetime.strftime("%Y-%m-%d %H:%M:%S"))
            
            # send ntfy notification :thumbsup:
            if NTFY_SERVER:

                requests.post("https:// " + NTFY_SERVER + "/" + NTFY_TOPIC,
                    data="Snart slipper vi skolan i 10 veckor.",
                    headers={ "Title": "Endast x dagar kvar tills sommarlov!" , "Tags": "tada,sommarlov" })

                if response.status_code == 200:
                    print("Notification successfully sent to", NTFY_SERVER)
                else:
                    print("Failed to send notification to", NTFY_SERVER)
            else:
                print("NTFY_SERVER variable is not set in the .env file")

            # Update the last run date in the file to today's date
            with open('lastrun.txt', 'w') as file:
                file.write(today_date.strftime("%Y-%m-%d"))

    return True

def count_working_days(start_date, end_date):
    current_date = start_date
    count = 0
    while current_date <= end_date:
        if not is_weekend(current_date) and not is_skippable_date(current_date):
            count += 1
        current_date += datetime.timedelta(days=1)
    return count

def main():
    start_date = datetime.datetime.now()
    end_date = datetime.datetime(2025, 6, 12)
    working_days = count_working_days(start_date, end_date)
    
    print("Number of working days between", start_date.strftime("%Y-%m-%d"), "and", end_date.strftime("%Y-%m-%d"), ":", working_days-1)
    notify(working_days)

# create the schedule to run every 5 minutes.
schedule.every(5).seconds.do(main)

# run the scheduler loop
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
