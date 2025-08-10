import subprocess
import os
import sys
import shutil

def run_file(file_path):
    try:
        file_path = file_path.strip('"')
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
        subprocess.Popen([file_path])
        return f"File {file_path} started successfully"
    except Exception as e:
        return f"Error starting file: {str(e)}"

def install_file(file_path):
    try:
        file_path = file_path.strip('"')
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
        target_directory = os.path.join("C:\\", "FRAT")
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        shutil.copy(file_path, target_directory)
        return f"File {file_path} copied to C:\\FRAT successfully"
    except Exception as e:
        return f"Error copying file: {str(e)}"

def list_directory(directory):
    try:
        if not directory:
            directory = os.path.expanduser("~\\Desktop")
        files_and_dirs = []
        for root, dirs, files in os.walk(directory):
            for name in files:
                files_and_dirs.append(os.path.relpath(os.path.join(root, name), directory))
            for name in dirs:
                files_and_dirs.append(os.path.relpath(os.path.join(root, name), directory))
            break
        return "\n".join(files_and_dirs)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def open_remote_file(filepath):
    """Открытие файла через стандартные средства ОС"""
    try:
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        if sys.platform == "win32":
            os.startfile(filepath)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filepath])
        return f"File {filepath} opened successfully"
    except Exception as e:
        return f"Error opening file: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: extool <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "run":
        if len(sys.argv) < 3:
            print("Usage: extool run <file_path>")
            sys.exit(1)
        file_path = sys.argv[2]
        print(run_file(file_path))

    elif command == "install":
        if len(sys.argv) < 3:
            print("Usage: extool install <file_path>")
            sys.exit(1)
        file_path = sys.argv[2]
        print(install_file(file_path))

    elif command == "ls":
        if len(sys.argv) > 2:
            directory = sys.argv[2]
        else:
            directory = ""
        print(list_directory(directory))

    elif command == "open":
        if len(sys.argv) < 3:
            print("Usage: extool open <file_path>")
            sys.exit(1)
        file_path = sys.argv[2]
        print(open_remote_file(file_path))

    else:
        print("Unknown command")
        sys.exit(1)

if __name__ == "__main__":
    main()