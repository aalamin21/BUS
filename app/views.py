from flask import render_template, redirect, url_for, flash, request, send_file, send_from_directory, session
from app import app
from app.models import User, Group
from app.forms import ChooseForm, LoginForm, AvailabilityForm, RegistrationForm, ModuleForm
from flask_login import current_user, login_user, logout_user, login_required, fresh_login_required
import sqlalchemy as sa
from app import db
from .availability_utils import days, time_slots, flatten_availability, av_vec_to_dict, slot_to_human
from .module_utils import module_list
from urllib.parse import urlsplit
from .utils import suggest_groups_for_user

from app.utils import get_all_suggestions

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
        return redirect(url_for('account'))

    user_availability = current_user.availability
    user_availability = av_vec_to_dict(user_availability)
    if user_availability:
        for day_code in user_availability:
            for time_code in user_availability[day_code]:
                field_name = f'{day_code}_{time_code}'
                form.data[field_name] = user_availability[day_code][time_code]

    return render_template('availability.html',
                           title='Availability', form=form)

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
        #  Join existing group
        group = Group.query.get(int(group_id))
        if group:
            group.add_user(current_user)
            db.session.commit()
            flash("You have successfully joined the group.", "success")
        return redirect(url_for('my_group'))

    else:
        #  Create a new group from suggestion
        new_group = Group()
        db.session.add(new_group)
        db.session.commit()

        current_user.group_id = new_group.id
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
    if not current_user.group_id:
        flash("You are not part of any study group yet.", "danger")
        return redirect(url_for("suggested_groups"))

    group = Group.query.get(current_user.group_id)
    members = group.users
    common_modules = list(set.intersection(*(set([m.module1, m.module2, m.module3]) for m in members))) # Todo: create a common module list in group database
    shared_slots = list(set.intersection(*(set(m.availability) for m in members if m.availability))) # Todo: Use group availability from database

    return render_template("my_group.html", title='My Group', group=group, members=members,
                           common_modules=common_modules, shared_slots=shared_slots, module_list=module_list)


@app.route("/suggest_meeting_time", methods=["GET"])
@login_required
def suggest_meeting_time():
    if not current_user.group_id:
        flash("You need to be in a group to suggest a meeting time", "danger")
        return redirect(url_for('suggested_groups'))

    # Retrieve the current group and its members
    group = Group.query.get(current_user.group_id)
    members = group.users

    # Collect availability for each member
    member_availabilities = {member.id: member.availability for member in members if member.availability}

    # Now find overlapping times for all group members
    overlapping_times = get_overlapping_times(member_availabilities)

    # Convert overlapping slots into human-readable time
    overlapping_slots = [slot_to_human(slot) for slot in overlapping_times]

    return render_template("suggest_meeting_time.html", title="Suggest Meeting Time",
                           overlapping_slots=overlapping_slots)
def get_overlapping_times(member_availabilities):
    # Assume all members have a similar availability structure, so take the first member's availability
    all_member_times = list(member_availabilities.values())

    # Find common slots: all members must be available at the same time
    overlapping_times = []
    for i in range(len(time_slots) * len(days)):  # Total slots
        if all(all_member[i] == 1 for all_member in all_member_times):
            overlapping_times.append(i)

    return overlapping_times





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