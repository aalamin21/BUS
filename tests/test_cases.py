import pytest
import numpy as np
from app.utils import jaccard_similarity, compute_match_score, suggest_groups_for_user
from app.models import User, Group
from app import app, db
import time
from sqlalchemy.orm import Session
import asyncio
from app.forms import RegistrationForm
from flask import current_app


@pytest.fixture(scope='function')
def test_client():
    with app.app_context():
        yield app.test_client()


@pytest.fixture(scope='function')
def init_database():
    #initialises the database for the test client
    with app.app_context():
        db.create_all()
        try:
            yield db
        finally:
            db.session.remove()
            db.drop_all()

# New fixture to provide a request context with CSRF disabled
@pytest.fixture
def form_test_context(test_client):
    """Provides a request context with CSRF disabled for form validation testing."""
    # test_client fixture ensures the app context is pushed.
    # Now, push a request context and disable CSRF temporarily.
    with current_app.test_request_context():
        original_csrf_status = current_app.config.get('WTF_CSRF_ENABLED', True)
        current_app.config['WTF_CSRF_ENABLED'] = False
        yield # Provide the context to the test
        # Restore original CSRF status after the test
        current_app.config['WTF_CSRF_ENABLED'] = original_csrf_status


@pytest.fixture
def sample_users(init_database):
    #Fixture to create the sample users for testing.
    with app.app_context():
        timestamp = str(time.time())
        users = [
            User(first_name="A", last_name="1", email=f"a{timestamp}@example.com", availability=[1] * 70,
                 module1=0, module2=1, module3=2, faculty="Life Sciences", course_name="Medicine", year_of_study="First Year"),
            User(first_name="B", last_name="2", email=f"b{timestamp}@example.com", availability=[1] * 70,
                 module1=0, module2=3, module3=1, faculty="Life Sciences", course_name="Medicine", year_of_study="First Year"),
            User(first_name="C", last_name="3", email=f"c{timestamp}@example.com", availability=[1, 1, 0] + [0] * 67,
                 module1=2, module2=4, module3=-1, faculty="Life Sciences", course_name="Medicine", year_of_study="First Year"),
            User(first_name="D", last_name="4", email=f"d{timestamp}@example.com", availability=[0] * 70,
                 module1=0, module2=1, module3=2, faculty="Life Sciences", course_name="Medicine", year_of_study="First Year")
        ]
        db.session.add_all(users)
        db.session.commit()
        return db.session.query(User).order_by(User.id).all()


@pytest.fixture
def sample_groups(init_database, sample_users):
   # Fixture to create sample groups for testing.
    with app.app_context():
        group1 = Group()
        group2 = Group()
        db.session.add_all([group1, group2])
        db.session.flush()  # Ensures group IDs are populated

        group1.users = [sample_users[0], sample_users[1]]
        group2.users = [sample_users[2]]
        db.session.commit()

        group1.update_availability()
        group2.update_availability()
        db.session.commit()

        return db.session.query(Group).order_by(Group.id).all()



# ------------------ Test Cases ------------------ #

# Feature 1: Jaccard Similarity Calculation
def test_jaccard_similarity_positive():
    #Test case where the two sets have 50% similarity.
    set1 = {1, 2, 3}
    set2 = {2, 3, 4}
    assert abs(jaccard_similarity(set1, set2) - 0.5) < 1e-6


def test_jaccard_similarity_negative():
    #Test case where the two sets have 0 common elements.
    set1 = {1, 2, 3}
    set2 = {4, 5, 6}
    assert abs(jaccard_similarity(set1, set2) - 0.0) < 1e-6


# Feature 2: Group Suggestion Algorithm
@pytest.mark.asyncio
async def test_suggest_groups_for_user_positive(test_client, sample_users, sample_groups):
    #This is a test case where a suitable existing group is suggested.
    with app.app_context():
        current_user = db.session.get(User, sample_users[3].id)  # Reattach to session
        suggested_groups, _ = suggest_groups_for_user(current_user, group_size=4, top_n=2, session=db.session)
        group_ids = [g['group'].id for g in suggested_groups]
        assert sample_groups[0].id in group_ids


def test_suggest_groups_for_user_negative(init_database):
    """This is a test case where no suitable existing groups exist."""
    with app.app_context():
        # Create a lonely user with no available groups
        timestamp = str(time.time())
        lonely_user = User(first_name="Lonely", last_name="User", email=f"lonely{timestamp}@example.com",
                           availability=[0] * 70, module1=0, module2=1, module3=2,
                           faculty="Life Sciences", course_name="Medicine", year_of_study="First Year")
        db.session.add(lonely_user)
        db.session.commit()

        # Now, suggest groups for this lonely user
        suggested_groups, _ = suggest_groups_for_user(lonely_user, group_size=4, top_n=2)

        # Assert that no groups are suggested, checking for empty list rather than None
        assert suggested_groups == []  # Expecting an empty list instead of None


# Feature 3: Match Score Calculation
def test_compute_match_score_positive():
    #Test case with non-zero similarity and overlap.
    mod_sim = 0.8
    avail_sim = 0.6
    overlap = 1
    expected_score = 0.5 * mod_sim + 0.3 * avail_sim + 0.2 * overlap
    assert abs(compute_match_score(mod_sim, avail_sim, overlap) - expected_score) < 1e-6


def test_compute_match_score_negative():
    #Test case with zero similarity and overlap.
    assert abs(compute_match_score(0.0, 0.0, 0.0) - 0.0) < 1e-6


# Easiest Positive Test Case for Registration Form (Using form_test_context)
def test_registration_form_positive(form_test_context):
    #Test registration form with minimal but valid data using form_test_context.
    form_data = {
        'first_name': 'Valid',
        'last_name': 'User',
        'email': 'valid.user@university.edu',   # Must be a valid email format
        'faculty': 'Life Sciences',   # Must be one of the choices
        'course_name': 'Medicine and Surgery MBChB',   # Must be one of the choices
        'year_of_study': 'First Year',   # Must be one of the choices
        'password': 'password123',   # Just needs to be non-empty for DataRequired
        'confirm_password': 'password123'   # Just needs to be non-empty for DataRequired
    }
    form = RegistrationForm(data=form_data)

    # Check if the form validates successfully
    assert form.validate(), f"Form should be valid with valid data, but got errors: {form.errors}"
    assert form.errors == {} # Ensure no validation errors were recorded


# Easiest Negative Test Case for Registration Form (Using form_test_context)
def test_registration_form_negative(form_test_context):
    """Test registration form with no data (missing all required fields) using form_test_context."""
    form_data = {} # An empty dictionary means no data was submitted for any field

    form = RegistrationForm(data=form_data)

    # Check if the form fails validation
    assert not form.validate(), "Form should be invalid with no data"

    # Check that there are errors.
    assert form.errors != {}
    # Check that specific required fields have errors
    assert 'first_name' in form.errors
    assert 'last_name' in form.errors
    assert 'email' in form.errors
    assert 'faculty' in form.errors
    assert 'course_name' in form.errors
    assert 'year_of_study' in form.errors
    assert 'password' in form.errors
    assert 'confirm_password' in form.errors
    #This should pass if the errors are picked up by the form
