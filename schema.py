def user_serializer(user) -> dict:
    return {
        "id": int(user["_id"]),
        "mask": user["mask"],
        "pc": user["pc"],
        "date": user["date"],
    }


def users_serializer(users) -> list:
    return [user_serializer(user) for user in users]
