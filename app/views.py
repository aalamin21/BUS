from flask import render_template, redirect, url_for, flash, request
from . import app, db
from .models import User, Group, Booking
from .forms import LoginForm, AvailabilityForm, RegistrationForm, ModuleForm, ChooseForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from .availability_utils import days, time_slots, flatten_availability, av_vec_to_dict, default_av
from .module_utils import module_list
from urllib.parse import urlsplit
from .utils import suggest_groups_for_user, rooms

def slot_to_time(slot_index):
    """Convert a slot index to human-readable time"""
    total_slots_per_day = len(time_slots)
    day_idx = slot_index // total_slots_per_day
    time_idx = slot_index % total_slots_per_day

    try:
        day = days[day_idx][1]  # Get full day name
        time = time_slots[time_idx][1]
        return f"{day} {time}"
    except IndexError:
        return "Unknown Time"


# Creates the Jinja filter
@app.template_filter('slot_to_time')
def slot_to_time_filter(slot_index):
    return slot_to_time(slot_index)

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
    return render_template('account.html', title="Account",
                           days=days, time_slots=time_slots, module_list=module_list)


"""Standard LOGIN page, with email and password fields - for login, use database values in debug_utils.py."""
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
       return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
           flash('Invalid username or password', 'danger')
           return redirect(url_for('login'))
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

"""Page 1/3 of 3 page registration, asks for user information that is stored in user database (See models). 
Includes validation for email addresses if duplicate"""
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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

"""Page 2/3 of 3 page registration, asks for user availability that is stored in user database (See models). """
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

        current_user.availability = flatten_availability(availability)
        if current_user.group:
            current_user.group.update_availability()
        db.session.commit()

        flash('Availability saved successfully', 'success')
        return redirect(url_for('modules'))

    user_availability = current_user.availability
    user_availability = av_vec_to_dict(user_availability)
    if user_availability:
        for day_code in user_availability:
            for time_code in user_availability[day_code]:
                field_name = f'{day_code}_{time_code}'
                form.data[field_name] = user_availability[day_code][time_code]

    return render_template('availability.html',
                           title='Availability', form=form)


"""Page 3/3 of 3 page registration, asks for modules that user wants to work on, can choose up to 3 but at 
least one. """
@app.route('/modules', methods=['GET', 'POST'])
@login_required
def modules():
    form = ModuleForm()
    if form.validate_on_submit():
        current_user.module1 = form.module1.data
        current_user.module2 = form.module2.data
        current_user.module3 = form.module3.data

        db.session.commit()

        flash('Module Choices saved successfully', 'success')
        return redirect(url_for('account'))

    return render_template('modules.html',
                           title='Modules', form=form)



@app.route("/suggested_groups")
@login_required
def suggested_groups():
    """Entry point for group suggestions
        - Checks existing group membership
        - Gets algorithm suggestions
        - Renders template with formatted data"""
    if current_user.group_id:
        flash("You’ve already joined a group.", "danger")
        return redirect(url_for("my_group"))

    existing_groups, new_group = suggest_groups_for_user(current_user)

    return render_template("group_suggestions.html",
                         title="Suggested Study Groups",
                            existing_groups=existing_groups,
                           new_group=new_group)

@app.route('/join_group', methods=['POST'])
@login_required
def join_group():
    group_id = request.form.get("group_id")

    if group_id:
        # Join existing group
        group = Group.query.get(int(group_id))
        if group:
            group.add_user(current_user)
            db.session.commit()
            flash("You have successfully joined the group.", "success")
        return redirect(url_for('my_group'))

    else:
        # Create a new group from suggestion
        new_group = Group()
        db.session.add(new_group)
        new_group.add_user(current_user)
        db.session.commit()

        flash("You've created and joined a new study group!", "success")
        return redirect(url_for('my_group'))

@app.route("/leave_group", methods=["POST"])
@login_required
def leave_group():
    current_user.group.remove_user(current_user)
    db.session.commit()
    flash("You have left the group.", "success")
    return redirect(url_for('suggested_groups'))


@app.route("/my_group")
@login_required
def my_group():
    form = ChooseForm()
    if not current_user.group_id:
        flash("You are not part of any study group yet.", "danger")
        return redirect(url_for("suggested_groups"))

    group = current_user.group
    common_modules = list(set.intersection(*({m.module1, m.module2, m.module3} for m in group.users)))
    shared_slots = group.group_av

    return render_template("my_group.html", title='My Group', group=group, form=form,
                           common_modules=common_modules, shared_slots=shared_slots, module_list=module_list)


@app.route("/suggest_meeting_time", methods=["GET","POST"])
@login_required
def suggest_meeting_time():
    form = ChooseForm()
    if not current_user.group_id:
        flash("You need to be in a group to suggest a meeting time", "danger")
        return redirect(url_for('suggested_groups'))
    # if current_user.group.bookings:
    #     flash("A booking has already been made for your group.", "danger")
    #     return redirect(url_for("my_group"))

    return render_template("suggest_meeting_time.html", title="Suggest Meeting Time", rooms=rooms
                           , form=form)

@app.route('/add_booking', methods=['POST'])
@login_required
def add_booking():
    form = ChooseForm()
    if form.validate_on_submit():
        group = current_user.group
        time_slot, room_idx = form.choice.data.split(",")
        room = rooms[int(room_idx)]
        new_booking = Booking(time_slot=int(time_slot), room=room)
        group.bookings.append(new_booking)
        db.session.add(new_booking)

        for user in group.users:
            user.change_time(int(time_slot))

        group.update_availability()
        db.session.commit()
        flash("You have successfully made a booking!", "success")

    return redirect(url_for('my_group'))

@app.route('/remove_booking', methods=['POST'])
def remove_booking():
    form = ChooseForm()
    if not current_user.group_id:
        flash("You need to be in a group to remove a booking", "danger")
        return redirect(url_for('suggested_groups'))
    if not current_user.group.bookings:
        flash("Your study group has no existing bookings", "danger")
        return redirect(url_for('my_group'))
    if form.validate_on_submit():
        booking = Booking.query.get(int(form.choice.data))
        if not booking:
            flash("This booking does not exist", "danger")
            return redirect(url_for('my_group'))
        for user in booking.group.users:
            user.change_time(booking.time_slot)
        booking.group.update_availability()
        db.session.delete(booking)
        db.session.commit()
        flash("You have successfully removed a booking!", "success")

    return redirect(url_for('my_group'))

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