import enum


class Role(str, enum.Enum):
    """User roles. Add more as your app grows."""

    USER = "USER"
    ADMIN = "ADMIN"
