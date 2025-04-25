DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TIMES = ["09", "10", "11", "12", "13", "14", "15", "16", "17", "18"]

day_map = {
    "monday": "Mon", "tuesday": "Tue", "wednesday": "Wed",
    "thursday": "Thu", "friday": "Fri", "saturday": "Sat", "sunday": "Sun"
}

def flatten_availability(availability):
    vector = []

    # Lowercase and normalize all keys up front
    normalized_avail = {}
    for raw_day, slots in availability.items():
        short_day = day_map.get(raw_day.lower(), raw_day[:3].capitalize())
        normalized_avail[short_day] = {}
        for raw_time, is_free in slots.items():
            if isinstance(raw_time, str) and len(raw_time) == 4 and raw_time.endswith("00"):
                hour = raw_time[:2]
            elif isinstance(raw_time, str) and raw_time in TIMES:
                hour = raw_time
            else:
                hour = None

            if hour in TIMES:
                normalized_avail[short_day][hour] = is_free

    # Now construct the vector
    for day in DAYS:
        for hour in TIMES:
            vector.append(1 if normalized_avail.get(day, {}).get(hour, False) else 0)

    return vector



