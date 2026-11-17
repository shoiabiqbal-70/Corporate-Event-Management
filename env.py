
"""
Application configuration.

Loads environment variables from the .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Stores application configuration."""

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")

    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    def validate(self):
        """Check whether essential settings are configured."""

        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is missing from .env")

        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY is missing from .env")


settings = Settings()
settings.validate()
