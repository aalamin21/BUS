from app import db
from app.models import User

def reset_db():
    db.drop_all()
    db.create_all()

    users = [
        {'first_name': 'Amelia', 'last_name': 'Carter', 'email': 'amelia.carter01@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'A123'},

        {'first_name': 'Daniel', 'last_name': 'Mensah', 'email': 'daniel.mensah@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'D123'},

        {'first_name': 'Priya', 'last_name': 'Shah', 'email': 'priya.shah@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'P123'},

        {'first_name': 'James', 'last_name': "O’Connell", 'email': 'james.oconnell@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'J123'},

        {'first_name': 'Thandi', 'last_name': 'Mokoena', 'email': 'thandi.mokoena@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'T123'},

        {'first_name': 'Ethan', 'last_name': 'Blake', 'email': 'ethan.blake@estudent.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'E123'},

        {'first_name': 'Fatima', 'last_name': 'Noor', 'email': 'fatima.noor@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'F123'},

        {'first_name': 'Liam', 'last_name': 'Zhang', 'email': 'liam.zhang@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'L123'},

        {'first_name': 'Chloe', 'last_name': 'Ncube', 'email': 'chloe.ncube@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'C123'},

        {'first_name': 'Nathan', 'last_name': 'Dlamini', 'email': 'nathan.dlamini@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'N123'},

        {'first_name': 'Olivia', 'last_name': 'Kimani', 'email': 'olivia.kimani@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'O123'},

        {'first_name': 'Samuel', 'last_name': 'Boateng', 'email': 'samuel.boateng@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'S123'},

        {'first_name': 'Grace', 'last_name': 'Mbatha', 'email': 'grace.mbatha@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'G123'},

        {'first_name': 'Isaac', 'last_name': 'Owusu', 'email': 'isaac.owusu@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'I123'},

        {'first_name': 'Nyasha', 'last_name': 'Moyo', 'email': 'nyasha.moyo@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'N123'},

        {'first_name': 'Zoe', 'last_name': 'Daniels', 'email': 'zoe.daniels@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'Z123'},

        {'first_name': 'Brian', 'last_name': 'Tshabalala', 'email': 'brian.tshabalala@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'B123'},

        {'first_name': 'Aisha', 'last_name': 'Yusuf', 'email': 'aisha.yusuf@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'A123'},

        {'first_name': 'Joseph', 'last_name': 'Eze', 'email': 'joseph.eze@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'J123'},

        {'first_name': 'Rebecca', 'last_name': 'Adebayo', 'email': 'rebecca.adebayo@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'R123'},

        {'first_name': 'Michael', 'last_name': 'Njoroge', 'email': 'michael.njoroge@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'M123'},

        {'first_name': 'Linda', 'last_name': 'Khupe', 'email': 'linda.khupe@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'L123'},

        {'first_name': 'David', 'last_name': 'Smith', 'email': 'david.smith@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'D123'},

        {'first_name': 'Thabo', 'last_name': 'Maluleke', 'email': 'thabo.maluleke@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'T123'},

        {'first_name': 'Yasmin', 'last_name': 'Khan', 'email': 'yasmin.khan@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'Y123'},

        {'first_name': 'Peter', 'last_name': 'Banda', 'email': 'peter.banda@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'P123'},

        {'first_name': 'Keisha', 'last_name': 'Brown', 'email': 'keisha.brown@estudent.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'K123'},

        {'first_name': 'Raymond', 'last_name': 'Okeke', 'email': 'raymond.okeke@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'R123'},

        {'first_name': 'Tamara', 'last_name': 'Sibanda', 'email': 'tamara.sibanda@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'T123'},

        {'first_name': 'Henry', 'last_name': 'Mthembu', 'email': 'henry.mthembu@student.bham.ac.uk',
         'faculty': "Life Sciences", 'course_name': 'Medicine and Surgery MBChB', 'year_of_study': 'First Year',
         'password': 'H123'}
    ]




    for u in users:
        password = u.pop('password')
        u = User(**u)
        u.set_password(password)
        db.session.add(u)

    db.session.commit()
