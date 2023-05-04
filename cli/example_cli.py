# This is a example of a CLI script that can be used to interact with the database.
# This script is not used in the project, but it can be used as a template for future functionality.
# Usage:
# python example_cli.py add --name "example" --type "typeA" --height 123
# python example_cli.py delete --name "example"
# python example_cli.py modify --id 1 --type "typeB" --height 456
# python example_cli.py rename --name "example" --newname "new_example"

# Import the required modules
import argparse

def add(name, type_, height):
    print(f"Adding: name={name}, type={type_}, height={height}")

def delete(name, id_):
    print(f"Deleting: name={name}, id={id_}")

def modify(name, id_, type_, height):
    print(f"Modifying: name={name}, id={id_}, type={type_}, height={height}")

def rename(name, id_, newname):
    print(f"Renaming: name={name}, id={id_}, newname={newname}")

parser = argparse.ArgumentParser(description="Command line script")

subparsers = parser.add_subparsers(dest="command")

add_parser = subparsers.add_parser("add", help="Add a new animal")
add_parser.add_argument("--name", required=True, help="Name of the animal")
add_parser.add_argument("--type", required=True, help="Type of animal")
add_parser.add_argument("--height", required=True, type=int, help="Height of the animal")

delete_parser = subparsers.add_parser("delete")
group1 = delete_parser.add_mutually_exclusive_group(required=True)
group1.add_argument("--name")
group1.add_argument("--id", type=int)

modify_parser = subparsers.add_parser("modify")
group2 = modify_parser.add_mutually_exclusive_group(required=True)
group2.add_argument("--name")
group2.add_argument("--id", type=int)
modify_parser.add_argument("--type", required=True)
modify_parser.add_argument("--height", required=True, type=int)

rename_parser = subparsers.add_parser("rename")
group3 = rename_parser.add_mutually_exclusive_group(required=True)
group3.add_argument("--name")
group3.add_argument("--id", type=int)
rename_parser.add_argument("--newname", required=True)

args = parser.parse_args()

if args.command == "add":
    add(args.name, args.type, args.height)
elif args.command == "delete":
    delete(args.name, args.id)
elif args.command == "modify":
    modify(args.name, args.id, args.type, args.height)
elif args.command == "rename":
    rename(args.name, args.id, args.newname)
else:
    parser.print_help()
