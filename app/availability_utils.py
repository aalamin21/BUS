from app import app

time_slots = [
    ('0900', '09:00 AM'),
    ('1000', '10:00 AM'),
    ('1100', '11:00 AM'),
    ('1200', '12:00 PM'),
    ('1300', '1:00 PM'),
    ('1400', '2:00 PM'),
    ('1500', '3:00 PM'),
    ('1600', '4:00 PM'),
    ('1700', '5:00 PM'),
    ('1800', '6:00 PM')
]

days = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday')
]

def default_av(bool):
    return [1 if bool else 0] * len(days) * len(time_slots)

def flatten_availability(availability):
    vector = []
    for day_code, day_name in days:
        for time_code, time_name in time_slots:
            vector.append(1 if availability[day_code][time_code] else 0)
    return vector

def group_availability(*avs):
    avs = list(map(list, avs))
    length = len(avs[0])
    return [int(all(av[i] for av in avs)) for i in range(length)]

def av_vec_to_dict(av):
    if len(av) != len(days)*len(time_slots):
        app.logger.error('Incorrect availability format')
        return
    idx = 0
    av_dict = {}
    for day_code, day in days:
        av_dict[day_code] = {}
        for time_code, time_name in time_slots:
            av_dict[day_code][time_code] = bool(av[idx])
            idx += 1

    return av_dict

app.jinja_env.globals.update(av_vec_to_dict=av_vec_to_dict)