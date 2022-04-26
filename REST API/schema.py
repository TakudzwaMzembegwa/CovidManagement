def user_serializer(user) -> dict:
    return {
        "id": int(user["_id"]),
        "mask": user["mask"],
        "desk": user["desk"],
        "accessCounter": int(user["accessCounter"]),
        "date": user["date"],
    }


def users_serializer(users) -> list:
    return [user_serializer(user) for user in users]


def building_serializer(room) -> dict:
    return {
        "id": str(room["_id"]),
        "desks": room["desks"],
        "date": room["date"]
    }


F = {"A1": "FREE", "A2": "OFF", "A3": "FREE", "A4": "OFF", "A5": "FREE", "A6": "FREE", "A7": "FREE", "B1": "FREE", "B2": "OFF", "B3": "FREE", "B4": "OFF", "B5": "FREE", "B6": "FREE", "B7": "FREE", "C1": "FREE", "C2": "OFF", "C3": "FREE", "C4": "OFF", "C5": "FREE", "C6": "FREE", "C7": "FREE", "D1": "FREE", "D2": "OFF", "D3": "FREE",
     "D4": "OFF", "D5": "FREE", "D6": "FREE", "D7": "FREE", "E1": "FREE", "E2": "OFF", "E3": "FREE", "E4": "OFF", "E5": "FREE", "E6": "FREE", "E7": "FREE", "F1": "FREE", "F2": "OFF", "F3": "FREE", "F4": "OFF", "F5": "FREE", "F6": "FREE", "F7": "FREE", "G1": "FREE", "G2": "OFF", "G3": "FREE", "G4": "OFF", "G5": "FREE", "G6": "FREE", "G7": "FREE"}
