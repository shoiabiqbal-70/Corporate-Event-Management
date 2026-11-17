
"""
Business logic for Corporate Event Management API.

Handles event CRUD operations and employee registrations.
All database operations are asynchronous.
"""

from datetime import date

from fastapi import HTTPException, status

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Event, Registration

from schemas import EventCreate, EventUpdate


# =========================================================
# 1. CREATE EVENT
# =========================================================

async def create_event(
    db: AsyncSession,
    event_data: EventCreate,
    user_id: int,
):
    """Create a new corporate event."""

    # Check whether the employee exists.
    user = await db.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active employee not found.",
        )

    # Convert Pydantic data into a dictionary.
    event_dict = event_data.model_dump()

    # Create SQLAlchemy event object.
    new_event = Event(
        **event_dict,
        created_by=user_id,
    )

    db.add(new_event)

    await db.commit()
    await db.refresh(new_event)

    return new_event


# =========================================================
# 2. GET ALL EVENTS
# =========================================================

async def get_all_events(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    title: str | None = None,
    event_date: date | None = None,
):
    """Retrieve events with pagination and filtering."""

    query = select(Event)

    # Search events by title.
    if title:
        query = query.where(
            Event.title.ilike(f"%{title.strip()}%")
        )

    # Filter events by date.
    if event_date:
        query = query.where(
            func.date(Event.event_date) == event_date
        )

    # Newest events first.
    query = query.order_by(Event.event_date.asc())

    # Apply pagination.
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)

    return result.scalars().all()


# =========================================================
# 3. GET EVENT BY ID
# =========================================================

async def get_event_by_id(
    db: AsyncSession,
    event_id: int,
):
    """Retrieve a specific event using its ID."""

    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )

    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    return event


# =========================================================
# 4. UPDATE EVENT
# =========================================================

async def update_event(
    db: AsyncSession,
    event_id: int,
    event_data: EventUpdate,
):
    """Update an existing corporate event."""

    event = await get_event_by_id(db, event_id)

    # Get only the fields supplied by the employee.
    update_data = event_data.model_dump(
        exclude_unset=True
    )

    # Prevent null values for required event fields.
    required_fields = {
        "title",
        "event_date",
        "location",
        "max_capacity",
    }

    for field in required_fields:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null.",
            )

    # Check existing registrations before reducing capacity.
    if (
        "max_capacity" in update_data
        and update_data["max_capacity"] is not None
    ):

        registration_count = await db.scalar(
            select(func.count(Registration.id)).where(
                Registration.event_id == event_id
            )
        )

        if update_data["max_capacity"] < registration_count:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Maximum capacity cannot be lower "
                    "than the current number of registrations."
                ),
            )

    # Update supplied fields.
    for key, value in update_data.items():
        setattr(event, key, value)

    await db.commit()
    await db.refresh(event)

    return event


# =========================================================
# 5. DELETE EVENT
# =========================================================

async def delete_event(
    db: AsyncSession,
    event_id: int,
):
    """Delete an event from the database."""

    event = await get_event_by_id(db, event_id)

    await db.delete(event)
    await db.commit()

    return True


# =========================================================
# 6. REGISTER FOR EVENT
# =========================================================

async def register_for_event(
    db: AsyncSession,
    event_id: int,
    user_id: int,
):
    """Register an employee for a corporate event."""

    # Check whether the employee exists and is active.
    user = await db.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active employee not found.",
        )

    # Lock the event row to prevent concurrent
    # registrations from exceeding event capacity.
    result = await db.execute(
        select(Event)
        .where(Event.id == event_id)
        .with_for_update()
    )

    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    # Check for duplicate registration.
    existing_registration = await db.execute(
        select(Registration).where(
            Registration.event_id == event_id,
            Registration.user_id == user_id,
        )
    )

    if existing_registration.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already registered for this event.",
        )

    # Count existing registrations.
    registration_count = await db.scalar(
        select(func.count(Registration.id)).where(
            Registration.event_id == event_id
        )
    )

    # Check event capacity.
    if registration_count >= event.max_capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event capacity has been reached.",
        )

    # Create registration.
    new_registration = Registration(
        user_id=user_id,
        event_id=event_id,
    )

    db.add(new_registration)

    try:
        await db.commit()
        await db.refresh(new_registration)

    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration already exists.",
        )

    return new_registration


# =========================================================
# 7. GET EVENT REGISTRATIONS
# =========================================================

async def get_event_registrations(
    db: AsyncSession,
    event_id: int,
):
    """Retrieve all registrations for a specific event."""

    # Verify that the event exists.
    await get_event_by_id(db, event_id)

    result = await db.execute(
        select(Registration)
        .where(Registration.event_id == event_id)
        .order_by(Registration.registered_at.desc())
    )

    return result.scalars().all()


# =========================================================
# 8. CANCEL REGISTRATION
# =========================================================

async def cancel_registration(
    db: AsyncSession,
    registration_id: int,
    user_id: int,
):
    """Cancel an employee's own event registration."""

    result = await db.execute(
        select(Registration).where(
            Registration.id == registration_id
        )
    )

    registration = result.scalar_one_or_none()

    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found.",
        )

    # Employees can only cancel their own registrations.
    if registration.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot cancel another employee's registration.",
        )

    await db.delete(registration)
    await db.commit()

    return True
