import datetime
import schedule
import time
import os
import requests

from dotenv import load_dotenv

load_dotenv()
SKIP_DATES = os.getenv("SKIP_DATES")
NTFY_SERVER = os.getenv("NTFY_SERVER")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
LAST_RUNTIME = ""

def is_weekend(date):
    # Returns True if the given date falls on a weekend (Saturday or Sunday)
    return date.weekday() in [5, 6]

def is_skippable_date(date):
    # Returns True if the given date should be skipped based on the settings
    return date.strftime("%Y-%m-%d") in SKIP_DATES

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
