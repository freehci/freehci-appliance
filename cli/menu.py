import npyscreen
import requests
import curses
import logging

# Set up logging
logging.basicConfig(filename='npyscreen.log', level=logging.DEBUG)

############################################################################################################################################################################
# Functions
############################################################################################################################################################################
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
        
        
############################################################################################################################################################################
# Custom theme
############################################################################################################################################################################        
class CustomTheme(npyscreen.ThemeManager):
    default_colors = {
        'DEFAULT': 'WHITE_BLACK',
        'FORMDEFAULT': 'WHITE_BLACK',
        'NO_EDIT': 'BLUE_BLACK',
        'STANDOUT': 'CYAN_BLACK',
        'CURSOR': 'BLACK_WHITE',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL': 'GREEN_BLACK',
        'LABELBOLD': 'GREEN_BLACK',
        'CONTROL': 'YELLOW_BLACK',
        'IMPORTANT': 'GREEN_BLACK',
        'SAFE': 'GREEN_BLACK',
        'WARNING': 'RED_BLACK',
        'DANGER': 'RED_BLACK',
        'CRITICAL': 'BLACK_RED',
        'GOOD': 'GREEN_BLACK',
        'GOODHL': 'GREEN_BLACK',
        'VERYGOOD': 'BLACK_GREEN',
        'CAUTION': 'YELLOW_BLACK',
        'CAUTIONHL': 'BLACK_YELLOW',
    }

############################################################################################################################################################################
# Main menu
############################################################################################################################################################################
class MainMenu(npyscreen.ActionForm):
    
    def create(self):
        self.add(npyscreen.TitleText, name='Welcome to FreeHCI!', editable=False)
        
        self.add(npyscreen.ButtonPress, name='Appliance', when_pressed_function=self.when_appliance_pressed)
        self.add(npyscreen.ButtonPress, name='Users', when_pressed_function=self.when_users_pressed)
        self.add(npyscreen.ButtonPress, name='Groups', when_pressed_function=self.when_groups_pressed)
        self.add(npyscreen.ButtonPress, name='Equipment', when_pressed_function=self.when_equipment_pressed)
        self.add(npyscreen.ButtonPress, name='Logs', when_pressed_function=self.when_logs_pressed)
        self.add(npyscreen.ButtonPress, name='Quit', when_pressed_function=self.when_quit_pressed)
        

        # Add services overview using checkboxes
        self.add(npyscreen.TitleText, name='Services:', editable=False, rely=2, relx=25)
        self.add(npyscreen.CheckBox, name='DHCP', value=True, editable=False, rely=3, relx=25)
        self.add(npyscreen.CheckBox, name='DNS', value=True, editable=False, rely=4, relx=25)
        # Redis
        self.add(npyscreen.CheckBox, name='Redis', value=True, editable=False, rely=5, relx=25)
        # Docker
        self.add(npyscreen.CheckBox, name='Docker', value=True, editable=False, rely=6, relx=25)
        # Nginx
        self.add(npyscreen.CheckBox, name='Nginx', value=True, editable=False, rely=7, relx=25)
        # Postgres
        self.add(npyscreen.CheckBox, name='Postgres', value=True, editable=False, rely=8, relx=25)
        # Celery
        self.add(npyscreen.CheckBox, name='Celery', value=True, editable=False, rely=9, relx=25)
        

    def when_appliance_pressed(self):
        npyscreen.notify_confirm("Appliance functionality not implemented yet", "Error")
    
    def when_users_pressed(self):
        self.parentApp.getForm('USERLIST').value = None
        self.parentApp.switchForm('USERLIST')

    def when_groups_pressed(self):
        npyscreen.notify_confirm("Groups functionality not implemented yet", "Error")

    def when_equipment_pressed(self):
        npyscreen.notify_confirm("Equipment functionality not implemented yet", "Error")
        
    def when_logs_pressed(self):
        npyscreen.notify_confirm("Logs functionality not implemented yet", "Error")
        
    def when_quit_pressed(self):
        self.parentApp.switchForm(None)
        
    def on_cancel(self):
        self.parentApp.switchForm(None)
        
    def afterEditing(self):
        pass
    
    
############################################################################################################################################################################
# Dialog - Just a test
############################################################################################################################################################################
class Dialog(npyscreen.NPSApp):
    def main(self):
        F = npyscreen.Form(name = "Welcome to Npyscreen",)
        t = F.add(npyscreen.BoxBasic, name = "Basic Box:", max_width=30, relx=2, max_height=3)
        t.footer = "This is a footer"

        t1 = F.add(npyscreen.BoxBasic, name = "Basic Box:", rely=2, relx=32,
        max_width=30, max_height=3)


        t2 = F.add(npyscreen.BoxTitle, name="Box Title:", footer="This is a footer", max_height=8)
        t2.entry_widget.scroll_exit = True
        t2.values = [
            "Hello",
            "This is a Test",
            "This is another test",
            "And here is another line",
            "And here is another line, which is really very long.abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz",
            "And one more."
            ]

        F.edit()

############################################################################################################################################################################
# User form
############################################################################################################################################################################

class UserForm(npyscreen.ActionForm):
    def create(self):
        self.add(npyscreen.TitleText, name='User Details:', editable=False)
        self.id = self.add(npyscreen.TitleText, name='ID:', editable=False)
        self.username = self.add(npyscreen.TitleText, name='Username:', editable=True)
        self.email = self.add(npyscreen.TitleText, name='Email:', editable=True)
        self.expires = self.add(npyscreen.TitleDateCombo, name = "Expires:")
        self.active = self.add(npyscreen.CheckBox, name='Active:', editable=True, relx=40, rely=3)
        self.delete_button = self.add(npyscreen.ButtonPress, name='Delete User', relx=2, rely=20 )
        
    def setup(self, user):
        logging.debug(f'UserForm.setup called with user: {user}')
        self.username.value = f'{user["username"]}'
        self.email.value = f'{user["email"]}'
        self.id.value = f'{user["id"]}'
        self.expires.value = None
        self.delete_button.when_pressed_function = lambda: delete_user(user["id"])
        self.display()

    def afterEditing(self):
        self.parentApp.setNextForm('USERLIST')
        self.parentApp.getForm('USERLIST').update_form()
        
    def beforeEditing(self):
        if hasattr(self, 'selected_user'):
            self.setup(self.selected_user)
    
    # Update user details / create new user
    def on_ok(self):
        if self.username.value == "" or self.email.value == "":
            npyscreen.notify_confirm("Username and email must be set", "Error")
            
        else:    
            
            if self.id.value == "":
                # Create new user
                user = {
                    "username": self.username.value,
                    "email": self.email.value,
                    "password": ""
                    #"active": self.active.value,
                    #"expires": self.expires.value,
                }
                create_user(user)
            else:    
                user = {
                    "id": self.id.value,
                    "username": self.username.value,
                    "email": self.email.value,
                    #"active": self.active.value,
                    #"expires": self.expires.value,
                }
                update_user(user["id"], user)
            self.parentApp.switchFormPrevious()
        

############################################################################################################################################################################
# Password change form
############################################################################################################################################################################

class PasswordChangeForm(npyscreen.ActionForm):
    def create(self):
        
        self.title = self.add(npyscreen.TitleText, name='Change password for user:                               ', editable=False) # Initial placeholder (Must be long enough to cover the longest username)
        
        #self.password_field = self.add(npyscreen.TitlePassword, name=' ', begin_entry_at=30, editable=False)  # Initial empty name
        
        self.user = None  # Placeholder for the user data
        
        self.password = self.add(npyscreen.TitlePassword, name="New Password:", begin_entry_at=20)
        self.confirm_password = self.add(npyscreen.TitlePassword, name="Confirm Password:", begin_entry_at=20)
        
    def setup(self, user_name):
        logging.debug(f'PasswordChangeForm.setup called with user: {user_name}')
        
        self.title.label_widget.value = f'Change password for user: {user_name}'
        
        self.user = user_name
        self.password.value = ""
        self.confirm_password.value = ""
        
        self.title.display()
        self.display()
        
    def afterEditing(self):
        self.parentApp.setNextForm('USERLIST')
        
    def beforeEditing(self):
        if hasattr(self, 'user_name'):
            self.setup(self.user_name)

    def on_ok(self):
        if self.password.value != self.confirm_password.value:
            npyscreen.notify_confirm("Passwords do not match", "Error")
            # TODO: Find a way to cancel the form submission and return to the form
        else:
            # Call your password change function here, using self.user to identify the user
            # For example: change_password(self.user, self.password.value)
            self.parentApp.switchFormPrevious()

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

############################################################################################################################################################################
# User list
############################################################################################################################################################################

class UserList(npyscreen.ActionForm):
    def create(self):
        self.add_handlers({"q": self.when_exit})  # Add a handler for q
        self.add_handlers({"+": self.when_plus_pressed})  # Add a handler for + (plus)
        self.add_handlers({"-": self.when_minus_pressed})  # Add a handler for - (minus)
        self.add_handlers({"r": self.when_r_pressed})  # Add a handler for r (change password) 
        
        #self.add(npyscreen.TitleText, name="[Press 'q' to go back]", editable=False) # Do we need this?
        
        # Add user list
        # TODO: Use another widget for the list, so that we can have headers and a more table-like layout
        self.users_list = self.add(npyscreen.BoxTitle, name='Users:', max_height=15, footer="Press enter to edit user, or 'q' to go back")
        #self.users_list.entry_widget.color = 'VERYGOOD' # Testing some colors
        self.update_form()
        
        
        # Add help text
        self.help_text = self.add(npyscreen.BoxTitle, 
                                  name='Help:', 
                                  value='This is some help text.', 
                                  scroll_exit=True, 
                                  editable=False, 
                                  footer=f"Press 'u' and 'd' to scroll through the list"
                                  )
        self.help_text.values = [
            f"Navigation:                                    Editing and Viewing:",
            f"Use the arrow keys to navigate the list.       Press Enter or Space to edit a user.",
            f"Use Tab to move between fields and groups.     Press 'r' to change a user's password.",
            "",
            f"Creating and Deleting Users:                   Exiting:",
            f"Press '+' to create a new user.                Press 'q' to go back or exit.",
            f"Press '-' to delete a user.",
            f"More lines of help text.",
            f"And even more lines of help text.",
            f"And more...."
            ]
        # Add keypress handlers for help text
        self.add_handlers({"u": self.when_u_pressed})  # Add a handler for h (Up)
        self.add_handlers({"d": self.when_d_pressed})  # Add a handler for j (Down)
            
        # This causes the function to be called twice on first keypress, and then works as expected
        # Log output:
        # DEBUG:root:when_enter_pressed called with value: None
        # DEBUG:root:when_enter_pressed called with value: None        
        self.users_list.entry_widget.when_value_edited = self.when_enter_pressed
        
        # This triggers when the cursor is moved
        #self.users_list.entry_widget.when_cursor_moved = self.when_cursor_moved
    
    def when_u_pressed(self, *args, **keywords):
        logging.debug(f'when_u_pressed called with args: {args} and keywords: {keywords}')
        current_line = self.help_text.entry_widget.cursor_line
        height = self.help_text.entry_widget.height
        if current_line - height >= 0:
            self.help_text.entry_widget.cursor_line -= height
        else:
            self.help_text.entry_widget.cursor_line = 0
        self.help_text.entry_widget.display()

    def when_d_pressed(self, *args, **keywords):
        logging.debug(f'when_d_pressed called with args: {args} and keywords: {keywords}')
        current_line = self.help_text.entry_widget.cursor_line
        height = self.help_text.entry_widget.height
        if current_line + height < len(self.help_text.entry_widget.values):
            self.help_text.entry_widget.cursor_line += height
        else:
            self.help_text.entry_widget.cursor_line = len(self.help_text.entry_widget.values) - 1
        self.help_text.entry_widget.display()
        
    # Update the user list    
    def update_form(self):
        self.users_list.values = [f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}" for user in get_users()]
        self.display()

    # this should be triggered when user presses enter on a user in the list               
    def when_enter_pressed(self, *args, **keywords):
        logging.debug(f'when_enter_pressed called with args: {args} and keywords: {keywords}')
        logging.debug(f'when_enter_pressed called with value: {self.users_list.entry_widget.value}') 
        if self.users_list.entry_widget.value is not None and self.users_list.entry_widget.value < len(self.users_list.values):
            npyscreen.notify_wait("Loading user info...", title="Please Wait")
            selected_user = get_users()[self.users_list.entry_widget.value]
            logging.debug(f'Selected user: {selected_user}') 
            
            self.parentApp.getForm('USERFORM').setup(selected_user)
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
        
        selected_user_string = self.users_list.values[self.users_list.entry_widget.cursor_line]
        user_id = int(selected_user_string.split(",")[0].split(":")[1].strip())
        user_name = str(selected_user_string.split(",")[1].split(":")[1].strip())
        title = f"Delete user {user_name}"
        
        if (npyscreen.notify_yes_no("Are you sure you want to delete this user?", title)):
        
            logging.debug(f'when_minus_pressed called with value: {self.users_list.values[self.users_list.entry_widget.cursor_line]}')
            
            #if self.users_list.entry_widget.value is not None and self.users_list.entry_widget.value < len(self.users_list.values):
            
            
            logging.debug(f'Selected user: {selected_user_string}') 
            # parse the selected user string to get the user id
            
            delete_user(user_id)
            self.users_list.values = [f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}" for user in get_users()]
            #self.display()
    
    # Change password
    def when_r_pressed(self, *args, **keywords):
        selected_user_string = self.users_list.values[self.users_list.entry_widget.cursor_line]
        user_id = int(selected_user_string.split(",")[0].split(":")[1].strip())
        user_name = str(selected_user_string.split(",")[1].split(":")[1].strip())
        
        #selected_user = get_users()[self.users_list.values[self.users_list.entry_widget.cursor_line]]
        
        logging.debug(f'Selected user for password change: {user_name}')
        
        self.parentApp.getForm('PASSWDFORM').user_name = user_name
        self.parentApp.getForm('PASSWDFORM').setup(user_name)
        
        #self.parentApp.getForm('PASSWDFORM').user_name = user_name
        self.parentApp.switchForm('PASSWDFORM')
        self.editing = False
    
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
        
    
############################################################################################################################################################################
# Main application
############################################################################################################################################################################
        
class Application(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(CustomTheme)
        self.addForm('MAIN', MainMenu, name="Main Menu")
        self.addForm('USERLIST', UserList, name="[FreeHCI User Management]")
        self.addForm('USERFORM', UserForm, name="User Form")
        self.addForm('PASSWDFORM', PasswordChangeForm, name="Change Password")  # Add this line

if __name__ == "__main__":
    App = Application().run()
