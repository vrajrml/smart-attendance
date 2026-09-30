from getpass import getpass

from app import create_app, db
from app.models import User


def create_admin():
    app = create_app()

    with app.app_context():

        username = input("Enter admin username: ").strip()

        if not username:
            print("Username cannot be empty.")
            return

        existing_user = db.session.execute(
            db.select(User).where(
                User.username == username
            )
        ).scalar_one_or_none()

        if existing_user:
            print("A user with that username already exists.")
            return

        password = getpass("Enter admin password: ")
        confirm_password = getpass(
            "Confirm admin password: "
        )

        if password != confirm_password:
            print("Passwords do not match.")
            return

        if len(password) < 6:
            print("Password must contain at least 6 characters.")
            return

        user = User(
            username=username,
            role="admin"
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(
            f"Admin user '{username}' created successfully."
        )


if __name__ == "__main__":
    create_admin()
