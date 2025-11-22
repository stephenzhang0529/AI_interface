# create_initial_user.py
import database as db
import os

def create_default_user():
    """Creates a default user in the database."""
    username = "user"
    password = "123"
    email = "test@example.com" # Changed to a valid email format

    print(f"Attempting to create user: {username}")

    # Ensure tables are created (this is already called when database.py is imported, but safe to call again)
    db.create_tables()

    # Check if the user already exists
    existing_user = db.get_user_by_username(username)
    if existing_user:
        print(f"User '{username}' already exists in the database. Skipping creation.")
        return

    result = db.add_user(username, email, password)

    if result is True:
        print(f"Successfully created user '{username}' with email '{email}'.")
    elif result == "username_exists":
        print(f"User '{username}' already exists. No new user created.")
    elif result == "email_exists":
        print(f"Email '{email}' is already registered. No new user created.")
    else:
        print(f"Failed to create user '{username}'.")

if __name__ == "__main__":
    create_default_user()