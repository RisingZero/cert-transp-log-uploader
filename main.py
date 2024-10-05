from datetime import datetime, date, timedelta
from iso_countries import iso_codes
from worker import fetch_index_records

DAY0 = date(2024, 5, 13)


def save_last_index(day, hour):
    with open("data/last_fetched", "w") as f:
        f.write(f"{day.isoformat()}\n{hour}")


def generate_record_indexes():
    try:
        with open("data/last_fetched", "r") as f:
            day, hour = (s.strip() for s in f.readlines())
            day = date.fromisoformat(day)
            hour = int(hour)
    except FileNotFoundError:
        day = DAY0
        hour = 0

    # up to today
    today_str = date.today().strftime("%Y%m%d")
    today_h = datetime.now().hour
    while day.strftime("%Y%m%d") < today_str:
        for h in range(hour, 24):
            for country in iso_codes:
                yield day, h, country
        hour = 0
        day += timedelta(days=1)

    # today
    for h in range(hour, today_h):
        for country in iso_codes:
            yield day, h, country


if __name__ == "__main__":
    for day, hour, country in generate_record_indexes():
        fetch_index_records.delay(day, hour, country)
    save_last_index(day, hour)
