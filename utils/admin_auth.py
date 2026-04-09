authorized_admins = set()


def grant_admin_access(user_id: int) -> None:
    authorized_admins.add(int(user_id))


def has_admin_access(user_id: int) -> bool:
    return int(user_id) in authorized_admins
