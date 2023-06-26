import npyscreen
import requests
#import curses
import logging
import time
import docker
import json
import os
import git

# Set up logging for console app
logging.basicConfig(filename='npyscreen.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


############################################################################################################################################################################
# Functions
############################################################################################################################################################################
# User functions
def get_users():
    response = requests.get('http://localhost:8000/users/')
    return response.json()

def delete_user(user_id):
    response = requests.delete(f'http://localhost:8000/users/{user_id}')
    if response.status_code == 200:
        logging.debug(f'delete_user succeeded with response: {response.json()}')
    else:
        logging.debug(f'delete_user failed with response: {response.json()}')

def create_user(user):
    response = requests.post('http://localhost:8000/users/', json=user)
    if response.status_code == 200:
        logging.debug(f'create_user succeeded with response: {response.json()}')
    else:
        logging.debug(f'create_user failed with response: {response.json()}')

def update_user(user_id, user):
    response = requests.put(f'http://localhost:8000/users/{user_id}', json=user)
    if response.status_code == 200:
        logging.debug(f'update_user succeeded with response: {response.json()}')
    else:
        logging.debug(f'update_user failed with response: {response.json()}')

# Group functions
def get_groups():
    response = requests.get('http://localhost:8000/groups/')
    return response.json()

def delete_group(group_id):
    response = requests.delete(f'http://localhost:8000/groups/{group_id}')
    if response.status_code == 200:
        logging.debug(f'delete_group succeeded with response: {response.json()}')
    else:
        logging.debug(f'delete_group failed with response: {response.json()}')

def create_group(group):
    response = requests.post('http://localhost:8000/groups/', json=group)
    if response.status_code == 200:
        logging.debug(f'create_group succeeded with response: {response.json()}')
    else:
        logging.debug(f'create_group failed with response: {response.json()}')
        
def update_group(group_id, group):
    response = requests.put(f'http://localhost:8000/groups/{group_id}', json=group)
    if response.status_code == 200:
        logging.debug(f'update_group succeeded with response: {response.json()}')
    else:
        logging.debug(f'update_group failed with response: {response.json()}')

# Group member functions        
def get_group_members(group_id):
    response = requests.get(f'http://localhost:8000/groups/{group_id}/members/')
    return response.json()

def add_group_member(group_id, user_id, expires=None):
    response = requests.post(f'http://localhost:8000/groups/{group_id}/members/', json={"user_id": user_id})
    if response.status_code == 200:
        logging.debug(f'add_group_member succeeded with response: {response.json()}')
    else:
        logging.debug(f'add_group_member failed with response: {response.json()}')

def delete_group_member(group_id, user_id):
    response = requests.delete(f'http://localhost:8000/groups/{group_id}/members/{user_id}')
    if response.status_code == 200:
        logging.debug(f'delete_group_member succeeded with response: {response.json()}')
    else:
        logging.debug(f'delete_group_member failed with response: {response.json()}')
        
def update_group_member(group_id, user_id, expires=None):
    response = requests.put(f'http://localhost:8000/groups/{group_id}/members/{user_id}', json={"expires": expires})
    if response.status_code == 200:
        logging.debug(f'update_group_member succeeded with response: {response.json()}')
    else:
        logging.debug(f'update_group_member failed with response: {response.json()}')
        
# Equipment functions



# Log functions

############################################################################################################################################################################
# Services functions
# To control services, we need to use the docker API to start and stop containers
# We need to compose the containers using docker-compose, and then start and stop the containers using the docker API
############################################################################################################################################################################

# Compose the containers
# Redis, Postgres, Nginx, Celery, Traefik, FreeHCI, BIND, DHCP
# Allso consider using LDAP for storing users and groups.
# RADIUS and TACACS may allso be a good idea for authentication and authorization, as FreeHCI can be used for datacenter bootstraping and configuration management.
# Alternatives is FreeRADIUS and tac_plus
#
# Docker is only applicable for Linux. If running on Windows, we need to rely on external servers for Redis, Postgres, Nginx, Celery, Traefik, BIND, DHCP and DNS
# We can allso run services natively on Windows, but this require the users to install the services themselves, and is not desirable. 
# In the future we will integrate into the Windows ecosystem, and use Windows DNS and DHCP services instead of BIND and DHCP containers.Maybe we will supply a Windows installer for the services.

def compose_containers():
    client = docker.from_env()
    
    # Redis (https://hub.docker.com/_/redis)
    if get_settings()["redis_enabled"]:
        client.containers.run("redis:alpine", name="redis", detach=True, restart_policy={"Name": "always"}, ports={'6379/tcp': 6379})
    
    # Postgres (https://hub.docker.com/_/postgres)
    # Place the postgres data in a volume to avoid data loss when the container is removed
    # Location of the volume: /var/lib/docker/volumes/freehci_postgres_data/_data
    # TODO: Check config for postgres
    if get_settings()["postgres_enabled"]:
        client.containers.run("postgres:alpine", name="postgres", detach=True, restart_policy={"Name": "always"}, ports={'5432/tcp': 5432}, volumes={'freehci_postgres_data': {'bind': '/var/lib/postgresql/data', 'mode': 'rw'}})
 
    # Load balancer (Traefik or Nginx)
    # TODO: Check config for load balancer and disable if not configured so it doesn't start to avoid port conflicts   
    if get_settings()["load_balancer"] == "traefik":
        # Traefik (https://hub.docker.com/_/traefik)
        client.containers.run("traefik:alpine", name="traefik", detach=True, restart_policy={"Name": "always"}, ports={'80/tcp': 80, '443/tcp': 443, '8080/tcp': 8080})
    else:
        # Nginx (https://hub.docker.com/_/nginx)
        client.containers.run("nginx:alpine", name="nginx", detach=True, restart_policy={"Name": "always"}, ports={'80/tcp': 80, '443/tcp': 443})
     
    # Celery (https://hub.docker.com/r/celery/celery)
    if get_settings()["celery_enabled"]:       
        client.containers.run("celery/celery", name="celery", detach=True, restart_policy={"Name": "always"})
    
    # FreeHCI (https://hub.docker.com/r/freehci/freehci) - This is the main container - Not yet available on Docker Hub
    # in the meantime, build the container locally using the Dockerfile in the FreeHCI repo located at github.com/freehci/freehci
    # pull the source code from github.com/freehci/freehci and build the Dockerfile. The docker image must have python3 installed, and the FreeHCI source code must be copied to /opt/freehci
    # The Dockerfile is located in the same folder as this file. Base image is python:3.8-slim
    client.images.build(path=".", tag="freehci")
    # Start the container with the following command: docker run -p 8000:8000 -v /etc/freehci:/etc/freehci my-python-app
    client.containers.run("freehci", name="freehci", detach=True, restart_policy={"Name": "always"}, ports={'8000/tcp': 8000}, volumes={'freehci_settings': {'bind': '/etc/freehci', 'mode': 'rw'}})
    
    # To build the container later, we need to remove the old container first using the following command: docker rmi -f my-python-app
    # This will allso be done when updating the container using the built-in update function (Not yet implemented)
    
# Start a container (service) by name
def start_container(container_name):
    # Command: docker start <container_name>
    client = docker.from_env()
    client.containers.get(container_name).start()
    return get_container_status(container_name)
    
def stop_container(container_name):
    client = docker.from_env()
    client.containers.get(container_name).stop()
    return get_container_status(container_name)
    
def restart_container(container_name):
    client = docker.from_env()
    client.containers.get(container_name).restart()
    return get_container_status(container_name)
    
def get_container_status(container_name):
    client = docker.from_env()
    container = client.containers.get(container_name)
    return container.status

############################################################################################################################################################################
# Settings functions
############################################################################################################################################################################

# Here we need to read and write to the settings file
# The settings file is located in /etc/freehci/settings.json
# The settings file is a json file containing a dictionary with the following keys:
# - "hostname": The hostname of the appliance
# - "domain": The domain of the appliance
# - "ip": The IP address of the appliance
# - "netmask": The netmask of the appliance
# - "gateway": The gateway of the appliance
# - "dns": The DNS server of the appliance
# - "ntp": The NTP server of the appliance
# - "timezone": The timezone of the appliance
# - "language": The language of the appliance
# - "keyboard": The keyboard layout of the appliance
# - "password": The password of the appliance admin (hashed). Removing this key will force the user to set a new password on next login
# - "email": The email address of the appliance admin
# SNMP settings
# - "snmp_enabled": True/False
# - "snmp_community": The SNMP community string
# - "snmp_location": The SNMP location
# - "snmp_contact": The SNMP contact
# - "snmp_trap_enabled": True/False
# - "snmp_trap_server": The SNMP trap server
# - "snmp_trap_community": The SNMP trap community string
# - "snmp_trap_version": The SNMP trap version
# - "snmp_trap_port": The SNMP trap port (default 162)
# - "snmp_trap_level": The SNMP trap level (default 6)
# - "snmp_trap_interval": The SNMP trap interval (default 60)
# - "snmp_trap_retries": The SNMP trap retries (default 3)
# - "snmp_trap_timeout": The SNMP trap timeout (default 3)
# - "snmp_trap_v3_user": The SNMP trap v3 user
# - "snmp_trap_v3_auth": The SNMP trap v3 auth
# - "snmp_trap_v3_priv": The SNMP trap v3 priv
# - "snmp_trap_v3_context": The SNMP trap v3 context
# SMTP settings
# - "smtp_enabled": True/False
# - "smtp_server": The SMTP server
# - "smtp_port": The SMTP port (default 25)
# - "smtp_username": The SMTP username
# - "smtp_password": The SMTP password (Clear text)
# - "smtp_from": The SMTP from address
# - "smtp_tls": True/False
# - "smtp_ssl": True/False
# - "smtp_auth": True/False
# - "smtp_starttls": True/False
# - "smtp_timeout": The SMTP timeout (default 10)
# - "smtp_debug": True/False (default False)
# Syslog settings
# - "syslog_enabled": True/False
# - "syslog_server": The syslog server
# - "syslog_port": The syslog port (default 514)
# - "syslog_protocol": The syslog protocol (default UDP)
# - "syslog_facility": The syslog facility (default local0)
# - "syslog_level": The syslog level (default info)
# - "syslog_tag": The syslog tag (default freehci)
# - "syslog_format": The syslog format (default rfc5424)
# - "syslog_tls": True/False (default False)
# Services settings
# - "dhcp_enabled": True/False
# - "redis_enabled": True/False
# - "postgres_enabled": True/False
# - "celery_enabled": True/False
# - "bind_enabled": True/False
# TODO: Find out wich load balancer to use for the services, nginx or traefik? 
# - "load_balancer": "nginx" or "traefik" (default "traefik")
# Plugins settings
# - "plugins_enabled": True/False
# - "plugins": A list of plugins to load
# VxRail, vSphere, HorizonView, NSX-T, OpenManage, OneView, MS_SCVMM, oVirt, 

# Settings file location
# Use /etc/freehci/settings.json for Linux and C:\Program Files\FreeHCI\settings.json for Windows
# If running on Windows, the docker functionality will not be available, but the settings will be read.
if os.name == 'nt':
    # Use user profile folder for Windows
    # Make sure the service user has access to the settings file.
    settings_file = os.path.join(os.environ['USERPROFILE'], 'settings.json')
    #settings_file = 'C:\\Program Files\\FreeHCI\\settings.json'
else:
    settings_file = '/etc/freehci/settings.json'
    
def get_settings():
    with open(settings_file) as f:
        settings = json.load(f)
    return settings
    
def save_settings(settings):
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)
        
# Save syslog setting to file
def save_syslog_settings(syslog_settings):
    settings = get_settings()
    settings["syslog_enabled"] = syslog_settings["syslog_enabled"]
    settings["syslog_server"] = syslog_settings["syslog_server"]
    settings["syslog_port"] = syslog_settings["syslog_port"]
    settings["syslog_protocol"] = syslog_settings["syslog_protocol"]
    settings["syslog_facility"] = syslog_settings["syslog_facility"]
    settings["syslog_level"] = syslog_settings["syslog_level"]
    settings["syslog_tag"] = syslog_settings["syslog_tag"]
    settings["syslog_format"] = syslog_settings["syslog_format"]
    settings["syslog_tls"] = syslog_settings["syslog_tls"]
    save_settings(settings)
        
def get_hostname():
    settings = get_settings()
    return settings["hostname"]

def get_domain():
    settings = get_settings()
    return settings["domain"]

def get_ip():
    settings = get_settings()
    return settings["ip"]

def get_netmask():
    settings = get_settings()
    return settings["netmask"]



        
############################################################################################################################################################################
# Custom theme
# TODO: Remove this. It's not used
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
        self.add_handlers({"q": self.when_quit_pressed})  # Add a handler for q
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
        self.parentApp.getForm('GROUPLIST').value = None
        self.parentApp.switchForm('GROUPLIST')

    def when_equipment_pressed(self):
        npyscreen.notify_confirm("Equipment functionality not implemented yet", "Error")
        
    def when_logs_pressed(self):
        npyscreen.notify_confirm("Logs functionality not implemented yet", "Error")
        
    def when_quit_pressed(self, *args, **keywords):
        self.parentApp.switchForm(None)
        
    #def when_exit(self, *args, **keywords):
    #    self.parentApp.switchForm('MAIN')
        
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
# Groups list
############################################################################################################################################################################

class GroupList(npyscreen.ActionForm):
    def create(self):
        self.add_handlers({"q": self.when_exit})  # Add a handler for q
        self.add_handlers({"+": self.when_plus_pressed})  # Add a handler for + (plus)
        self.add_handlers({"-": self.when_minus_pressed})  # Add a handler for - (minus)
        self.add_handlers({"e": self.when_enter_pressed})  # Add a handler for - (minus)
        
        # Add group list
        logging.debug(f'GroupList.create called')
        self.groups_list = self.add(npyscreen.BoxTitle, name='Groups:', max_height=15, footer="Press enter to edit group, or 'q' to go back")
        #self.update_form()
        
        self.group_members_list = self.add(npyscreen.BoxTitle, name='Group Members:', footer="Press enter to edit group member, or 'q' to go back")
        # This triggers when the cursor is moved
        self.groups_list.entry_widget.when_cursor_moved = self.when_cursor_moved
        self.groups_list.entry_widget.when_value_edited = self.when_enter_pressed
       
    def update_group_members_list(self, group_id):
        members = get_group_members(group_id)
        member_strings = []
        for member in members:
            if member['member_type'] == 'user':
                user = member['user']
                member_strings.append(f"User ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")
            elif member['member_type'] == 'group':
                group = member['member_group']
                member_strings.append(f"Group ID: {group['id']}, Group Name: {group['name']}, Group Email: {group['email']}")
        self.group_members_list.values = member_strings
        self.group_members_list.display()
    
    # Reset the group members list when the cursor is moved, and only show the groups members list when pressing enter to avoid performance issues 
    # (Lagg when scrolling through the list)
    def when_cursor_moved(self, *args, **keywords):
        self.group_members_list.values = None
        self.group_members_list.display()

    # TODO: 
    # Consder moving loading of group members to "when_enter_pressed" instead of "when_cursor_moved"
    # as loading the group members list when the cursor is moved is not very efficient. Anoing delays when scrolling through the list.
    # NOTE: This is now implemented, but we have some issues if we try to show the group members in a group again, as the selection is not changed before selecting another group.
    def when_enter_pressed(self, *args, **keywords): 
        logging.debug(f'when_cursor_moved called with args: {args} and keywords: {keywords}')
        logging.debug(f'when_cursor_moved called with value: {self.groups_list.entry_widget.value}') 
        selected_group_string = self.groups_list.values[self.groups_list.entry_widget.cursor_line]
        group_id = int(selected_group_string.split(",")[0].split(":")[1].strip())
        group_name = str(selected_group_string.split(",")[1].split(":")[1].strip())
        logging.debug(f'Selected group: ID: {group_id} Name: {group_name}')
        
        if group_id is not None:
            selected_group_string = self.groups_list.values[self.groups_list.entry_widget.cursor_line]
            #group_id = int(selected_group_string.split(",")[0].split(":")[1].strip())
            logging.debug(f'Selected group: {group_id}') 
            npyscreen.notify("Loading group members...", title="Please Wait")
            self.update_group_members_list(group_id)
            
    
    # Update the group list
    def update_form(self):
        npyscreen.notify("Loading group info...", title="Please Wait")
        self.groups_list.values = [f"ID: {group['id']}, Name: {group['name']}" for group in get_groups()]
        logging.debug(f'GroupList.update_form called', self.groups_list.values)
        self.display()
        
    # Key bindings    
    def when_plus_pressed(self, *args, **keywords):
        logging.debug(f'when_plus_pressed called with args: {args} and keywords: {keywords}')
        
    def when_minus_pressed(self, *args, **keywords):
        logging.debug(f'when_minus_pressed called with args: {args} and keywords: {keywords}')
        
    def when_exit(self, *args, **keywords):
        self.parentApp.switchForm('MAIN')
        
    def on_cancel(self):
        self.parentApp.switchForm('MAIN')
        
    def on_ok(self):
        self.parentApp.switchForm('GROUPFORM')
        
    def on_esc(self):
        self.parentApp.switchForm('MAIN')
    
    def beforeEditing(self):
        self.update_form()
        self.when_enter_pressed() # This is a hack to trigger the when_cursor_moved function when the form is loaded. Otherwise the group members list is not updated.
        
    def afterEditing(self):
        self.parentApp.setNextForm('MAIN')
        
    

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
        #self.update_form()
        
        
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

    # Navigate down in the help text
    # BUG: This doesn't work properly. Getting index out of range error when pressing 'd' to scroll down.
    def when_d_pressed(self, *args, **keywords):
        logging.debug(f'when_d_pressed called with args: {args} and keywords: {keywords}')
        logging.debug(f'when_d_pressed, entry_widget len: {len(self.help_text.entry_widget.values)}')
        current_line = self.help_text.entry_widget.cursor_line
        logging.debug(f'when_d_pressed, current_line: {current_line}')
        
        height = self.help_text.entry_widget.height
        logging.debug(f'when_d_pressed, height: {height}')
        if current_line + height < len(self.help_text.entry_widget.values):
            new_line = self.help_text.entry_widget.cursor_line + height
            logging.debug(f'when_d_pressed, new cursor_line: {new_line}')
            #self.help_text.entry_widget.cursor_line += height
        else:
            self.help_text.entry_widget.cursor_line = len(self.help_text.entry_widget.values) - 1
        self.help_text.entry_widget.display()
        
    # Update the user list    
    def update_form(self):
        npyscreen.notify("Loading users list...", title="Please Wait")
        self.users_list.values = [f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}" for user in get_users()]
        self.display()

    # this should be triggered when user presses enter on a user in the list               
    def when_enter_pressed(self, *args, **keywords):
        logging.debug(f'when_enter_pressed called with args: {args} and keywords: {keywords}')
        logging.debug(f'when_enter_pressed called with value: {self.users_list.entry_widget.value}') 
        if self.users_list.entry_widget.value is not None and self.users_list.entry_widget.value < len(self.users_list.values):
            npyscreen.notify("Loading user info...", title="Please Wait")
            selected_user = get_users()[self.users_list.entry_widget.value]
            logging.debug(f'Selected user: {selected_user}') 
            
            self.parentApp.getForm('USERFORM').setup(selected_user)
            self.parentApp.switchForm('USERFORM') 
            self.editing = False
            
        #else:
        #    npyscreen.notify_confirm("No user selected", "Error")

    # Update help text when resizing the form
    # BUG: This doesn't work properly. The help text is not updated when the form is resized, and cancel and ok buttons are stuck at the same position.
    def resize(self):
        logging.debug(f'resize called')
        logging.debug(f'resize, entry_widget len: {self.help_text.entry_widget.height}')
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
        self.help_text._resize()
        self.help_text.entry_widget.display()
        self.help_text.update()
        self.help_text.display()
        self.display()
    
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
    
    def beforeEditing(self):
        
        self.update_form()

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
        self.addForm('GROUPLIST', GroupList, name="Group List")
        self.addForm('PASSWDFORM', PasswordChangeForm, name="Change Password")  # Add this line


if __name__ == "__main__":
    App = Application().run()
