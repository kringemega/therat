import subprocess
import os
import sys
import shutil

def run_file(file_path):
    try:
        # Удаление кавычек из пути
        file_path = file_path.strip('"')
        subprocess.Popen([file_path])
        return f"File {file_path} started successfully"
    except Exception as e:
        return f"Error starting file: {str(e)}"

def install_file(file_path):
    try:
        # Удаление кавычек из пути
        file_path = file_path.strip('"')
        target_directory = os.path.expanduser("~\\Documents")
        shutil.copy(file_path, target_directory)
        return f"File {file_path} copied to Documents successfully"
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
            break  # Останавливаемся после первого уровня вложенности
        return "\n".join(files_and_dirs)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

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

    else:
        print("Unknown command")
        sys.exit(1)

if __name__ == "__main__":
    main()