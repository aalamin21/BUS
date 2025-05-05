from app.views import slot_to_time

def test_slot_to_time_valid_index():
    index = 5
    result = slot_to_time(index)
    print(f"slot_to_time({index}) returned: '{result}'")
    assert result in ["Monday 2:00 PM", "Monday 02:00 PM"]

def test_slot_to_time_out_of_bounds():
    assert slot_to_time(999) == "Unknown Time"
