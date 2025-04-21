
from app.models import *
from app.forms import RegistrationForm
def test_default_availability_all_false():
    av = default_av()
    for day in av:
        for time in av[day]:
            assert av[day][time] is False
