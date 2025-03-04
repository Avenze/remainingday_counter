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

def send_notification(days):
    if NTFY_SERVER:

        STRING = "Endast " + days + " dagar kvar tills sommarlov!"
        requests.post("https:// " + NTFY_SERVER + "/" + NTFY_TOPIC,
            data="Snart slipper vi skolan i 10 veckor.",
            headers={ "Title": STRING, "Tags": "tada,sommarlov" })

        if response.status_code == 200:
            print("SUC: Notification successfully sent to", NTFY_SERVER)
        else:
            print("ERR: NTFY_SERVER errored, using server: ", NTFY_SERVER)
        
    else:
        print("ERR: NTFY_SERVER variable is not set in the .env file")


def run_function(days):
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.time()
    today_date = current_datetime.date()

    # Check if it's between 08:00 and 08:30 and it hasn't been run today (fuck codespaces running in UTC/CET-1)
    if datetime.time(12, 0) <= current_time <= datetime.time(14, 30):

        # Read the last run date from memory
        if LAST_RUNTIME == "":
            print("INF: Sending notification due to container startup at: ", current_datetime.strftime("%Y-%m-%d %H:%M:%S"))
            send_notification(days)
        else:
            last_rundate = datetime.datetime.strptime(LAST_RUNTIME, "%Y-%m-%d").date()
            if last_run_date != today_date:
                print("INF: Sending notification due to new day: ", current_datetime.strftime("%Y-%m-%d %H:%M:%S"))
                send_notification(days)

        # Update the last run date in the file to today's date
        LAST_RUNETIME = today_date.strftime("%Y-%m-%d"))

    return True

def main():
    start_date = datetime.datetime.now()
    end_date = datetime.datetime(2025, 6, 12)
    working_days = count_working_days(start_date, end_date)
    
    print("INF: Number of working days between", start_date.strftime("%Y-%m-%d"), "and", end_date.strftime("%Y-%m-%d"), ":", working_days-1)
    run_function(working_days)

# create the schedule to run every 5 minutes.
schedule.every(5).seconds.do(main)

# run the scheduler loop
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(30)
