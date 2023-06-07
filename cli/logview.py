import time
import os

def tail(filename, n=10):
    '''
    Print the last `n` lines from the file with name `filename`
    '''
    with open(filename, 'r') as file:
        lines = file.readlines()
        last_lines = lines[-n:]
        for line in last_lines:
            print(line, end='')

def tail_follow(filename):
    '''
    Continuously monitor the file with name `filename` and
    print new lines as they are written to the file.
    '''
    with open(filename, 'r') as file:
        # Move to the end of the file
        file.seek(0, os.SEEK_END)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)    # Sleep briefly
                continue
            print(line, end='')

# Example usage:
# tail('my_file.txt')
tail_follow('npyscreen.log')
