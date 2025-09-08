from typing import Optional

import domain


def seed_admin(username: str = "admin", password: str = "admin") -> Optional[int]:
	try:
		uid = domain.create_user(username=username, password=password, role="admin")
		return uid
	except Exception as e:
		return None


if __name__ == "__main__":
	seed_admin()

