import datetime
import settings
import schedule
import time

def is_weekend(date):
    # Returns True if the given date falls on a weekend (Saturday or Sunday)
    return date.weekday() in [5, 6]

def is_skippable_date(date):
    # Returns True if the given date should be skipped based on the settings
    return date.strftime("%Y-%m-%d") in settings.SKIP_DATES

def save_last_run_date(date):
    # Save the last run date to a file
    with open('last_run_date.txt', 'w') as file:
        file.write(date.strftime("%Y-%m-%d"))

def load_last_run_date():
    # Load the last run date from the file
    try:
        with open('last_run_date.txt', 'r') as file:
            return datetime.datetime.strptime(file.readline().strip(), "%Y-%m-%d").date()
    except FileNotFoundError:
        return None

def count_down(start_date, days_to_skip):
    current_date = start_date
    remaining_days = days_to_skip
    while remaining_days > 0:
        if not is_weekend(current_date) and not is_skippable_date(current_date):
            remaining_days -= 1
        current_date -= datetime.timedelta(days=1)
    return current_date

def main():
    now = datetime.datetime.now()
    current_time = now.time()
    today = now.date()

    # Check if the current time is between 08:00 and 08:30
    if current_time >= datetime.time(14, 0) and current_time <= datetime.time(14, 30):
        last_run_date = load_last_run_date()

        # Check if main() has already been run for the day
        if last_run_date != today:
            start_date = today
            remaining_days = 42
            end_date = count_down(start_date, remaining_days)
            save_last_run_date(today)
            print("Countdown from", start_date.strftime("%Y-%m-%d"), "to", end_date.strftime("%Y-%m-%d"))
        else:
            print("Already ran main() for today")
    else:
        print("Done for the day.")

# Schedule main() function to run every 5 minutes
#schedule.every(5).minutes.do(main)

# Run the scheduler loop
#while True:
#    schedule.run_pending()
#    time.sleep(1)

if __name__ == "__main__":
    main()