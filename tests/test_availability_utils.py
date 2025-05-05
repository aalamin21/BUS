import pytest
from app.availability_utils import *

@pytest.fixture
def empty_availability():
    return {
        day[0]: {slot[0]: False for slot in time_slots}
        for day in days
    }

def test_flatten_and_unflatten_round_trip(empty_availability):
    empty_availability['monday']['0900'] = True
    empty_availability['tuesday']['1000'] = True

    flat = flatten_availability(empty_availability)
    restored = av_vec_to_dict(flat)

    assert restored['monday']['0900'] is True
    assert restored['tuesday']['1000'] is True
    assert restored['wednesday']['1100'] is False

def test_default_av_all_true_and_false():
    true_vector = default_av(True)
    false_vector = default_av(False)

    assert all(true_vector)
    assert not any(false_vector)

def test_group_availability_multiple_users():
    av1 = [1, 1, 0, 1]
    av2 = [1, 0, 0, 1]
    expected = [1, 0, 0, 1]
    result = group_availability(av1, av2)
    assert result == expected

def test_av_vec_to_dict_invalid():
    with pytest.raises(ValueError):
        av_vec_to_dict([1, 0, 1])  # wrong length

def test_slot_overlap_logic():
    assert slot_overlap([1, 1, 0, 0], [1, 1, 1, 1]) is True
    assert slot_overlap([1, 0, 0, 0], [0, 1, 0, 0]) is False

def test_slot_to_human_readability():
    index = 0  # First slot: Monday 09:00 AM
    result = slot_to_human(index)
    assert result.startswith("Monday") and "09:00" in result
