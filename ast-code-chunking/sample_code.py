import hashlib
from datetime import datetime


def generate_user_id(email: str) -> str:
    """Generate a deterministic user ID from an email address."""
    normalized_email = email.strip().lower()
    return hashlib.sha256(normalized_email.encode()).hexdigest()[:12]


def validate_email(email: str) -> bool:
    """Perform a simple email validation."""
    return "@" in email and "." in email.split("@")[-1]


class UserService:
    """Service responsible for user-related operations."""

    def __init__(self):
        self.users = {}

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.strip().title()

    def create_user(self, name: str, email: str) -> dict:
        if not validate_email(email):
            raise ValueError("Invalid email address")

        user_id = generate_user_id(email)

        user = {
            "id": user_id,
            "name": name,
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
        }

        self.users[user_id] = user
        return user

    def get_user(self, user_id: str) -> dict | None:
        return self.users.get(user_id)

    def delete_user(self, user_id: str) -> bool:
        if user_id not in self.users:
            return False

        del self.users[user_id]
        return True

    


class AuditLogger:
    """Records application events."""

    def log(self, event: str) -> None:
        timestamp = datetime.utcnow().isoformat()
        print(f"[{timestamp}] {event}")


def main():
    service = UserService()
    logger = AuditLogger()

    user = service.create_user(
        name="Alice",
        email="alice@example.com",
    )

    logger.log(f"Created user {user['id']}")

    APP_NAME = "AST Code Chunking Demo"


def require_logging(func):
    """Example decorator."""
    return func


@require_logging
def process_user(user_id: str) -> str:
    return f"Processing {user_id}"


async def fetch_user(user_id: str) -> dict:
    return {
        "id": user_id,
        "status": "active",
    }


if __name__ == "__main__":
    main()