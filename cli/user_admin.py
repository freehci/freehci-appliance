# File: cli\user_admin.py
# This file is used to create a CLI tool to manage users in the database.

import sys
sys.path.append("..")


import argparse
from sqlalchemy.orm import Session
from models import crud, database
from models.user_schemas import UserCreate, UserUpdate

# CLI functions
def list_users(db: Session):
    users = crud.get_users(db)
    for user in users:
        print(user)

def find_user(db: Session, user_id: int):
    user = crud.get_user_by_id(db, user_id)
    if user:
        print(user)
    else:
        print(f"User with ID {user_id} not found")

def create_user(db: Session, username: str, email: str, password: str):
    user_create = UserCreate(username=username, email=email, password=password)
    user = crud.create_user(db, user_create)
    print(f"User created with ID {user.id}")

def modify_user_by_id(db: Session, user_id: int, username: str, email: str):
    # Implement modify user logic here
    user_modify = UserUpdate(id=user_id, username=username, email=email)
    user = crud.update_user_by_id(db, user_id, user_modify)
    print(f"User modified with ID {user.id}")

def main():
    parser = argparse.ArgumentParser(description="User administration tool")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List all users")
    
    find_parser = subparsers.add_parser("find", help="Find a user by ID")
    find_parser.add_argument("user_id", type=int, help="User ID to find")
    
    delete_parser = subparsers.add_parser("delete", help="Delete a user by username")
    delete_parser.add_argument("username", help="Username to delete")

    create_parser = subparsers.add_parser("create", help="Create a new user")
    create_parser.add_argument("username", help="Username for the new user")
    create_parser.add_argument("email", help="Email for the new user")
    create_parser.add_argument("password", help="Password for the new user")

    modify_parser = subparsers.add_parser("modify", help="Modify an existing user")
    modify_parser.add_argument("user_id", type=int, help="User ID to modify")
    modify_parser.add_argument("username", help="New username for the user")
    modify_parser.add_argument("email", help="New email for the user")

    args = parser.parse_args()

    with database.SessionLocal() as db:
        if args.command == "list":
            list_users(db)
        elif args.command == "find":
            find_user(db, args.user_id)
        elif args.command == "create":
            create_user(db, args.username, args.email, args.password)
        elif args.command == "modify":
            modify_user_by_id(db, args.user_id, args.username, args.email)
        elif args.command == "delete":
            ...
            
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
