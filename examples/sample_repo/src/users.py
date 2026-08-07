def get_users() -> list[dict]:
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]


def find_user(users: list[dict], user_id: int) -> dict | None:
    for user in users:
        if user["id"] == user_id:
            return user
    return None
