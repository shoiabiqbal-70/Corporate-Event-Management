
"""
Automated API tests for Corporate Event Management API.

Tests authentication, event CRUD, registrations,
capacity restrictions, and validation.
"""

import pytest


# =========================================================
# HELPER FUNCTIONS
# =========================================================

async def create_employee(
    client,
    name="Test Employee",
    email="employee@example.com",
    password="Employee123",
):
    """Register an employee and return their details."""

    response = await client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    return response.json()


async def login_employee(
    client,
    email="employee@example.com",
    password="Employee123",
):
    """Log in an employee and return the JWT token."""

    response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


async def create_test_event(
    client,
    token,
    capacity=10,
):
    """Create an event for testing."""

    response = await client.post(
        "/events",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Python Testing Workshop",
            "description": "Automated testing event",
            "event_date": "2026-12-15T10:00:00Z",
            "location": "Conference Hall",
            "max_capacity": capacity,
        },
    )

    assert response.status_code == 201

    return response.json()


# =========================================================
# TEST 1: EMPLOYEE REGISTRATION
# =========================================================

@pytest.mark.asyncio
async def test_employee_registration(client):
    """Test successful employee registration."""

    response = await client.post(
        "/auth/register",
        json={
            "name": "Ali Khan",
            "email": "ali@example.com",
            "password": "Password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Ali Khan"
    assert data["email"] == "ali@example.com"

    # Password must never appear in the response.
    assert "password" not in data
    assert "hashed_password" not in data


# =========================================================
# TEST 2: DUPLICATE EMPLOYEE REGISTRATION
# =========================================================

@pytest.mark.asyncio
async def test_duplicate_employee_registration(client):
    """Test that duplicate employee emails are rejected."""

    await create_employee(client)

    response = await client.post(
        "/auth/register",
        json={
            "name": "Another Employee",
            "email": "employee@example.com",
            "password": "Password123",
        },
    )

    assert response.status_code == 409


# =========================================================
# TEST 3: EMPLOYEE LOGIN
# =========================================================

@pytest.mark.asyncio
async def test_employee_login(client):
    """Test successful employee login."""

    await create_employee(client)

    response = await client.post(
        "/auth/login",
        json={
            "email": "employee@example.com",
            "password": "Employee123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


# =========================================================
# TEST 4: INVALID LOGIN
# =========================================================

@pytest.mark.asyncio
async def test_invalid_login(client):
    """Test rejection of incorrect login credentials."""

    await create_employee(client)

    response = await client.post(
        "/auth/login",
        json={
            "email": "employee@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401


# =========================================================
# TEST 5: CURRENT USER
# =========================================================

@pytest.mark.asyncio
async def test_current_user(client):
    """Test retrieving the authenticated employee."""

    await create_employee(client)

    token = await login_employee(client)

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "employee@example.com"


# =========================================================
# TEST 6: EVENT CREATION
# =========================================================

@pytest.mark.asyncio
async def test_event_creation(client):
    """Test creating a new corporate event."""

    await create_employee(client)

    token = await login_employee(client)

    event = await create_test_event(client, token)

    assert event["title"] == "Python Testing Workshop"
    assert event["max_capacity"] == 10


# =========================================================
# TEST 7: GET ALL EVENTS
# =========================================================

@pytest.mark.asyncio
async def test_get_all_events(client):
    """Test retrieving all available events."""

    await create_employee(client)

    token = await login_employee(client)

    await create_test_event(client, token)

    response = await client.get("/events")

    assert response.status_code == 200
    assert len(response.json()) == 1


# =========================================================
# TEST 8: GET SINGLE EVENT
# =========================================================

@pytest.mark.asyncio
async def test_get_single_event(client):
    """Test retrieving one event by its ID."""

    await create_employee(client)

    token = await login_employee(client)

    event = await create_test_event(client, token)

    response = await client.get(
        f"/events/{event['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == event["id"]


# =========================================================
# TEST 9: UPDATE EVENT
# =========================================================

@pytest.mark.asyncio
async def test_update_event(client):
    """Test updating an existing event."""

    await create_employee(client)

    token = await login_employee(client)

    event = await create_test_event(client, token)

    response = await client.put(
        f"/events/{event['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Python Workshop",
            "description": "Updated training",
            "event_date": "2026-12-20T10:00:00Z",
            "location": "Room B",
            "max_capacity": 20,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Python Workshop"


# =========================================================
# TEST 10: DELETE EVENT
# =========================================================

@pytest.mark.asyncio
async def test_delete_event(client):
    """Test deleting an existing event."""

    await create_employee(client)

    token = await login_employee(client)

    event = await create_test_event(client, token)

    response = await client.delete(
        f"/events/{event['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    # Verify that deleted event no longer exists.
    check_response = await client.get(
        f"/events/{event['id']}"
    )

    assert check_response.status_code == 404


# =========================================================
# TEST 11: EMPLOYEE EVENT REGISTRATION
# =========================================================

@pytest.mark.asyncio
async def test_event_registration(client):
    """Test successful event registration."""

    await create_employee(client)

    token = await login_employee(client)

    event = await create_test_event(client, token)

    response = await client.post(
        f"/events/{event['id']}/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json()["event_id"] == event["id"]


# =========================================================
# TEST 12: DUPLICATE EVENT REGISTRATION
# =========================================================

@pytest.mark.asyncio
async def test_duplicate_event_registration(client):
    """Test prevention of duplicate registrations."""

    await create_employee(client)

    token = await login_employee(client)

    event = await create_test_event(client, token)

    endpoint = f"/events/{event['id']}/registrations"

    headers = {"Authorization": f"Bearer {token}"}

    first_response = await client.post(
        endpoint,
        headers=headers,
    )

    second_response = await client.post(
        endpoint,
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


# =========================================================
# TEST 13: EVENT CAPACITY RESTRICTION
# =========================================================

@pytest.mark.asyncio
async def test_event_capacity_limit(client):
    """Test that an event cannot exceed its capacity."""

    # Create first employee.
    await create_employee(
        client,
        name="Employee One",
        email="one@example.com",
    )

    token_one = await login_employee(
        client,
        email="one@example.com",
    )

    # First employee creates an event with capacity 1.
    event = await create_test_event(
        client,
        token_one,
        capacity=1,
    )

    endpoint = f"/events/{event['id']}/registrations"

    # First employee takes the only available seat.
    first_response = await client.post(
        endpoint,
        headers={"Authorization": f"Bearer {token_one}"},
    )

    assert first_response.status_code == 201

    # Create second employee.
    await create_employee(
        client,
        name="Employee Two",
        email="two@example.com",
    )

    token_two = await login_employee(
        client,
        email="two@example.com",
    )

    # Second employee tries to register.
    second_response = await client.post(
        endpoint,
        headers={"Authorization": f"Bearer {token_two}"},
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "Event capacity has been reached."
    )


# =========================================================
# TEST 14: CANCEL REGISTRATION
# =========================================================

@pytest.mark.asyncio
async def test_cancel_registration(client):
    """Test successful registration cancellation."""

    await create_employee(client)

    token = await login_employee(client)

    event = await create_test_event(client, token)

    registration_response = await client.post(
        f"/events/{event['id']}/registrations",
        headers={"Authorization": f"Bearer {token}"},
    )

    registration_id = registration_response.json()["id"]

    response = await client.delete(
        f"/registrations/{registration_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


# =========================================================
# TEST 15: INVALID EVENT DATA
# =========================================================

@pytest.mark.asyncio
async def test_invalid_event_data(client):
    """Test validation of invalid event information."""

    await create_employee(client)

    token = await login_employee(client)

    response = await client.post(
        "/events",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Invalid Event",
            "description": "Invalid capacity",
            "event_date": "2026-12-15T10:00:00Z",
            "location": "Conference Hall",
            "max_capacity": 0,
        },
    )

    assert response.status_code == 422


# =========================================================
# TEST 16: UNAUTHORIZED EVENT CREATION
# =========================================================

@pytest.mark.asyncio
async def test_unauthorized_event_creation(client):
    """Test that unauthenticated users cannot create events."""

    response = await client.post(
        "/events",
        json={
            "title": "Unauthorized Event",
            "description": "Testing authentication",
            "event_date": "2026-12-15T10:00:00Z",
            "location": "Conference Hall",
            "max_capacity": 20,
        },
    )

    assert response.status_code == 401
