from app.models import *
from app.forms import RegistrationForm
def test_valid_user_registration():
    form = RegistrationForm()
    user = User(
        first_name="James",
        last_name="Smith",
        email="James_Smith@example.com",
        faculty="life science",
        course_name="medicine",
        year_of_study="First Year",
        password="password",
        availability=default_av()
    )
    assert "@" in user.email
    assert (user.course_name, user.course_name) in form.course_name.choices
