import datetime
import schedule
import time
import os
import requests

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Define global environment and non static variables
global SKIP_DATES
global NTFY_SERVER
global NTFY_TOPIC

SKIP_DATES = os.getenv("SKIP_DATES")
NTFY_SERVER = os.getenv("NTFY_SERVER")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

# Function to check if the date passed is a weekend
# @param date: The date which you want to check
def is_weekend(date):
    # Returns True if the given date falls on a weekend (Saturday or Sunday)
    return date.weekday() in [5, 6]

# Function to check if the date passed is a skippable date
# @param date: The date which you want to check
def is_skippable_date(date):
    # Returns True if the given date should be skipped based on the settings
    return date.strftime("%Y-%m-%d") in SKIP_DATES

# Function to count the remaining days from the start and end date
# @param start_date: The date which you want to start counting from
# @param end_date: The date which you want to stop counting at
def count_working_days(start_date, end_date):
    current_date = start_date
    count = 0
    while current_date <= end_date:
        if not is_weekend(current_date) and not is_skippable_date(current_date):
            count += 1
        current_date += datetime.timedelta(days=1)
    return count

# Function to send the notification using Ntfy to the clients
# @param days: The amount of remaining days
def send_notification(days):
    if NTFY_SERVER:

        STRING = "Endast " + str(days) + " dagar kvar tills sommarlov!"
        response = requests.post(NTFY_SERVER + "/" + NTFY_TOPIC,
            data="Snart slipper vi skolan i 10 veckor.",
            headers={ "Title": STRING, "Tags": "tada,sommarlov" })

        if response.status_code == 200:
            print("SUC: Notification successfully sent to", NTFY_SERVER, flush=True)
        else:
            print("ERR: NTFY_SERVER errored, using server: ", NTFY_SERVER, flush=True)
        
    else:
        print("ERR: NTFY_SERVER variable is not set in the .env file", flush=True)


if __name__ == "__main__":
    print("INF: Starting the main scheduler loop...", flush=True)
    start_date = datetime.datetime.now()
    end_date = datetime.datetime(2025, 6, 12)
    working_days = count_working_days(start_date, end_date)
    
    print("INF: Number of working days between", start_date.strftime("%Y-%m-%d"), "and", end_date.strftime("%Y-%m-%d"), ":", working_days-1, flush=True)
    send_notification(working_days)
