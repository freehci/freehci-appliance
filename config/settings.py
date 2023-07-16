# File: config/settings.py
import os

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
