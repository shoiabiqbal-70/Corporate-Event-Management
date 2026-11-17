
"""
Corporate Event Management API.

Main application entry point.

Built with FastAPI, PostgreSQL, SQLAlchemy 2.0,
Pydantic, and JWT authentication.
"""

from contextlib import asynccontextmanager
from datetime import date

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Query,
    status,
    Response,
)

from sqlalchemy.ext.asyncio import AsyncSession

# Database imports
from db import (
    get_db,
    create_tables,
    close_database_connection,
)

# Model imports
from models import User, Event, Registration

# Schema imports
from schemas import (
    UserCreate,
    UserLogin,
    UserOut,
    Token,
    EventCreate,
    EventUpdate,
    EventOut,
    RegistrationOut,
    MessageResponse,
)

# Business logic imports
import services

# Authentication imports
from auth import (
    register_user,
    authenticate_user,
    get_current_user,
)


# =========================================================
# 1. APPLICATION LIFECYCLE
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Run database initialization when the application starts
    and close database connections when it shuts down.
    """

    print("Starting Corporate Event Management API...")

    await create_tables()

    print("Database initialized successfully!")

    yield

    await close_database_connection()

    print("Application database connections closed.")


# =========================================================
# 2. FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Corporate Event Management API",
    description="""
    REST API for Acme Corp's internal event management system.

    Features:
    - Employee registration and login
    - JWT authentication
    - Event CRUD operations
    - Employee event registrations
    - Registration cancellation
    - Pagination and filtering
    - Neon PostgreSQL database
    """,
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# 3. ROOT ENDPOINT
# =========================================================

@app.get("/", tags=["Home"])
async def home():
    """Welcome endpoint."""

    return {
        "message": "Welcome to Acme Corp Event Management API",
        "documentation": "/docs",
        "version": "1.0.0",
    }


# =========================================================
# 4. AUTHENTICATION ENDPOINTS
# =========================================================

@app.post(
    "/auth/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
async def create_account(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new employee account."""

    return await register_user(db, user_data)


@app.post(
    "/auth/login",
    response_model=Token,
    tags=["Authentication"],
)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate an employee and return a JWT token."""

    return await authenticate_user(db, login_data)


@app.get(
    "/auth/me",
    response_model=UserOut,
    tags=["Authentication"],
)
async def get_my_account(
    current_user: User = Depends(get_current_user),
):
    """Return the currently authenticated employee."""

    return current_user


# =========================================================
# 5. CREATE EVENT
# =========================================================

@app.post(
    "/events",
    response_model=EventOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Events"],
)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new corporate event.

    Authentication required.
    """

    return await services.create_event(
        db,
        event_data,
        current_user.id,
    )


# =========================================================
# 6. GET ALL EVENTS
# =========================================================

@app.get(
    "/events",
    response_model=list[EventOut],
    tags=["Events"],
)
async def get_events(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    title: str | None = Query(default=None, min_length=1),
    event_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve events with pagination and optional filtering.

    Public endpoint.
    """

    return await services.get_all_events(
        db=db,
        skip=skip,
        limit=limit,
        title=title,
        event_date=event_date,
    )


# =========================================================
# 7. GET EVENT BY ID
# =========================================================

@app.get(
    "/events/{event_id}",
    response_model=EventOut,
    tags=["Events"],
)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a specific event.

    Public endpoint.
    """

    return await services.get_event_by_id(
        db,
        event_id,
    )


# =========================================================
# 8. UPDATE EVENT
# =========================================================

@app.put(
    "/events/{event_id}",
    response_model=EventOut,
    tags=["Events"],
)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing event.

    Authentication required.
    """

    # Only the event creator can update the event.
    event = await services.get_event_by_id(
        db,
        event_id,
    )

    if event.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update events you created.",
        )

    return await services.update_event(
        db,
        event_id,
        event_data,
    )


# =========================================================
# 9. DELETE EVENT
# =========================================================

@app.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Events"],
)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an existing event.

    Authentication required.
    """

    # Only the event creator can delete the event.
    event = await services.get_event_by_id(
        db,
        event_id,
    )

    if event.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete events you created.",
        )

    await services.delete_event(
        db,
        event_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# =========================================================
# 10. REGISTER FOR EVENT
# =========================================================

@app.post(
    "/events/{event_id}/registrations",
    response_model=RegistrationOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Registrations"],
)
async def register_for_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register the authenticated employee for an event."""

    return await services.register_for_event(
        db,
        event_id,
        current_user.id,
    )


# =========================================================
# 11. GET EVENT REGISTRATIONS
# =========================================================

@app.get(
    "/events/{event_id}/registrations",
    response_model=list[RegistrationOut],
    tags=["Registrations"],
)
async def get_registrations(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve registrations for a specific event.

    Authentication required.
    """

    return await services.get_event_registrations(
        db,
        event_id,
    )


# =========================================================
# 12. CANCEL REGISTRATION
# =========================================================

@app.delete(
    "/registrations/{registration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Registrations"],
)
async def cancel_registration(
    registration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel the authenticated employee's registration."""

    await services.cancel_registration(
        db,
        registration_id,
        current_user.id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# =========================================================
# 13. HEALTH CHECK
# =========================================================

@app.get(
    "/health",
    tags=["Health"],
)
async def health_check():
    """Check whether the API application is running."""

    return {
        "status": "healthy",
        "application": "Corporate Event Management API",
    }
