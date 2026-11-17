# CLAUDE.md --- Corporate Event Management API

This file provides project context and working instructions for Claude
(or another coding assistant) when working in this repository. Read it
before changing code.

## 1. Project overview

**Project:** Corporate Event Management API\
**Organization scenario:** Acme Corp internal event system\
**Purpose:** Build a REST API that lets employees create and manage
corporate events, view events, register for events, view registrations,
and cancel their own registrations.

The system supports events such as: - Product launches - Technical
workshops and training sessions - Team-building activities - Corporate
events and conferences

**Assignment:** Backend Development --- Assignment 01, Corporate Event
Management API.\
**Instructor:** Osama Izhar.\
**Deadline stated in assignment:** Wednesday, 18 November 2026, end of
day.

The project builds on a previous Bookstore API project. Keep the
architecture familiar and straightforward; do not introduce unnecessary
complexity.

## 2. Required technology

-   Python
-   FastAPI
-   PostgreSQL hosted on Neon
-   SQLAlchemy 2.0
-   Pydantic v2
-   JWT authentication (assignment bonus feature)
-   Asynchronous SQLAlchemy engine and sessions (assignment bonus
    feature)
-   pytest (assignment bonus feature)
-   Git and GitHub

Use async database operations (`async` / `await`) throughout the
application.

## 3. Assignment requirements

### Mandatory features

#### A. Event CRUD

  Method   Endpoint         Purpose
  -------- ---------------- ---------------------
  POST     `/events`        Create an event
  GET      `/events`        Retrieve all events
  GET      `/events/{id}`   Retrieve one event
  PUT      `/events/{id}`   Update an event
  DELETE   `/events/{id}`   Delete an event

Each event must contain: - Event ID - Event title - Description - Event
date - Event location - Maximum attendee capacity

#### B. Event registration

  ------------------------------------------------------------------------------
  Method                  Endpoint                       Purpose
  ----------------------- ------------------------------ -----------------------
  POST                    `/events/{id}/registrations`   Register an employee
                                                         for an event

  GET                     `/events/{id}/registrations`   View registrations for
                                                         an event

  DELETE                  `/registrations/{id}`          Cancel a registration
  ------------------------------------------------------------------------------

Business rules: 1. An employee cannot register for the same event twice.
2. An event cannot accept registrations beyond its maximum capacity. 3.
A registration cannot be made for a non-existent event.

#### C. Pydantic validation

-   Event title cannot be empty.
-   Event date must be valid.
-   Maximum capacity must be greater than zero.
-   Required fields must be provided.
-   Invalid registration data must be rejected.

#### D. Error handling

Use appropriate HTTP status codes: - `200 OK`: successful retrieval or
update - `201 Created`: resource created - `204 No Content`: successful
deletion - `401 Unauthorized`: authentication missing or invalid -
`404 Not Found`: event or registration does not exist - `409 Conflict`:
duplicate registration or event capacity reached -
`422 Unprocessable Entity`: invalid request data

#### E. API documentation

Use FastAPI's generated OpenAPI documentation at:

`http://127.0.0.1:8000/docs`

Ensure endpoints, parameters, schemas, and responses are documented.

### Bonus features

1.  **Pagination:** list endpoints use `skip` and `limit`,
    e.g. `GET /events?skip=0&limit=10`.
2.  **Search and filtering:** allow filtering by event title and event
    date, e.g. `GET /events?title=Python` and
    `GET /events?event_date=2026-11-20`.
3.  **JWT authentication:**
    -   Users can register/login and receive an access token.
    -   Event create, update, and delete operations require
        authentication.
    -   Public users can view available events.
4.  **Async database operations:** use SQLAlchemy 2.0 async engine and
    async sessions.
5.  **pytest:** test successful and failing API cases, including
    validation, duplicate registration, and capacity limits.

### Other assignment expectations

-   Public GitHub repository.
-   `main` is the stable branch.
-   Use feature branches for individual features, for example
    `feature/event-crud`, `feature/jwt-auth`, and
    `feature/registrations`.
-   Make regular commits with meaningful messages and merge completed
    features into `main`.
-   Use docstrings, meaningful names, comments where useful, consistent
    formatting, appropriate exception handling, and separation of
    business logic from API routes.
-   Submission includes source code, `requirements.txt`, `README.md`,
    Swagger screenshots, and AI usage documentation if AI tools are
    used.
-   A project demo video is mandatory. It must explain the project,
    structure, database integration, business logic, running
    application, endpoint tests, and implementation decisions.

## 4. Current project structure

The repository currently uses a flat module structure:

``` text
Corporate-Event-Management/
├── .venv/
├── .env                 # local secrets; never commit
├── .gitignore
├── requirements.txt
├── db.py
├── env.py
├── models.py
├── schemas.py
├── services.py
├── auth.py
├── main.py
└── README.md
```

A `tests/` directory and pytest files still need to be added. Keep the
existing flat structure unless there is a clear reason to change it. Do
not move files or introduce a package layout without asking first.

## 5. File responsibilities

-   `env.py`: load and validate environment configuration from `.env`.
-   `db.py`: create the async SQLAlchemy engine and session factory,
    define the declarative `Base`, provide `get_db`, create tables, test
    the connection, and dispose of the engine.
-   `models.py`: SQLAlchemy ORM models and database relationships.
-   `schemas.py`: Pydantic request and response schemas.
-   `services.py`: business logic and database operations; keep route
    handlers thin.
-   `auth.py`: password hashing/verification, JWT creation,
    registration/login logic, and current-user dependency.
-   `main.py`: FastAPI app, lifecycle, route definitions, dependency
    injection, and API metadata.
-   `requirements.txt`: Python dependencies.
-   `.env`: Neon connection string and JWT secret; do not commit.
-   `README.md`: setup, configuration, run, testing, endpoint, and demo
    instructions.

## 6. Database design

The current SQLAlchemy models are:

### `users`

-   `id`: primary key
-   `name`: employee name
-   `email`: unique employee email
-   `hashed_password`: password hash only; never store plaintext
    passwords
-   `is_active`: account status
-   `created_at`: timezone-aware creation timestamp

Relationships: - One user can create multiple events. - One user can
have multiple registrations.

### `events`

-   `id`: primary key
-   `title`
-   `description` (optional)
-   `event_date` (timezone-aware datetime)
-   `location`
-   `max_capacity` (must be greater than zero)
-   `created_by`: foreign key to `users.id`
-   `created_at`

Constraint: - `max_capacity > 0`

Relationships: - Each event has one creator. - One event can have
multiple registrations.

### `registrations`

-   `id`: primary key
-   `user_id`: foreign key to `users.id`
-   `event_id`: foreign key to `events.id`
-   `registered_at`

Constraint: - Unique `(user_id, event_id)` pair prevents duplicate
registrations at database level.

Foreign keys use cascading deletion in the current model definitions.
Consider the implications before changing cascade behavior.

## 7. Environment and database configuration

The `.env` file is expected to contain:

``` dotenv
DATABASE_URL=postgresql://USER:PASSWORD@NEON_HOST/DATABASE?sslmode=require
SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Important: - Never print, expose, paste into source control, or commit
the real Neon connection string, database password, or JWT secret. -
`.env` must be ignored by Git. - If a credential has been exposed,
rotate it in Neon and update the local `.env`. - `db.py` converts
PostgreSQL URLs to `postgresql+asyncpg` and configures SSL for Neon. -
Do not replace the async driver with a synchronous driver. - Do not put
credentials directly in Python files.

## 8. Current API routes

The current `main.py` implementation defines:

### Home and health

-   `GET /`
-   `GET /health`

### Authentication

-   `POST /auth/register`
-   `POST /auth/login`
-   `GET /auth/me`

### Events

-   `POST /events` --- authenticated
-   `GET /events` --- public; supports `skip`, `limit`, `title`, and
    `event_date`
-   `GET /events/{event_id}` --- public
-   `PUT /events/{event_id}` --- authenticated; current implementation
    permits only the event creator
-   `DELETE /events/{event_id}` --- authenticated; current
    implementation permits only the event creator

### Registrations

-   `POST /events/{event_id}/registrations` --- authenticated
-   `GET /events/{event_id}/registrations` --- authenticated in the
    current implementation
-   `DELETE /registrations/{registration_id}` --- authenticated; current
    implementation permits cancellation only by the registration owner

Note: The assignment does not explicitly require authentication for
registration endpoints or for viewing registrations. The current
implementation protects these routes. Keep this behavior unless the
project owner decides to change it, and document the choice.

## 9. Authentication design

-   Passwords are hashed using `pwdlib` with its recommended
    password-hashing configuration.
-   Login verifies the supplied password against the stored hash.
-   A successful login returns a JWT access token with:
    -   `sub`: user ID as a string
    -   `exp`: token expiration
-   The configured algorithm is `HS256`.
-   The configured token lifetime is 30 minutes by default.
-   Protected routes resolve the current active user through the bearer
    token.
-   Swagger's Authorize dialog accepts the token value; for HTTP Bearer
    auth, paste the token itself (not the word `Bearer`).

## 10. Dependencies

The current `requirements.txt` is intended to include:

``` text
fastapi>=0.115,<1.0
uvicorn[standard]>=0.30
sqlalchemy[asyncio]>=2.0,<3.0
asyncpg>=0.29
pydantic>=2.7,<3.0
python-dotenv>=1.0
python-jose[cryptography]>=3.3
pwdlib[argon2]>=0.2
email-validator>=2.0
pytest>=8.0
pytest-asyncio>=0.24
httpx>=0.27
```

If a dependency is missing or incompatible, explain why before changing
the dependency list.

## 11. How to run locally

Windows PowerShell:

``` powershell
# Create virtual environment (only once)
python -m venv .venv

# If PowerShell blocks activation, allow scripts for this terminal session only
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Start FastAPI
uvicorn main:app --reload
```

Open Swagger:

`http://127.0.0.1:8000/docs`

The FastAPI lifespan currently calls `create_tables()` on startup and
disposes the engine on shutdown.

To check Neon connectivity:

``` powershell
python -c "import asyncio; from db import check_database_connection; print(asyncio.run(check_database_connection()))"
```

Expected result: `1`.

To check model mappings:

``` powershell
python -c "from models import User, Event, Registration; from sqlalchemy.orm import configure_mappers; configure_mappers(); print('All database models loaded successfully!')"
```

To check service imports:

``` powershell
python -c "import services; print('All service functions imported successfully!')"
```

To check authentication imports:

``` powershell
python -c "import auth; print('Authentication module imported successfully!')"
```

To check the FastAPI app import:

``` powershell
python -c "import main; print('FastAPI application imported successfully!')"
```

## 12. Current development status

Based on the work completed so far:

  -----------------------------------------------------------------------
  Area                                Status
  ----------------------------------- -----------------------------------
  Python virtual environment          Completed

  Dependencies installed              Completed

  Neon PostgreSQL connection          Successful; `SELECT 1` returned `1`

  SQLAlchemy models                   Created and mapper import test
                                      passed

  Pydantic schemas                    Created and import test passed

  Neon tables (`users`, `events`,     Created successfully
  `registrations`)                    

  Business services                   Created; import test passed

  JWT authentication                  Created; import test passed

  Employee registration               Tested successfully

  Employee login                      Tested successfully; returned `200`
                                      and JWT

  Swagger authorization               Tested successfully

  Event creation                      Tested

  List events with pagination         Tested;
                                      `GET /events?skip=0&limit=10`
                                      returned `200` and two records

  Get one event                       Reported completed by project owner

  Update event                        Reported completed by project owner

  Delete event                        Reported completed by project owner

  Event registration and cancellation Guided through testing; confirm
                                      final results if continuing

  Capacity-limit test                 Planned/in progress; do not assume
                                      passed

  pytest suite                        Not yet implemented or executed

  README finalization                 Pending

  Git feature-branch workflow and     Must be checked
  commits                             

  Swagger screenshots                 Pending collection

  Demo video                          Pending
  -----------------------------------------------------------------------

Do not claim that unverified tests have passed. Ask for the latest
terminal or Swagger output when needed.

## 13. Known implementation details to review

The code was built incrementally. Before declaring the project
submission-ready, review these points carefully:

1.  **Database schema changes:** `Base.metadata.create_all()` creates
    missing tables but does not migrate existing tables when model
    definitions change. Use a migration strategy or explicit safe
    migration steps if schemas change.
2.  **Registration capacity concurrency:** the service locks the event
    row with `SELECT ... FOR UPDATE` before counting registrations.
    Verify this behavior with two concurrent requests and Neon. Keep the
    database unique constraint for duplicate prevention.
3.  **Registration cancellation:** verify that an employee cannot cancel
    another employee's registration and that missing registrations
    return `404`.
4.  **Event ownership:** current update/delete routes restrict actions
    to the event creator. Confirm this policy is acceptable for the
    assignment demonstration.
5.  **Event deletion:** verify the intended cascade behavior for
    registrations.
6.  **Event dates:** use timezone-aware datetimes consistently.
7.  **Input validation:** test whitespace-only values, invalid emails,
    missing fields, zero/negative capacity, and invalid date values.
8.  **Error handling:** ensure database transactions are rolled back
    after integrity errors and unexpected failures do not leave sessions
    in a failed state.
9.  **Password handling:** never return `hashed_password` in API
    responses.
10. **Authentication:** test missing, malformed, expired, and valid
    JWTs.
11. **Pagination/filtering:** verify boundary cases for `skip`, `limit`,
    title, and date filters.
12. **Tests:** write and actually execute pytest tests; do not treat
    test files that have not been run as completed.

Do not rewrite working files wholesale without first inspecting their
current contents and explaining the reason for the change.

## 14. Git and branch workflow

The project owner has an existing GitHub repository and is working in a
feature branch. Confirm the current branch before committing.

Useful commands:

``` powershell
git status
git branch
git switch -c feature/event-crud
git add .
git commit -m "Implement event CRUD operations"
git push -u origin feature/event-crud
```

Use separate feature branches where appropriate, such as: -
`feature/event-crud` - `feature/jwt-auth` - `feature/registrations` -
`feature/pytest-tests`

Do not force-push, delete branches, or merge into `main` without the
project owner's explicit instruction. Never stage `.env`, `.venv/`,
cache files, or secrets.

## 15. Working instructions for AI coding assistants

When assisting with this repository:

1.  Treat the six-page assignment brief as the source of truth for
    requirements.
2.  Explain each step in beginner-friendly language. The project owner
    wants to learn and must be able to explain the code in the mandatory
    demo video.
3.  Give complete, paste-ready code and identify the exact filename
    where it belongs.
4.  Work one step at a time. Ask the owner to run the relevant command
    or API test and share the result before proceeding.
5.  Preserve the existing project structure and working code unless a
    change is necessary.
6.  Do not invent test results, database contents, branch names, or
    GitHub status.
7.  Distinguish mandatory assignment requirements from bonus features
    and optional improvements.
8.  Explain any changes to schemas, database tables, API contracts, or
    security behavior before applying them.
9.  Keep secrets out of code, logs, examples, commits, and
    documentation.
10. Prefer simple, maintainable code appropriate for a student FastAPI
    assignment over unnecessary abstractions.
11. Add docstrings and meaningful comments, but avoid noisy comments
    that merely repeat the code.
12. When fixing a bug, explain its cause, provide the smallest safe fix,
    and give a command or Swagger test to verify it.
13. Keep `README.md` and this `CLAUDE.md` consistent with the actual
    implementation.
14. Do not claim the assignment is complete until mandatory features,
    tests, documentation, GitHub submission requirements, and the demo
    preparation have been verified.

## 16. Immediate next tasks

Continue in this order:

1.  Finish and record the event capacity test using two different
    employee accounts.
2.  Verify registration listing, duplicate-registration rejection, and
    cancellation ownership.
3.  Test pagination and title/date filtering.
4.  Add a pytest test suite using an isolated test database or carefully
    isolated test setup; avoid destructive tests against production Neon
    data.
5.  Run the complete test suite and fix failures.
6.  Review error handling, security, concurrency, and schema
    consistency.
7.  Complete `README.md` with installation, `.env` configuration,
    running, endpoints, and test commands.
8.  Confirm `.gitignore` excludes `.env`, `.venv/`, Python caches, and
    test caches.
9.  Commit changes on feature branches and merge into `main` only with
    the owner's approval.
10. Capture Swagger screenshots and prepare the mandatory demo video.
11. Prepare transparent AI usage documentation (tools/models, prompts,
    relevant chat history, and configuration) as requested by the
    assignment.

------------------------------------------------------------------------

**Core principle:** Build a working, tested, understandable Corporate
Event Management API that satisfies the assignment. The project owner
must understand and be able to explain every important implementation
decision.
