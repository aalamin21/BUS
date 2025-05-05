def test_register_new_user(client):
    response = client.post("/register", data={
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "faculty": "Medicine",
        "course_name": "MBBS",
        "year_of_study": 1,
        "password": "testpass",
        "confirm": "testpass"
    }, follow_redirects=True)

    assert b"Account created successfully" in response.data

def test_login_with_invalid_credentials(client):
    response = client.post("/login", data={
        "email": "fake@example.com",
        "password": "wrong"
    }, follow_redirects=True)

    assert b"Invalid username or password" in response.data
