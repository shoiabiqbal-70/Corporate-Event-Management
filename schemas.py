
"""
Pydantic schemas for Corporate Event Management API.

These schemas validate incoming requests and structure API responses.
"""

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


# =========================================================
# 1. USER SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    """Schema for creating a new employee account."""

    name: str = Field(
        min_length=2,
        max_length=100,
        description="Employee's full name",
    )

    email: EmailStr = Field(
        description="Employee's valid email address",
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        description="Account password (minimum 8 characters)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        """Reject names containing only whitespace."""

        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty.")

        return value


class UserLogin(BaseModel):
    """Schema for employee login."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Schema for returning employee information."""

    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# 2. TOKEN SCHEMAS
# =========================================================

class Token(BaseModel):
    """Schema for JWT access token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for information extracted from a JWT."""

    user_id: int | None = None


# =========================================================
# 3. EVENT SCHEMAS
# =========================================================

class EventBase(BaseModel):
    """Common fields shared by event creation and updating."""

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Title of the corporate event",
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
        description="Detailed event description",
    )

    event_date: datetime = Field(
        description="Event date and time",
    )

    location: str = Field(
        min_length=1,
        max_length=255,
        description="Location where the event will take place",
    )

    max_capacity: int = Field(
        gt=0,
        description="Maximum number of attendees",
    )

    @field_validator("title", "location")
    @classmethod
    def validate_required_text(cls, value):
        """Reject empty or whitespace-only text."""

        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class EventCreate(EventBase):
    """Schema for creating a new event."""

    pass


class EventUpdate(BaseModel):
    """Schema for updating an existing event.

    All fields are optional so that users can update
    only the information they want to change.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    event_date: datetime | None = None

    location: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    max_capacity: int | None = Field(
        default=None,
        gt=0,
    )

    @field_validator("title", "location")
    @classmethod
    def validate_optional_text(cls, value):
        """Reject empty text when a field is supplied."""

        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError("This field cannot be empty.")

        return value

    @model_validator(mode="after")
    def validate_update_fields(self):
        """Require at least one field to be updated."""

        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one field to update."
            )

        return self


class EventOut(BaseModel):
    """Schema for returning event information."""

    id: int
    title: str
    description: str | None
    event_date: datetime
    location: str
    max_capacity: int
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# 4. REGISTRATION SCHEMAS
# =========================================================

class RegistrationCreate(BaseModel):
    """Schema for registering an employee for an event.

    The employee ID comes from the authenticated JWT token,
    so it is not accepted in the request body.
    """

    pass


class RegistrationOut(BaseModel):
    """Schema for returning registration information."""

    id: int
    user_id: int
    event_id: int
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# 5. MESSAGE SCHEMAS
# =========================================================

class MessageResponse(BaseModel):
    """Standard response for successful operations."""

    message: str
