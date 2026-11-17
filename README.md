# Corporate Event Management API

A RESTful backend API for Acme Corp's internal event management system,
built with **FastAPI**, **PostgreSQL (Neon)**, **SQLAlchemy 2.0**,
**Pydantic v2**, and **JWT authentication**.

The API allows employees to create and manage corporate events, browse
available events, register for events, view event registrations, and
cancel their own registrations.

## Features

### Mandatory assignment features

-   Create, retrieve, update, and delete events (CRUD).
-   Register employees for events.
-   View registrations for a specific event.
-   Cancel an employee's own registration.
-   Validate incoming request data with Pydantic.
-   Prevent duplicate registrations for the same employee and event.
-   Enforce event attendee capacity.
-   Return appropriate HTTP error responses.
-   Generate interactive API documentation through Swagger UI.

### Additional features implemented

-   JWT-based employee authentication.
-   Public event listing and event details.
-   Protected event creation, updating, and deletion.
-   Event creator ownership checks for updating and deleting.
-   Registration ownership checks for cancellation.
-   Pagination using `skip` and `limit`.
-   Filtering events by title and date.
-   Asynchronous database access using SQLAlchemy 2.0.
-   Automated API tests using pytest and an isolated in-memory SQLite
    database.

## Technology stack

  Technology          Purpose
  ------------------- ------------------------------------------
  Python              Backend programming language
  FastAPI             REST API framework
  PostgreSQL / Neon   Hosted application database
  SQLAlchemy 2.0      ORM and asynchronous database operations
  asyncpg             Async PostgreSQL driver
  Pydantic v2         Request validation and response schemas
  python-jose         JWT token creation and validation
  pwdlib              Password hashing and verification
  pytest              Automated testing
  HTTPX               Async HTTP client for API tests
  aiosqlite           Temporary SQLite database for tests
  Uvicorn             ASGI application server

## Project structure

``` text
Corporate-Event-Management/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_api.py
├── .venv/                 # Local virtual environment; not committed
├── .env                   # Local secrets; not committed
├── .gitignore
├── requirements.txt
├── pytest.ini
├── db.py                  # Async database engine, sessions and table creation
├── env.py                 # Environment configuration
├── models.py              # SQLAlchemy database models
├── schemas.py             # Pydantic request and response schemas
├── services.py            # Business logic and database operations
├── auth.py                # Password hashing and JWT authentication
├── main.py                # FastAPI application and API routes
├── README.md
└── CLAUDE.md              # Project context for AI coding assistants
```

## Database design

The application uses three main PostgreSQL tables:

### `users`

Stores employee accounts.

-   `id`: primary key
-   `name`: employee name
-   `email`: unique email address
-   `hashed_password`: password hash; plaintext passwords are not stored
-   `is_active`: account status
-   `created_at`: account creation timestamp

### `events`

Stores corporate event details.

-   `id`: primary key
-   `title`: event title
-   `description`: event description
-   `event_date`: event date and time
-   `location`: event location
-   `max_capacity`: maximum number of attendees
-   `created_by`: employee who created the event
-   `created_at`: event creation timestamp

### `registrations`

Connects employees to events.

-   `id`: primary key
-   `user_id`: employee foreign key
-   `event_id`: event foreign key
-   `registered_at`: registration timestamp

A database unique constraint on `(user_id, event_id)` prevents duplicate
registrations. Event capacity must be greater than zero.

## Requirements

-   Python 3.10 or newer (developed with Python 3.12).
-   A Neon PostgreSQL project and database.
-   Git.
-   PowerShell on Windows, or an equivalent terminal on another
    operating system.

## Installation and setup

### 1. Clone the repository

``` bash
git clone <YOUR_PUBLIC_GITHUB_REPOSITORY_URL>
cd Corporate-Event-Management
```

Replace the placeholder with the URL of your own public GitHub
repository.

### 2. Create and activate a virtual environment

Windows PowerShell:

``` powershell
python -m venv .venv
```

If PowerShell blocks script activation, allow scripts for the current
terminal session only:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Activate:

``` powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

``` powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Environment configuration

Create a `.env` file in the project root. Do not commit this file.

Add the following variables, replacing the placeholders with your own
values:

``` dotenv
DATABASE_URL=postgresql://YOUR_NEON_USER:YOUR_NEON_PASSWORD@YOUR_NEON_HOST/YOUR_DATABASE?sslmode=require
SECRET_KEY=YOUR_LONG_RANDOM_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Use the connection string supplied by Neon. Keep the real database URL
and JWT secret private.

**Security:** Never place credentials directly in Python source code,
README examples, screenshots, Git commits, or public issue reports. If a
credential is exposed, rotate it in Neon and update the local `.env`
file.

## Run the application

From the project root, with the virtual environment activated:

``` powershell
uvicorn main:app --reload
```

The FastAPI application initializes the database tables during startup
using the configured SQLAlchemy metadata.

Open Swagger UI:

<http://127.0.0.1:8000/docs>

Alternative OpenAPI schema:

<http://127.0.0.1:8000/openapi.json>

## API endpoints

### Home and health

  Method   Endpoint    Access   Description
  -------- ----------- -------- -----------------------------
  GET      `/`         Public   API welcome information
  GET      `/health`   Public   Application health response

### Authentication

  ------------------------------------------------------------------------
  Method            Endpoint           Access            Description
  ----------------- ------------------ ----------------- -----------------
  POST              `/auth/register`   Public            Register an
                                                         employee account

  POST              `/auth/login`      Public            Authenticate and
                                                         receive a JWT
                                                         access token

  GET               `/auth/me`         JWT required      Get the
                                                         authenticated
                                                         employee
  ------------------------------------------------------------------------

### Events

  ----------------------------------------------------------------------------
  Method            Endpoint               Access            Description
  ----------------- ---------------------- ----------------- -----------------
  POST              `/events`              JWT required      Create an event

  GET               `/events`              Public            List events with
                                                             pagination and
                                                             filters

  GET               `/events/{event_id}`   Public            Retrieve one
                                                             event

  PUT               `/events/{event_id}`   JWT required;     Update an event
                                           creator only      

  DELETE            `/events/{event_id}`   JWT required;     Delete an event
                                           creator only      
  ----------------------------------------------------------------------------

List events with pagination:

``` http
GET /events?skip=0&limit=10
```

Filter by title:

``` http
GET /events?title=Python
```

Filter by date (the implemented query parameter is `event_date`):

``` http
GET /events?event_date=2026-11-20
```

### Registrations

  ------------------------------------------------------------------------------------------
  Method            Endpoint                             Access            Description
  ----------------- ------------------------------------ ----------------- -----------------
  POST              `/events/{event_id}/registrations`   JWT required      Register the
                                                                           authenticated
                                                                           employee

  GET               `/events/{event_id}/registrations`   JWT required      View
                                                                           registrations for
                                                                           an event

  DELETE            `/registrations/{registration_id}`   JWT required;     Cancel the
                                                         owner only        employee's own
                                                                           registration
  ------------------------------------------------------------------------------------------

## Authentication workflow

1.  Send employee details to `POST /auth/register`.
2.  Log in through `POST /auth/login`.
3.  Copy the `access_token` from the response.
4.  In Swagger UI, click **Authorize** and paste the token value. For
    HTTP Bearer authentication, paste the token itself; Swagger supplies
    the Bearer scheme.
5.  Use the protected endpoints.

Example login request:

``` json
{
  "email": "employee@example.com",
  "password": "YOUR_PASSWORD"
}
```

Example successful token response:

``` json
{
  "access_token": "<JWT_ACCESS_TOKEN>",
  "token_type": "bearer"
}
```

The default token lifetime is configured through
`ACCESS_TOKEN_EXPIRE_MINUTES`.

## Business rules and validation

-   Event titles cannot be empty.
-   Event dates must be valid datetime values.
-   Maximum event capacity must be greater than zero.
-   An employee cannot register for the same event more than once.
-   An event cannot accept more registrations than its capacity.
-   Employees cannot cancel another employee's registration.
-   In the current route implementation, only an event's creator can
    update or delete that event.
-   Passwords are stored as hashes, not plaintext.

## HTTP status codes

  -----------------------------------------------------------------------
  Status                              Meaning in this API
  ----------------------------------- -----------------------------------
  `200 OK`                            Successful retrieval or update

  `201 Created`                       Resource created

  `204 No Content`                    Successful deletion

  `401 Unauthorized`                  Authentication is missing or
                                      invalid

  `403 Forbidden`                     Authenticated user is not permitted
                                      to perform the action

  `404 Not Found`                     Requested event, user, or
                                      registration does not exist

  `409 Conflict`                      Duplicate registration or event
                                      capacity reached

  `422 Unprocessable Entity`          Request data failed validation
  -----------------------------------------------------------------------

## Automated tests

The automated tests use pytest and an isolated in-memory SQLite
database. They do not need to write test records to the production Neon
database.

Install dependencies:

``` powershell
pip install -r requirements.txt
```

Run all tests from the project root:

``` powershell
python -m pytest
```

The test suite currently contains 16 tests covering:

-   Employee registration and duplicate email handling.
-   Successful and unsuccessful login.
-   Retrieving the authenticated employee.
-   Event creation, listing, retrieval, updating, and deletion.
-   Event registration and duplicate registration prevention.
-   Event capacity restriction.
-   Registration cancellation.
-   Invalid event data.
-   Unauthorized event creation.

**Verified development result:** The project owner reported `16 passed`
in the local test environment. Run the command again after any code
changes and update this result if the outcome changes.

## Git and GitHub workflow

The assignment requires a public GitHub repository, `main` as the stable
branch, feature branches for individual features, regular meaningful
commits, and merging completed features into `main`.

Useful commands:

``` powershell
git status
git branch
git switch -c feature/pytest-tests
git add tests pytest.ini requirements.txt
git commit -m "Add automated API tests"
git push -u origin feature/pytest-tests
```

Use the actual branch name appropriate to your current work. Review
`git status` before staging files.

Never commit `.env`, `.venv/`, database credentials, JWT secrets, Python
cache files, or pytest cache files. Confirm `.gitignore` excludes them.

Do not merge into `main` until the feature branch has been reviewed and
tested.

## Assignment submission checklist

-   [ ] Public GitHub repository link.
-   [ ] Complete source code and required project structure.
-   [ ] `requirements.txt` with project dependencies.
-   [ ] `README.md` with installation, database configuration, and
    execution instructions.
-   [ ] Swagger UI screenshots showing successful API testing.
-   [ ] AI usage documentation, if AI tools were used. The assignment
    requests prompts, relevant chat history, tools/models, and
    configurations.
-   [ ] Mandatory project demo video.

### Mandatory demo video outline

The assignment asks the demo video to include:

1.  A brief introduction to the project and its purpose.
2.  Explanation of the project structure and how files work together.
3.  Demonstration of the database and FastAPI integration.
4.  Walkthrough of important functions and business logic.
5.  The application running successfully.
6.  Testing of implemented API endpoints with requests and responses.
7.  Explanation of key concepts and implementation decisions.
8.  Frontend demonstration only if a frontend has been implemented.

The project owner should be able to explain the submitted code and
implementation decisions.

## Notes

-   This is a backend-focused assignment. A frontend is optional and is
    not required for marks.
-   Keep this README synchronized with the actual code and current test
    results.
-   The assignment deadline stated in the brief is Wednesday, 18
    November 2026, end of day.
