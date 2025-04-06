from app import db
from app.models import User
import datetime


def reset_db():
    db.drop_all()
    db.create_all()

    users =[
        {'first_name': 'Amelia', 'last_name':'Carter', 'email': 'amelia.carter01@example.com',
         'faculty': "Life Sciences", 'course_name':'Medicine and Surgery MBChB', 'year_of_study':'First Year',
         'password':'A123'},
        {'first_name': 'Daniel', 'last_name': 'Mensah', 'email': 'daniel.mensah@example.com',
        'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
        'password': 'D123'},
        {'first_name': 'Priya', 'last_name': 'Shah', 'email': 'priya.shah@example.com',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'P123'},
        {'first_name': 'James', 'last_name': 'O’Connell', 'email': 'james.oconnell@example.com',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'J123'},
        {'first_name': 'Thandi', 'last_name': 'Mokoena', 'email': 'thandi.mokoena@example.com',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'T123'}
            ]




    for u in users:
        u = User(**u)
        db.session.add(u)

    db.session.commit()
