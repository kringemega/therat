import subprocess
import os

def open_new_command_prompt():
    try:
        # Check the operating system
        if os.name == 'nt':  # For Windows
            subprocess.Popen(['start', 'cmd', '/k', 'title', 'New Command Prompt'], shell=True)
        elif os.name == 'posix':  # For Unix/Linux/MacOS
            subprocess.Popen(['xterm'])  # You can change this to your preferred terminal emulator
        else:
            return "Unsupported operating system"
    except Exception as e:
        return f"Error: {str(e)}"
    return "New command prompt opened successfully"

if __name__ == "__main__":
    open_new_command_prompt()