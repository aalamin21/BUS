from flask import render_template, redirect, url_for, flash, request, send_file, send_from_directory
from app import app
from app.models import User, Group
from app.forms import ChooseForm, LoginForm, AvailabilityForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required, fresh_login_required
import sqlalchemy as sa
from app import db
from app.static.dt_lists import days, time_slots
from urllib.parse import urlsplit



@app.route("/")
def start():
    return render_template('startpage.html', title="Start")

@app.route("/home")
@login_required
def home():
    return render_template('home.html', title="Home")

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title="Account", days=days, time_slots=time_slots)


@app.route('/login', methods=['GET', 'POST'])
def login():
    #if current_user.is_authenticated:
       # return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        #if user is None or not user.check_password(form.password.data):
         #   flash('Invalid username or password', 'danger')
          #  return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('generic_form.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('start'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    #if current_user.is_authenticated:
     #   return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                        email =form.email.data, faculty =form.faculty.data,
                        course_name=form.course_name.data, year_of_study=form.year_of_study.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        try:
            db.session.commit()
        except sa.exc.IntegrityError:
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        login_user(new_user)
        flash('Account created successfully', 'success')
        return redirect(url_for('availability'))
    return render_template('register.html', title='Register', form=form)

@app.route('/availability', methods=['GET', 'POST'])
@login_required
def availability():
    form = AvailabilityForm()
    if form.validate_on_submit():
        availability = {}
        for day_code, day_name in days:
            availability[day_code] = {}
            for time_code, time_name in time_slots:
                field_name = f'{day_code}_{time_code}'
                availability[day_code][time_code] = form.data[field_name]

        current_user.availability = availability

        db.session.commit()

        flash('Availability saved successfully', 'success')
        return redirect(url_for('account'))

    user_availability = current_user.availability
    if user_availability:
        for day_code in user_availability:
            for time_code in user_availability[day_code]:
                field_name = f'{day_code}_{time_code}'
                form.data[field_name] = user_availability[day_code][time_code]

    return render_template('availability.html',
                           title='Availability', form=form)

@app.route('/groups_page')
@login_required
def groups_page():
    groups = db.session.scalars(db.select(Group))
    # print(groups[0].id)
    # for group in groups:
    #     print(group.id)
    # print('~~~~~~~~HERE~~~~~~~~')

    return render_template('groups.html', title='Groups', groups=groups)

@app.route('/group_page/<int:id>')
@login_required
def group_page_id(id):
    group = db.session.scalar(sa.select(Group).where(Group.id == id))


    if group is None:
        flash('Group not found', 'danger')
        return redirect(url_for('groups_page'))

    return render_template('group_page.html', title=f'Group {id}', group=group)

@app.route('/new_group')
@login_required
def new_group():
    group = Group()
    db.session.add(group)
    db.session.commit()
    return redirect(url_for('groups_page'))


# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403

# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404

@app.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413

# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500