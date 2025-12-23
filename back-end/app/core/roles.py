# Central role definitions and helpers

ROLE_ADMIN = 1
ROLE_AGENT = 2
ROLE_CLIENT = 3

ROLE_NAME_TO_ID = {
    "admin": ROLE_ADMIN,
    "agent": ROLE_AGENT,
    "client": ROLE_CLIENT,
}

ROLE_ID_TO_NAME = {v: k for k, v in ROLE_NAME_TO_ID.items()}


def role_name_to_id(name: str) -> int | None:
    return ROLE_NAME_TO_ID.get(name)


def role_id_to_name(rid: int) -> str | None:
    return ROLE_ID_TO_NAME.get(rid)