import pytest
import numpy as np
from app.utils import jaccard_similarity, compute_match_score, suggest_groups_for_user
from app.models import User, Group
from app import app, db
import time

@pytest.fixture(scope='module')
def test_client():
    """Fixture to create a test client for the Flask app."""
    # Use 'with app.app_context():' to push an application context
    with app.app_context():
        # Yield the test client
        yield app.test_client()

@pytest.fixture(scope='module')
def init_database():
    """Fixture to initialize the database for testing."""
    # Use 'with app.app_context():' here as well
    with app.app_context():
        # Create all tables
        db.create_all()
        try:
            yield db
        except Exception as e:
            db.session.rollback()
            raise e
        finally:
            # Drop all tables
            db.drop_all()



@pytest.fixture
def sample_users(init_database):
    """Fixture to create sample users for testing."""
    with app.app_context():
        timestamp = str(time.time())
        user1 = User(first_name="A", last_name="1", email=f"a{timestamp}@example.com", availability=[1] * 70,
                     module1=0, module2=1, module3=2, faculty="Life Sciences",
                     course_name="Medicine", year_of_study="First Year")  # User A
        user2 = User(first_name="B", last_name="2", email=f"b{timestamp}@example.com", availability=[1] * 70,
                     module1=0, module2=3, module3=1, faculty="Life Sciences",
                     course_name="Medicine", year_of_study="First Year")  # User B
        user3 = User(first_name="C", last_name="3", email=f"c{timestamp}@example.com",
                     availability=[1, 1, 0] + [0] * 67, module1=2, module2=4, module3=-1,
                     faculty="Life Sciences", course_name="Medicine", year_of_study="First Year")  # User C
        user4 = User(first_name="D", last_name="4", email=f"d{timestamp}@example.com", availability=[0] * 70,
                     module1=0, module2=1, module3=2, faculty="Life Sciences",
                     course_name="Medicine", year_of_study="First Year")  # User D
        db.session.add_all([user1, user2, user3, user4])
        db.session.commit()
        return [user1, user2, user3, user4]



@pytest.fixture
def sample_groups(init_database, sample_users):
    """Fixture to create sample groups for testing."""
    with app.app_context():
        group1 = Group()
        db.session.add(group1)  # Add group1 to the session FIRST
        group1.users = [sample_users[0], sample_users[1]]  # Users A and B
        group1.update_availability()
        group2 = Group()
        db.session.add(group2)  # Add group2 to the session FIRST
        group2.users = [sample_users[2]]
        group2.update_availability()
        db.session.commit()
        return [group1, group2]



# Feature 1: Jaccard Similarity Calculation
def test_jaccard_similarity_positive():
    """Test case where the two sets have 50% similarity."""
    set1 = {1, 2, 3}
    set2 = {2, 3, 4}
    assert jaccard_similarity(set1, set2) == 0.5


def test_jaccard_similarity_negative():
    """Test case where the two sets have no common elements."""
    set1 = {1, 2, 3}
    set2 = {4, 5, 6}
    assert jaccard_similarity(set1, set2) == 0.0


# Feature 2: Group Suggestion Algorithm
def test_suggest_groups_for_user_positive(test_client, sample_users, sample_groups):
    """Test case where a suitable existing group is suggested."""
    with app.app_context():
        current_user = sample_users[3]  # User D
        suggested_groups, a = suggest_groups_for_user(current_user, group_size=4, top_n=2)
        assert any(group['group'].id == 1 for group in suggested_groups)
        assert suggested_groups[0]['group'].id == 1

def test_suggest_groups_for_user_negative(test_client, sample_users):
    """Test case where no suitable existing groups exist."""
    with app.app_context():
        current_user = sample_users[3]
        suggested_groups, _ = suggest_groups_for_user(current_user, group_size=4, top_n=2)
        assert len(suggested_groups) == 0


# Feature 3: Match Score Calculation
def test_compute_match_score_positive():
    """Test case with non-zero similarity and overlap."""
    mod_sim = 0.8
    avail_sim = 0.6
    overlap = 1
    expected_score = 0.5 * 0.8 + 0.3 * 0.6 + 0.2 * 1
    assert compute_match_score(mod_sim, avail_sim, overlap) == expected_score


def test_compute_match_score_negative():
    """Test case with zero similarity and overlap."""
    mod_sim = 0.0
    avail_sim = 0.0
    overlap = 0
    assert compute_match_score(mod_sim, avail_sim, overlap) == 0.0

