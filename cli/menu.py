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
        print("[User deleted successfully.]")
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
        
    def on_cancel(self):
        self.parentApp.switchForm(None)
        
    def afterEditing(self):
        pass


class UserForm(npyscreen.ActionForm):
    def create(self):
        self.add(npyscreen.TitleText, name='User Details:', editable=False)
        self.username = self.add(npyscreen.TitleText, name='Username:', editable=True)
        self.email = self.add(npyscreen.TitleText, name='Email:', editable=True)
        self.id = self.add(npyscreen.TitleText, name='ID:', editable=False)
        self.delete_button = self.add(npyscreen.ButtonPress, name='Delete User')
        
    
    def setup(self, user):
        logging.debug(f'UserForm.setup called with user: {user}')
        self.username.value = f'{user["username"]}'
        self.email.value = f'{user["email"]}'
        self.id.value = f'{user["id"]}'
        self.delete_button.when_pressed_function = lambda: delete_user(user["id"])
        self.display()

    def afterEditing(self):
        self.parentApp.setNextForm('USERLIST')
        
    def beforeEditing(self):
        if hasattr(self, 'selected_user'):
            self.setup(self.selected_user)


class UserList(npyscreen.ActionForm):
    def create(self):
        self.add_handlers({"^Q": self.when_exit})  # Add a handler for ctrl-q
        self.add_handlers({"+": self.when_plus_pressed})  # Add a handler for ctrl-q
        self.add_handlers({"-": self.when_minus_pressed})  # Add a handler for ctrl-q
        
        self.add(npyscreen.TitleText, name='[ctrl-q: back]', editable=False)
        self.users_list = self.add(npyscreen.BoxTitle, name='Users:', max_height=15, footer="Press enter to edit user, or ctrl-q to go back")
        self.users_list.values = [f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}" for user in get_users()]

        # Add help text
        
        self.help_text = self.add(npyscreen.BoxTitle, name='Help Text:', value='This is some help text.', editable=False)
        self.help_text.values = [
            f"Press enter or space to edit user, or ctrl-q to go back", 
            f"Press '+' to create new user",
            f"Press '-' to delete user",
            ]
        
        # This causes the function to be called twice on first keypress, and then works as expected
        # Log output:
        # DEBUG:root:when_enter_pressed called with value: None
        # DEBUG:root:when_enter_pressed called with value: None        
        self.users_list.entry_widget.when_value_edited = self.when_enter_pressed
        self.users_list.entry_widget.when_cursor_moved = self.when_cursor_moved
        

    # this should be triggered when user presses enter on a user in the list               
    def when_enter_pressed(self, *args, **keywords):
        logging.debug(f'when_enter_pressed called with args: {args} and keywords: {keywords}')
        logging.debug(f'when_enter_pressed called with value: {self.users_list.entry_widget.value}') 
        if self.users_list.entry_widget.value is not None and self.users_list.entry_widget.value < len(self.users_list.values):
            selected_user = get_users()[self.users_list.entry_widget.value]
            logging.debug(f'Selected user: {selected_user}') 
            self.parentApp.getForm('USERFORM').setup(selected_user)
            #self.parentApp.setNextForm('USERFORM')  # Set the next form here
            #self.parentApp.getForm('USERFORM').display()
            
            self.parentApp.switchForm('USERFORM') 
            self.editing = False
            
        #else:
        #    npyscreen.notify_confirm("No user selected", "Error")

    def when_cursor_moved(self, *args, **keywords):
        logging.debug(f'when_cursor_moved called with args: {args} and keywords: {keywords}')
        logging.debug(f'when_cursor_moved called with value: {self.users_list.entry_widget.value}') 
        if self.users_list.entry_widget.value is not None and self.users_list.entry_widget.value < len(self.users_list.values):
            selected_user = get_users()[self.users_list.entry_widget.value]
            logging.debug(f'Selected user: {selected_user}') 
    

    # Add user
    def when_plus_pressed(self, *args, **keywords):
        logging.debug(f'when_plus_pressed called with args: {args} and keywords: {keywords}')
        self.parentApp.getForm('USERFORM').setup({"username": "", "email": "", "id": ""})
        self.parentApp.switchForm('USERFORM')
        
    # Delete user
    def when_minus_pressed(self, *args, **keywords):
        logging.debug(f'when_minus_pressed called with args: {args} and keywords: {keywords}')
        logging.debug(f'when_minus_pressed called with value: {self.users_list.entry_widget.value}')
        logging.debug(f'user list values: {self.users_list.values}') 
        logging.debug(f'user list values: {self.users_list.entry_widget.value}')
        #logging.debug(f'user list values: {self.users_list.entry_widget.selected_line}')
        logging.debug(f'user list cursor line: {self.users_list.entry_widget.cursor_line}')
        
        if (npyscreen.notify_yes_no("Are you sure you want to delete this user?", "Delete user")):
        
            logging.debug(f'when_minus_pressed called with value: {self.users_list.values[self.users_list.entry_widget.cursor_line]}')
            
            #if self.users_list.entry_widget.value is not None and self.users_list.entry_widget.value < len(self.users_list.values):
            selected_user_string = self.users_list.values[self.users_list.entry_widget.cursor_line]
            
            logging.debug(f'Selected user: {selected_user_string}') 
            # parse the selected user string to get the user id
            user_id = int(selected_user_string.split(",")[0].split(":")[1].strip())
            delete_user(user_id)
            self.users_list.values = [f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}" for user in get_users()]
            #self.display()
    
    
    # This is commented out.
    def afterEditing(self):
        ...
        #self.parentApp.setNextForm('MAIN')  # This will only be called if the form is exited without selecting a user

    def on_cancel(self):
        #self.parentApp.switchFormPrevious()
        self.parentApp.switchForm('MAIN')

    def when_exit(self, *args, **keywords):
        #self.parentApp.switchFormPrevious()
        self.parentApp.switchForm('MAIN')
        
    def on_ok(self):
        self.parentApp.switchForm('USERFORM')
    
    def on_esc(self):
        self.parentApp.switchForm('MAIN')

        
class Application(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', MainMenu, name="Main Menu")
        self.addForm('USERLIST', UserList, name="[FreeHCI User Management]")
        self.addForm('USERFORM', UserForm, name="User Form")

if __name__ == "__main__":
    App = Application().run()
