import npyscreen
import requests
import curses
import logging

# Set up logging
logging.basicConfig(filename='npyscreen.log', level=logging.DEBUG)

def get_users():
    response = requests.get('http://localhost:8000/users/')
    return response.json()

def delete_user(user_id):
    response = requests.delete(f'http://localhost:8000/users/{user_id}')
    if response.status_code == 200:
        print("User deleted successfully.")
    else:
        print("Failed to delete user.")

def create_user(user):
    response = requests.post('http://localhost:8000/users/', json=user)
    if response.status_code == 200:
        print("User created successfully.")
    else:
        print("Failed to create user.")

def update_user(user_id, user):
    response = requests.put(f'http://localhost:8000/users/{user_id}', json=user)
    if response.status_code == 200:
        print("User updated successfully.")
    else:
        print("Failed to update user.")

# Main menu
class MainMenu(npyscreen.ActionForm):
    def create(self):
        self.add(npyscreen.TitleText, name='Welcome to FreeHCI!', editable=False)
        self.add(npyscreen.ButtonPress, name='Users', when_pressed_function=self.when_users_pressed)
        self.add(npyscreen.ButtonPress, name='Groups', when_pressed_function=self.when_groups_pressed)
        self.add(npyscreen.ButtonPress, name='Equipment', when_pressed_function=self.when_equipment_pressed)
        self.add(npyscreen.ButtonPress, name='Quit', when_pressed_function=self.when_quit_pressed)

    def when_users_pressed(self):
        self.parentApp.getForm('USERLIST').value = None
        self.parentApp.switchForm('USERLIST')

    def when_groups_pressed(self):
        npyscreen.notify_confirm("Groups functionality not implemented yet", "Error")

    def when_equipment_pressed(self):
        npyscreen.notify_confirm("Equipment functionality not implemented yet", "Error")
        
    def when_quit_pressed(self):
        self.parentApp.switchForm(None)


class UserForm(npyscreen.ActionForm):
    def create(self):
        self.add(npyscreen.TitleText, name='User Details:', editable=False)
        self.username = self.add(npyscreen.TitleText, name='Username:', editable=False)
        self.email = self.add(npyscreen.TitleText, name='Email:', editable=False)
        self.id = self.add(npyscreen.TitleText, name='ID:', editable=False)
        self.delete_button = self.add(npyscreen.ButtonPress, name='Delete User')
    
    def setup(self, user):
        logging.debug(f'UserForm.setup called with user: {user}')
        self.username.value = f'Username: {user["username"]}'
        self.email.value = f'Email: {user["email"]}'
        self.id.value = f'ID: {user["id"]}'
        self.delete_button.when_pressed_function = lambda: delete_user(user["id"])
        #self.display()

    def afterEditing(self):
        self.parentApp.setNextForm('USERLIST')
        
    def beforeEditing(self):
        if hasattr(self, 'selected_user'):
            self.setup(self.selected_user)


class UserList(npyscreen.ActionForm):
    def create(self):
        self.add_handlers({"^Q": self.when_exit})  # Add a handler for ctrl-q
        
        self.add(npyscreen.TitleText, name='[ctrl-q: back]', editable=False)
        self.users_list = self.add(npyscreen.BoxTitle, name='Users:', max_height=15, footer="Press enter to edit user, or ctrl-q to go back")
        self.users_list.values = [f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}" for user in get_users()]

        # This causes the function to be called twice on first keypress, and then works as expected
        # Log output:
        # DEBUG:root:when_enter_pressed called with value: None
        # DEBUG:root:when_enter_pressed called with value: None        
        self.users_list.entry_widget.when_value_edited = self.when_enter_pressed
        

    # this should be triggered when user presses enter on a user in the list               
    def when_enter_pressed(self, *args, **keywords):
        logging.debug(f'when_enter_pressed called with args: {args} and keywords: {keywords}')
        logging.debug(f'when_enter_pressed called with value: {self.users_list.entry_widget.value}') # DEBUG:root:when_enter_pressed called with value: 8
        if self.users_list.entry_widget.value is not None and self.users_list.entry_widget.value < len(self.users_list.values):
            selected_user = get_users()[self.users_list.entry_widget.value]
            logging.debug(f'Selected user: {selected_user}') # DEBUG:root:Selected user: {'password': '$2b$12$kRE5nZ0H.nUX6v5Y0JGpo.rxRb3/pVRHXLLXTT8Iq.DrrTw5TfSYu', 'username': 'sofagris', 'email': 'sofagris@freehci.com', 'id': 10}
            self.parentApp.getForm('USERFORM').setup(selected_user)
            self.parentApp.setNextForm('USERFORM')  # Set the next form here
        #else:
        #    npyscreen.notify_confirm("No user selected", "Error")

    def afterEditing(self):
        self.parentApp.setNextForm('MAIN')  # This will only be called if the form is exited without selecting a user

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def when_exit(self, *args, **keywords):
        self.parentApp.switchFormPrevious()

        
class Application(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', MainMenu, name="Main Menu")
        self.addForm('USERLIST', UserList, name="User Management")
        self.addForm('USERFORM', UserForm, name="User Form")

if __name__ == "__main__":
    App = Application().run()
