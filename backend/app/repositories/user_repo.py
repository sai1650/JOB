from sqlalchemy.orm import Session
from app.models.user import User
from app.services.auth import hash_password


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, name: str, email: str, password: str, is_admin: bool = False
    ) -> User:
        """Create a new user."""
        hashed_password = hash_password(password)
        user = User(
            name=name,
            email=email,
            hashed_password=hashed_password,
            is_admin=is_admin,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> User:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> User:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all(self) -> list:
        """Get all users."""
        return self.db.query(User).all()

    def update_active_status(self, user_id: str, is_active: bool) -> User:
        """Update user active status."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = is_active
            self.db.commit()
            self.db.refresh(user)
        return user
