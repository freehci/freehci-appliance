# File: config/settings.py
import os
import subprocess
import requests

def read_version_number():
    # __file__ is the path to this file
    # os.path.dirname gets the directory containing this file
    # os.path.abspath makes it into an absolute path
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Now we can find .ver relative to base_dir
    version_file = os.path.join(base_dir, '..', '.ver')
    
    with open(version_file, "r") as file:
        version_number = file.read().strip()
        
    return version_number

app_version_number = read_version_number()


# Function to check for updates. This url conains the latest version number : https://raw.githubusercontent.com/freehci/freehci-appliance/main/.ver
def get_latest_version_number():
    
    # Get the latest version number from the url
    url = "https://raw.githubusercontent.com/freehci/freehci-appliance/main/.ver"
    response = requests.get(url)
    latest_version_number = response.text.strip()
    
    return latest_version_number

latest_version_number = get_latest_version_number()

# Function to update the appliance. We need to stop the server before updating the appliance, and then restart the server after the update is complete.
def update_appliance():
    # Launch the update script "update.py" as a standalone process
    # Download the update script first to the parent directory to avoid conflicts
    
    # Get the parent directory
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Jump up one directory
    top_level = os.path.join(base_dir, '..')
    
    # Download the update script to the top level directory
    url = "https://raw.githubusercontent.com/freehci/freehci-appliance/upate.py"
    subprocess.run(["wget", url, "-P", top_level])
    
    # Finaly launch the update script
    subprocess.Popen(["python", os.path.join(top_level, "update.py")])
    
def update():
    # Compare the latest version number with the current version number
    if get_latest_version_number() != app_version_number:
        # If the latest version number is different from the current version number, then download the latest version from the url
        url = "https://github.com/freehci/freehci-appliance.git"
        subprocess.run(["git", "clone", url])
        